from datetime import date

from stock_up.market.akshare_provider import calc_hist_date_range


def test_calc_hist_date_range_uses_buffer_days():
    start, end = calc_hist_date_range(days=30, today=date(2026, 5, 31))
    assert end == "20260531"
    assert start < end
    # buffer should be larger than 30 calendar days enough for weekends/holidays
    assert start == "20260322"
