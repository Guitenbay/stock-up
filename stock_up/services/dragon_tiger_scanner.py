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
    by_code = {}
    for row in rows:
        full_code = format_code(row.code) or row.code
        if full_code in by_code:
            data = by_code[full_code]
            if row.reason and row.reason not in data["reasons"]:
                data["reasons"].append(row.reason)
            data["close"] = row.close or data["close"]
            continue
        by_code[full_code] = {"row": row, "reasons": [row.reason] if row.reason else [], "close": row.close}

    codes = list(by_code.keys())
    quote_map = {q.code: q for q in provider.get_realtime_quotes(codes)}
    added = 0

    for full_code, data in by_code.items():
        row = data["row"]
        close = data["close"]
        reason = "；".join(data["reasons"])
        quote = quote_map.get(full_code)
        high, low = _quote_range_or_close(quote, close)
        repo.upsert(WatchItem(
            code=full_code,
            name=row.name,
            reason=f"龙虎榜: {reason}",
            high=high,
            low=low,
            avg=quote.avg if quote else 0.0,
            now=quote.now if quote else close,
            status="watching",
        ))
        added += 1

    return DragonTigerScanSummary(total_count=len(rows), added_count=added)


def _quote_range_or_close(quote, close: float) -> tuple[float, float]:
    if quote and quote.high > 0 and quote.low > 0:
        return quote.high, quote.low
    return close, close
