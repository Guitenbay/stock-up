from stock_up.market.qq import parse_qt_line


def test_parse_qt_line_a_share():
    line = 'v_sz300308="51~中际旭创~300308~120.5~118.0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~2.12~123.4~117.8~0~100000~1200000000";'
    q = parse_qt_line(line)
    assert q is not None
    assert q.code == "sz300308"
    assert q.name == "中际旭创"
    assert q.now == 120.5
    assert q.pre_close == 118.0
    assert q.high == 123.4
    assert q.low == 117.8
    assert q.avg > 0


def test_parse_qt_line_ignores_bad_line():
    assert parse_qt_line("bad") is None
