from __future__ import annotations

from typing import Literal

from stock_up.models import DailyBar, LimitUpStock


InitialLowMode = Literal["same_day", "recent_1d"]


def choose_initial_low(stock: LimitUpStock, recent_bars: list[DailyBar], mode: InitialLowMode = "same_day") -> float:
    if mode == "recent_1d" and recent_bars:
        return recent_bars[-1].low
    return stock.low
