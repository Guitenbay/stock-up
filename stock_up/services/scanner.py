from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stock_up.market.base import MarketDataProvider
from stock_up.models import LimitUpStock, WatchItem
from stock_up.repositories import WatchRepository
from stock_up.services.initial_low import InitialLowMode, choose_initial_low


@dataclass(frozen=True)
class ScanSummary:
    total_count: int = 0
    added_count: int = 0
    skipped_count: int = 0


@dataclass(frozen=True)
class LimitUpFilter:
    exclude_st: bool = True
    exclude_bj: bool = True
    min_amount: float = 500_000_000


def run_limit_up_scan(
    db_path: Path,
    provider: MarketDataProvider,
    trade_date: str,
    filters: LimitUpFilter | None = None,
    initial_low_mode: InitialLowMode = "same_day",
) -> ScanSummary:
    filters = filters or LimitUpFilter()
    pool = provider.get_limit_up_pool(trade_date)
    repo = WatchRepository(db_path)
    added = 0
    skipped = 0

    for stock in pool:
        if not _passes(stock, filters):
            skipped += 1
            continue
        recent_bars = provider.get_daily_bars(stock.code, 1) if initial_low_mode == "recent_1d" else []
        repo.upsert(WatchItem(
            code=stock.code,
            name=stock.name,
            reason=stock.reason or "涨停池",
            high=stock.high,
            low=choose_initial_low(stock, recent_bars, initial_low_mode),
            now=stock.close,
            status="watching",
        ))
        added += 1

    return ScanSummary(total_count=len(pool), added_count=added, skipped_count=skipped)


def _passes(stock: LimitUpStock, filters: LimitUpFilter) -> bool:
    name = stock.name or ""
    code = stock.code or ""
    if filters.exclude_st and ("ST" in name.upper() or "*ST" in name.upper()):
        return False
    if filters.exclude_bj and (code.startswith("8") or code.startswith("4") or code.startswith("bj")):
        return False
    if stock.amount < filters.min_amount:
        return False
    return True
