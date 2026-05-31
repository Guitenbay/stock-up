from __future__ import annotations

from pathlib import Path

from stock_up.db import connect
from stock_up.market.base import MarketDataProvider
from stock_up.strategy.rsi import calculate_rsi_series


def _get_direct_rsi_rows(
    provider: MarketDataProvider,
    code: str,
    days: int,
    short_period: int,
    long_period: int,
) -> list[tuple[str, float, float]]:
    get_rsi_rows = getattr(provider, "get_rsi_rows", None)
    if not callable(get_rsi_rows):
        return []
    try:
        return list(get_rsi_rows(code, days, short_period, long_period, 24))
    except Exception:
        return []


def has_rsi_cache_for_date(db_path: Path, code: str, trade_date: str) -> bool:
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT 1 FROM quotes_daily
            WHERE code=? AND trade_date=? AND rsi_short IS NOT NULL AND rsi_long IS NOT NULL
            LIMIT 1
            """,
            (code, trade_date),
        ).fetchone()
    return row is not None


def update_rsi_for_code(
    db_path: Path,
    provider: MarketDataProvider,
    code: str,
    days: int = 30,
    short_period: int = 6,
    long_period: int = 12,
    cache_date: str | None = None,
) -> bool:
    if cache_date and has_rsi_cache_for_date(db_path, code, cache_date):
        return False

    direct_rows = _get_direct_rsi_rows(provider, code, days, short_period, long_period)
    if direct_rows:
        with connect(db_path) as conn:
            for trade_date, rsi_s, rsi_l in direct_rows:
                conn.execute(
                    """
                    INSERT INTO quotes_daily(code, trade_date, rsi_short, rsi_long)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(code, trade_date) DO UPDATE SET
                      rsi_short=excluded.rsi_short,
                      rsi_long=excluded.rsi_long
                    """,
                    (code, trade_date, rsi_s, rsi_l),
                )
            conn.commit()
        return True

    bars = provider.get_daily_bars(code, days)
    closes = [bar.close for bar in bars]
    rsi_short = calculate_rsi_series(closes, short_period)
    rsi_long = calculate_rsi_series(closes, long_period)

    with connect(db_path) as conn:
        for idx, bar in enumerate(bars):
            pre_close = bars[idx - 1].close if idx > 0 else 0.0
            pct_chg = ((bar.close - pre_close) / pre_close * 100) if pre_close else 0.0
            conn.execute(
                """
                INSERT INTO quotes_daily(code, trade_date, open, high, low, close, pre_close, pct_chg, amount, volume, is_limit_up, rsi_short, rsi_long)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(code, trade_date) DO UPDATE SET
                  open=excluded.open,
                  high=excluded.high,
                  low=excluded.low,
                  close=excluded.close,
                  pre_close=excluded.pre_close,
                  pct_chg=excluded.pct_chg,
                  amount=excluded.amount,
                  volume=excluded.volume,
                  rsi_short=excluded.rsi_short,
                  rsi_long=excluded.rsi_long
                """,
                (
                    bar.code,
                    bar.trade_date,
                    bar.open,
                    bar.high,
                    bar.low,
                    bar.close,
                    pre_close,
                    pct_chg,
                    bar.amount,
                    bar.volume,
                    0,
                    rsi_short[idx],
                    rsi_long[idx],
                ),
            )
        conn.commit()
    return bool(bars)


def latest_two_rsi(db_path: Path, code: str) -> tuple[tuple[float | None, float | None], tuple[float | None, float | None]] | None:
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT rsi_short, rsi_long FROM quotes_daily WHERE code=? ORDER BY trade_date DESC LIMIT 2",
            (code,),
        ).fetchall()
    if len(rows) < 2:
        return None
    curr = (rows[0]["rsi_short"], rows[0]["rsi_long"])
    prev = (rows[1]["rsi_short"], rows[1]["rsi_long"])
    return prev, curr
