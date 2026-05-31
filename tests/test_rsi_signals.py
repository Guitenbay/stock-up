from stock_up.strategy.technical import detect_rsi_cross


def test_detect_rsi_golden_cross():
    signal = detect_rsi_cross(prev_short=40, prev_long=45, curr_short=50, curr_long=48)
    assert signal == "golden"


def test_detect_rsi_dead_cross():
    signal = detect_rsi_cross(prev_short=55, prev_long=50, curr_short=45, curr_long=48)
    assert signal == "dead"


def test_detect_rsi_no_cross():
    assert detect_rsi_cross(50, 45, 55, 48) is None
