from __future__ import annotations

from dataclasses import dataclass, field

from stock_up.models import DailyBar, LimitUpStock, Quote


@dataclass
class MockProvider:
    quotes: dict[str, Quote] = field(default_factory=dict)
    daily_bars: dict[str, list[DailyBar]] = field(default_factory=dict)
    limit_up_pool: list[LimitUpStock] = field(default_factory=list)
    trade_calendar: list[str] = field(default_factory=list)

    def get_realtime_quotes(self, codes: list[str]) -> list[Quote]:
        return [self.quotes[c] for c in codes if c in self.quotes]

    def get_daily_bars(self, code: str, days: int) -> list[DailyBar]:
        return self.daily_bars.get(code, [])[-days:]

    def get_limit_up_pool(self, trade_date: str) -> list[LimitUpStock]:
        return [item for item in self.limit_up_pool if item.trade_date == trade_date]

    def get_trade_calendar(self) -> list[str]:
        return self.trade_calendar
