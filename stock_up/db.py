from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS watchlist (
  code TEXT PRIMARY KEY,
  name TEXT,
  reason TEXT,
  added_date TEXT,
  high REAL,
  low REAL,
  avg REAL,
  now REAL,
  limit_up REAL,
  limit_down REAL,
  limit_status TEXT,
  f382 REAL,
  f618 REAL,
  f786 REAL,
  status TEXT,
  abandoned_at TEXT,
  abandon_reason TEXT,
  note TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS holdings (
  code TEXT PRIMARY KEY,
  name TEXT,
  cost REAL,
  quantity INTEGER,
  buy_date TEXT,
  now REAL,
  highest REAL,
  high REAL,
  low REAL,
  limit_up REAL,
  limit_down REAL,
  limit_status TEXT,
  swing_low REAL,
  ref_high REAL,
  rule_type TEXT,
  status TEXT,
  note TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS holding_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT,
  name TEXT,
  cost REAL,
  quantity INTEGER,
  buy_date TEXT,
  close_date TEXT,
  close_price REAL,
  realized_pnl REAL,
  reason TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT,
  name TEXT,
  trade_type TEXT,
  price REAL,
  quantity INTEGER,
  trade_date TEXT,
  reason TEXT,
  realized_pnl REAL,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT,
  name TEXT,
  signal_type TEXT,
  level TEXT,
  price REAL,
  message TEXT,
  trade_date TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS quotes_daily (
  code TEXT,
  trade_date TEXT,
  open REAL,
  high REAL,
  low REAL,
  close REAL,
  pre_close REAL,
  pct_chg REAL,
  amount REAL,
  volume REAL,
  is_limit_up INTEGER,
  rsi_short REAL,
  rsi_long REAL,
  PRIMARY KEY (code, trade_date)
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        _ensure_column(conn, "watchlist", "limit_up", "REAL")
        _ensure_column(conn, "watchlist", "limit_down", "REAL")
        _ensure_column(conn, "watchlist", "limit_status", "TEXT")
        _ensure_column(conn, "holdings", "limit_up", "REAL")
        _ensure_column(conn, "holdings", "limit_down", "REAL")
        _ensure_column(conn, "holdings", "limit_status", "TEXT")
        conn.commit()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, column_type: str) -> None:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    if column not in {row["name"] for row in rows}:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
