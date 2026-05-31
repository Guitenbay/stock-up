from stock_up.strategy.trading_day import trading_days_since


def test_trading_days_since_excludes_weekends():
    # 2026-05-29 Friday to 2026-06-02 Tuesday = Fri, Mon, Tue = 3 trading days
    assert trading_days_since("2026-05-29", "2026-06-02", holidays=set()) == 3


def test_trading_days_since_excludes_holidays():
    assert trading_days_since("2026-05-29", "2026-06-02", holidays={"2026-06-01"}) == 2


def test_trading_days_since_future_returns_zero():
    assert trading_days_since("2026-06-03", "2026-06-02", holidays=set()) == 0
