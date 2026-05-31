from stock_up.market.stockapi import parse_hot_boards, parse_hot_leaders


def test_parse_hot_boards():
    payload = {
        "code": 20000,
        "msg": "success",
        "data": [
            {"bkCode": "801004", "bkName": "锂电池", "qjzf": 1.53, "qjje": 498, "jlrts": 1, "qiangdu": 29576.2, "time": "2025-11-14"}
        ],
    }
    boards = parse_hot_boards(payload)
    assert len(boards) == 1
    assert boards[0].bk_code == "801004"
    assert boards[0].bk_name == "锂电池"


def test_parse_hot_leaders():
    payload = {
        "code": 20000,
        "msg": "success",
        "data": [
            {"qjzf": 61.23, "code": "002083", "jlrts": 4, "name": "孚日股份", "bkCode": "801004", "bk": "电解液、服装家纺", "time": "2025-11-14"}
        ],
    }
    leaders = parse_hot_leaders(payload)
    assert len(leaders) == 1
    assert leaders[0].code == "002083"
    assert leaders[0].name == "孚日股份"
    assert leaders[0].board_name == "电解液、服装家纺"
