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


def test_parse_qt_line_does_not_fallback_range_to_current_price():
    line = 'v_sz300308="51~中际旭创~300308~120.5~118.0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~0~2.12~~~~100000~1200000000";'
    q = parse_qt_line(line)
    assert q is not None
    assert q.now == 120.5
    assert q.high == 0
    assert q.low == 0


def test_parse_qt_line_detects_limit_down():
    line = 'v_sh603601="1~再升科技~603601~19.06~21.18~19.06~81028~81028~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~19.06~1258952~19.07~6296~19.08~3656~19.09~1348~19.10~4392~~20260601161411~-2.12~-10.01~19.06~19.06~19.06/81028/154439368~81028~15444~0.71~590.61~~19.06~19.06~0.00~217.73~217.73~8.05~23.30~19.06~0.04~-1274644~19.06~380.47~387.99~~~1.69~15443.9368~0.0000~0~ ~GP-A~52.85~-1.09~0.14~1.36~1.25~23.53~3.46~2.69~25.39~65.74~1142340971~1142340971~-100.00~221.42~1142340971~~~422.19~0.00~~CNY~0~___D__F__N~19.11~-2949~";'
    q = parse_qt_line(line)
    assert q is not None
    assert q.limit_up == 23.3
    assert q.limit_down == 19.06
    assert q.limit_status == "跌停"
