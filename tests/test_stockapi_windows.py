from datetime import date

from stock_up.market.stockapi import build_date_windows


def test_build_date_windows_uses_max_five_days():
    windows = build_date_windows(date(2026, 5, 1), date(2026, 5, 12), max_days=5)
    assert windows == [
        ("2026-05-01", "2026-05-05"),
        ("2026-05-06", "2026-05-10"),
        ("2026-05-11", "2026-05-12"),
    ]
