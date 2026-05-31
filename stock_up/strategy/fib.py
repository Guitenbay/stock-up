from stock_up.models import FibLevels


def calculate_fib_levels(high: float, low: float) -> FibLevels:
    diff = high - low
    return FibLevels(
        f382=round(high - diff * 0.382, 3),
        f618=round(high - diff * 0.618, 3),
        f786=round(high - diff * 0.786, 3),
    )
