from stock_up.codes import format_code


def test_format_a_share_codes():
    assert format_code("600519") == "sh600519"
    assert format_code("300308") == "sz300308"
    assert format_code("510300") == "sh510300"
    assert format_code("830001") == "bj830001"
    assert format_code("920190") == "bj920190"


def test_format_hk_codes():
    assert format_code("700") == "hk00700"
    assert format_code("00700") == "hk00700"


def test_keep_prefixed_code():
    assert format_code("sz300308") == "sz300308"
    assert format_code("SH600519") == "sh600519"
