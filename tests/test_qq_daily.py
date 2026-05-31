from stock_up.market.qq import parse_daily_js


def test_parse_daily_js():
    text = 'daily_data="230101 10.00 11.00 12.00 9.00 1000\n230102 11.00 12.00 13.00 10.00 2000";'
    bars = parse_daily_js("sz000858", text)
    assert len(bars) == 2
    assert bars[0].trade_date == "2023-01-01"
    assert bars[0].open == 10
    assert bars[0].close == 11
    assert bars[0].high == 12
    assert bars[0].low == 9
    assert bars[0].volume == 1000
