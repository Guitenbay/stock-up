from stock_up.db import connect, init_db
from stock_up.services.rsi import update_rsi_for_code


class DirectRsiProvider:
    def get_rsi_rows(self, code, days, cycle1=6, cycle2=12, cycle3=24):
        return [("2026-05-30", 40.0, 45.0), ("2026-05-31", 50.0, 48.0)]

    def get_daily_bars(self, code, days):
        raise AssertionError("daily bars should not be called when direct RSI exists")


def test_update_rsi_uses_direct_provider(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    assert update_rsi_for_code(db_path, DirectRsiProvider(), "300308")
    with connect(db_path) as conn:
        rows = conn.execute("SELECT trade_date, rsi_short, rsi_long FROM quotes_daily WHERE code='300308' ORDER BY trade_date").fetchall()
    assert len(rows) == 2
    assert rows[-1]["rsi_short"] == 50
