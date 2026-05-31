from stock_up.services.initial_low import choose_initial_low
from stock_up.models import DailyBar, LimitUpStock


def test_choose_initial_low_same_day():
    stock = LimitUpStock(code="300308", name="x", trade_date="2026-05-31", high=120, low=110, close=120)
    assert choose_initial_low(stock, [], mode="same_day") == 110


def test_choose_initial_low_recent_1d():
    stock = LimitUpStock(code="300308", name="x", trade_date="2026-05-31", high=120, low=110, close=120)
    bars = [DailyBar(code="300308", trade_date="2026-05-30", open=100, high=105, low=95, close=102)]
    assert choose_initial_low(stock, bars, mode="recent_1d") == 95


def test_choose_initial_low_recent_1d_falls_back_to_same_day():
    stock = LimitUpStock(code="300308", name="x", trade_date="2026-05-31", high=120, low=110, close=120)
    assert choose_initial_low(stock, [], mode="recent_1d") == 110
