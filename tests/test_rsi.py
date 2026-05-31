from stock_up.strategy.rsi import calculate_rsi_series, crossed_above, crossed_below


def test_rsi_series_returns_values_after_period():
    closes = [10, 11, 12, 11, 13, 14, 13, 15, 16, 17]
    rsi = calculate_rsi_series(closes, period=3)
    assert len(rsi) == len(closes)
    assert rsi[0] is None
    assert rsi[-1] is not None
    assert 0 <= rsi[-1] <= 100


def test_crossed_above():
    assert crossed_above(prev_short=40, prev_long=45, curr_short=50, curr_long=48)
    assert not crossed_above(prev_short=46, prev_long=45, curr_short=50, curr_long=48)


def test_crossed_below():
    assert crossed_below(prev_short=55, prev_long=50, curr_short=45, curr_long=48)
    assert not crossed_below(prev_short=45, prev_long=50, curr_short=44, curr_long=48)
