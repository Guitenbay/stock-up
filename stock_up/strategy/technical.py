from __future__ import annotations

from typing import Literal

from stock_up.strategy.rsi import crossed_above, crossed_below


def detect_rsi_cross(
    prev_short: float | None,
    prev_long: float | None,
    curr_short: float | None,
    curr_long: float | None,
) -> Literal["golden", "dead"] | None:
    if crossed_above(prev_short, prev_long, curr_short, curr_long):
        return "golden"
    if crossed_below(prev_short, prev_long, curr_short, curr_long):
        return "dead"
    return None
