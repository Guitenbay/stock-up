import sqlite3

from stock_up.db import init_db


def test_init_db_creates_tables(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()

    assert "watchlist" in tables
    assert "holdings" in tables
    assert "holding_history" in tables
    assert "trades" in tables
    assert "alerts" in tables
    assert "quotes_daily" in tables
