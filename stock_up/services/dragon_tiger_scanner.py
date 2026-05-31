from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stock_up.codes import format_code
from stock_up.market.base import MarketDataProvider
from stock_up.models import WatchItem
from stock_up.repositories import WatchRepository


@dataclass(frozen=True)
class DragonTigerScanSummary:
    total_count: int = 0
    added_count: int = 0


def run_dragon_tiger_scan(db_path: Path, provider: MarketDataProvider, trade_date: str) -> DragonTigerScanSummary:
    rows = provider.get_dragon_tiger(trade_date)  # type: ignore[attr-defined]
    repo = WatchRepository(db_path)
    codes = [format_code(row.code) or row.code for row in rows]
    quote_map = {q.code: q for q in provider.get_realtime_quotes(codes)}
    added = 0

    for row, full_code in zip(rows, codes):
        quote = quote_map.get(full_code)
        repo.upsert(WatchItem(
            code=full_code,
            name=row.name,
            reason=f"龙虎榜: {row.reason}",
            high=quote.high if quote else row.close,
            low=quote.low if quote else row.close,
            avg=quote.avg if quote else 0.0,
            now=quote.now if quote else row.close,
            status="watching",
        ))
        added += 1

    return DragonTigerScanSummary(total_count=len(rows), added_count=added)
