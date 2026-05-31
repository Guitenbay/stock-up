from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stock_up.market.base import MarketDataProvider
from stock_up.repositories import HoldingRepository, WatchRepository
from stock_up.strategy.fib import calculate_fib_levels


@dataclass(frozen=True)
class TickSummary:
    updated_watch_count: int = 0
    updated_holding_count: int = 0


def run_tick(db_path: Path, provider: MarketDataProvider) -> TickSummary:
    watch_repo = WatchRepository(db_path)
    holding_repo = HoldingRepository(db_path)

    watch_items = watch_repo.list_active()
    holdings = holding_repo.list_open()
    codes = sorted({item.code for item in watch_items} | {h.code for h in holdings})
    quote_map = {q.code: q for q in provider.get_realtime_quotes(codes)}

    updated_watch = 0
    for item in watch_items:
        quote = quote_map.get(item.code)
        if not quote:
            continue
        item.name = quote.name or item.name
        item.now = quote.now
        item.avg = quote.avg or item.avg
        if quote.now > item.high:
            item.high = quote.now
        levels = calculate_fib_levels(item.high, item.low)
        # persist current levels through raw update fields supported by table
        watch_repo.upsert(item)
        _update_watch_levels(db_path, item.code, levels.f382, levels.f618, levels.f786)
        updated_watch += 1

    updated_holdings = 0
    for holding in holdings:
        quote = quote_map.get(holding.code)
        if not quote:
            continue
        holding.name = quote.name or holding.name
        holding.now = quote.now
        holding.highest = max(holding.highest, quote.now, quote.high)
        if quote.now > holding.high:
            holding.high = quote.now
        holding_repo.upsert(holding)
        updated_holdings += 1

    return TickSummary(updated_watch_count=updated_watch, updated_holding_count=updated_holdings)


def _update_watch_levels(db_path: Path, code: str, f382: float, f618: float, f786: float) -> None:
    from stock_up.db import connect

    with connect(db_path) as conn:
        conn.execute(
            "UPDATE watchlist SET f382=?, f618=?, f786=? WHERE code=?",
            (f382, f618, f786, code),
        )
        conn.commit()
