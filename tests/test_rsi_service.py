from stock_up.db import init_db, connect
from stock_up.market.mock import MockProvider
from stock_up.models import DailyBar
from stock_up.services.rsi import update_rsi_for_code


def test_update_rsi_for_code_caches_daily_rows(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    bars = [DailyBar(code="300308", trade_date=f"2026-05-{i:02d}", open=10+i, high=11+i, low=9+i, close=10+i) for i in range(1, 20)]
    provider = MockProvider(daily_bars={"300308": bars})

    update_rsi_for_code(db_path, provider, "300308", days=30, short_period=6, long_period=12)

    with connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM quotes_daily WHERE code='300308' ORDER BY trade_date").fetchall()
    assert len(rows) == 19
    assert rows[-1]["rsi_short"] is not None
    assert rows[-1]["rsi_long"] is not None
