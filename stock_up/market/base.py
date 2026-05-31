from __future__ import annotations

from typing import Protocol

from stock_up.models import DailyBar, LimitUpStock, Quote


class MarketDataProvider(Protocol):
    def get_realtime_quotes(self, codes: list[str]) -> list[Quote]:
        ...

    def get_daily_bars(self, code: str, days: int) -> list[DailyBar]:
        ...

    def get_limit_up_pool(self, trade_date: str) -> list[LimitUpStock]:
        ...

    def get_trade_calendar(self) -> list[str]:
        ...
