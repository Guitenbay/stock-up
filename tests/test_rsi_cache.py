from stock_up.db import connect, init_db
from stock_up.market.mock import MockProvider
from stock_up.models import DailyBar
from stock_up.services.rsi import has_rsi_cache_for_date, update_rsi_for_code


def test_has_rsi_cache_for_date(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO quotes_daily(code, trade_date, open, high, low, close, rsi_short, rsi_long) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("300308", "2026-05-31", 1, 1, 1, 1, 50, 55),
        )
        conn.commit()
    assert has_rsi_cache_for_date(db_path, "300308", "2026-05-31")
    assert not has_rsi_cache_for_date(db_path, "300308", "2026-05-30")


def test_update_rsi_skips_when_cache_exists(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO quotes_daily(code, trade_date, open, high, low, close, rsi_short, rsi_long) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("300308", "2026-05-31", 1, 1, 1, 1, 50, 55),
        )
        conn.commit()

    provider = MockProvider(daily_bars={"300308": [DailyBar(code="300308", trade_date="2026-05-31", open=1, high=1, low=1, close=1)]})
    assert not update_rsi_for_code(db_path, provider, "300308", cache_date="2026-05-31")
