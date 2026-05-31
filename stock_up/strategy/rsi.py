from __future__ import annotations


def calculate_rsi_series(closes: list[float], period: int) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(closes) < 2:
        return [None] * len(closes)

    rsis: list[float | None] = [None] * len(closes)
    gains: list[float] = []
    losses: list[float] = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

        if i < period:
            continue

        window_gains = gains[i - period:i]
        window_losses = losses[i - period:i]
        avg_gain = sum(window_gains) / period
        avg_loss = sum(window_losses) / period

        if avg_loss == 0:
            rsis[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsis[i] = round(100 - (100 / (1 + rs)), 4)

    return rsis


def crossed_above(prev_short: float | None, prev_long: float | None, curr_short: float | None, curr_long: float | None) -> bool:
    if None in (prev_short, prev_long, curr_short, curr_long):
        return False
    return prev_short <= prev_long and curr_short > curr_long


def crossed_below(prev_short: float | None, prev_long: float | None, curr_short: float | None, curr_long: float | None) -> bool:
    if None in (prev_short, prev_long, curr_short, curr_long):
        return False
    return prev_short >= prev_long and curr_short < curr_long
