from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stock_up.codes import format_code
from stock_up.market.base import MarketDataProvider
from stock_up.models import WatchItem
from stock_up.repositories import WatchRepository


@dataclass(frozen=True)
class HotLeaderScanSummary:
    board_count: int = 0
    leader_count: int = 0
    added_count: int = 0


def run_hot_leader_scan(
    db_path: Path,
    provider: MarketDataProvider,
    trade_date: str,
    max_boards: int = 10,
) -> HotLeaderScanSummary:
    boards = provider.get_hot_boards(trade_date)[:max_boards]
    repo = WatchRepository(db_path)
    added = 0
    leader_count = 0

    for board in boards:
        leaders = provider.get_hot_leaders(trade_date, board.plate_id or board.bk_code)
        leader_count += len(leaders)
        codes = [format_code(leader.code) or leader.code for leader in leaders]
        quote_map = {q.code: q for q in provider.get_realtime_quotes(codes)}
        for leader, full_code in zip(leaders, codes):
            quote = quote_map.get(full_code)
            high, low = _valid_quote_range(quote)
            repo.upsert(WatchItem(
                code=full_code,
                name=leader.name,
                reason=f"热点板块龙头: {board.bk_name} / {leader.board_name}",
                high=high,
                low=low,
                avg=quote.avg if quote else 0.0,
                now=quote.now if quote else 0.0,
                status="watching",
            ))
            added += 1

    return HotLeaderScanSummary(board_count=len(boards), leader_count=leader_count, added_count=added)


def _valid_quote_range(quote) -> tuple[float, float]:
    if quote and quote.high > 0 and quote.low > 0:
        return quote.high, quote.low
    return 0.0, 0.0
