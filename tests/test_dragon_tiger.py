from stock_up.market.stockapi import parse_dragon_tiger


def test_parse_dragon_tiger_array_object():
    payload = {
        "code": 20000,
        "msg": "success",
        "data": {
            "thsCode": ["000858"],
            "name": ["五粮液"],
            "reason": ["日涨幅偏离值达7%"],
            "close": ["84.89"],
            "chg": ["4.17"],
            "turnover": ["1.55"],
            "buyAmount": ["1000"],
            "sellAmount": ["800"],
            "topAmount": ["1800"],
            "endDate": ["2026-05-29"],
        },
    }
    rows = parse_dragon_tiger(payload)
    assert len(rows) == 1
    assert rows[0].code == "000858"
    assert rows[0].name == "五粮液"
    assert rows[0].reason == "日涨幅偏离值达7%"


def test_parse_dragon_tiger_bad_payload():
    assert parse_dragon_tiger({"code": 500}) == []
