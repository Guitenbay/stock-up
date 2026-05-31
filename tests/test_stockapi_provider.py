from stock_up.market.stockapi import parse_stockapi_daily, strip_market_prefix


def test_strip_market_prefix():
    assert strip_market_prefix("sh600004") == "600004"
    assert strip_market_prefix("sz000858") == "000858"
    assert strip_market_prefix("600004") == "600004"


def test_parse_stockapi_daily_with_date_array():
    payload = {
        "code": 20000,
        "msg": "success",
        "data": {
            "date": ["2021-11-09"],
            "open": [10.0],
            "high": [11.0],
            "low": [9.0],
            "close": [10.5],
            "volume": [1000],
            "amount": [2000],
        },
    }
    bars = parse_stockapi_daily("600004", payload)
    assert len(bars) == 1
    assert bars[0].trade_date == "2021-11-09"
    assert bars[0].close == 10.5


def test_parse_stockapi_daily_with_list_rows():
    payload = {
        "code": 20000,
        "msg": "success",
        "data": [
            {
                "code": "000858.SZ",
                "time": "2026-05-27",
                "open": "83",
                "high": "86.25",
                "low": "81.7",
                "close": "83.89",
                "volume": "60380066",
                "amount": "5045124428",
            }
        ],
    }
    bars = parse_stockapi_daily("sz000858", payload)
    assert len(bars) == 1
    assert bars[0].trade_date == "2026-05-27"
    assert bars[0].close == 83.89


def test_parse_stockapi_daily_without_dates_returns_empty():
    payload = {"code": 20000, "data": {"open": [10.0], "close": [10.5]}}
    assert parse_stockapi_daily("600004", payload) == []
