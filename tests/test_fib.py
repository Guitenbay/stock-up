from stock_up.strategy.fib import calculate_fib_levels


def test_calculate_fib_levels():
    levels = calculate_fib_levels(high=20, low=10)
    assert levels.f382 == 16.18
    assert levels.f618 == 13.82
    assert levels.f786 == 12.14
