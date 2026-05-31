from stock_up.market.stockapi import parse_stockapi_rsi


def test_parse_stockapi_rsi():
    payload = {
        "code": 20000,
        "msg": "success",
        "data": [
            {"date": "2021-10-10", "api_code": "600004.SH", "rsi1": 29.7, "rsi2": 35.2, "rsi3": 40.1}
        ],
    }
    rows = parse_stockapi_rsi(payload)
    assert rows == [("2021-10-10", 29.7, 35.2)]


def test_parse_stockapi_rsi_with_array_object():
    payload = {
        "code": 20000,
        "msg": "success",
        "data": {
            "api_code": "000858",
            "date": ["2026-05-27", "2026-05-28"],
            "rsi1": [17.3, 10.3],
            "rsi2": [14.9, 11.8],
        },
    }
    rows = parse_stockapi_rsi(payload)
    assert rows == [("2026-05-27", 17.3, 14.9), ("2026-05-28", 10.3, 11.8)]


def test_parse_stockapi_rsi_bad_payload():
    assert parse_stockapi_rsi({"code": 500}) == []
