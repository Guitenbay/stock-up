from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from stock_up.db import connect
from stock_up.models import Holding, WatchItem


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class WatchRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def upsert(self, item: WatchItem) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO watchlist(code, name, reason, high, low, avg, now, limit_up, limit_down, limit_status, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                  name=excluded.name,
                  reason=excluded.reason,
                  high=excluded.high,
                  low=excluded.low,
                  avg=excluded.avg,
                  now=excluded.now,
                  limit_up=excluded.limit_up,
                  limit_down=excluded.limit_down,
                  limit_status=excluded.limit_status,
                  status=excluded.status,
                  updated_at=excluded.updated_at
                """,
                (item.code, item.name, item.reason, item.high, item.low, item.avg, item.now, item.limit_up, item.limit_down, item.limit_status, item.status, _now()),
            )
            conn.commit()

    def get(self, code: str) -> WatchItem | None:
        with connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM watchlist WHERE code = ?", (code,)).fetchone()
        return _watch_from_row(row) if row else None

    def delete(self, code: str) -> None:
        with connect(self.db_path) as conn:
            conn.execute("DELETE FROM watchlist WHERE code = ?", (code,))
            conn.commit()

    def list_active(self) -> list[WatchItem]:
        with connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM watchlist WHERE COALESCE(status, 'watching') != 'abandoned' ORDER BY updated_at DESC").fetchall()
        return [_watch_from_row(r) for r in rows]

    def list_abandoned(self) -> list[WatchItem]:
        with connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM watchlist WHERE status = 'abandoned' ORDER BY abandoned_at DESC").fetchall()
        return [_watch_from_row(r) for r in rows]

    def mark_abandoned(self, code: str, reason: str, date: str) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                "UPDATE watchlist SET status='abandoned', abandon_reason=?, abandoned_at=?, updated_at=? WHERE code=?",
                (reason, date, _now(), code),
            )
            conn.commit()


def _watch_from_row(row: Any) -> WatchItem:
    return WatchItem(
        code=row["code"],
        name=row["name"] or "",
        reason=row["reason"] or "",
        high=row["high"] or 0.0,
        low=row["low"] or 0.0,
        avg=row["avg"] or 0.0,
        now=row["now"] or 0.0,
        limit_up=row["limit_up"] or 0.0,
        limit_down=row["limit_down"] or 0.0,
        limit_status=row["limit_status"] or "",
        status=row["status"] or "watching",
    )


@dataclass
class ClosedHolding:
    code: str
    realized_pnl: float


class HoldingRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def upsert(self, h: Holding) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO holdings(code, name, cost, quantity, buy_date, now, highest, high, low, limit_up, limit_down, limit_status, swing_low, ref_high, rule_type, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                  name=excluded.name,
                  cost=excluded.cost,
                  quantity=excluded.quantity,
                  buy_date=excluded.buy_date,
                  now=excluded.now,
                  highest=excluded.highest,
                  high=excluded.high,
                  low=excluded.low,
                  limit_up=excluded.limit_up,
                  limit_down=excluded.limit_down,
                  limit_status=excluded.limit_status,
                  swing_low=excluded.swing_low,
                  ref_high=excluded.ref_high,
                  rule_type=excluded.rule_type,
                  status=excluded.status,
                  updated_at=excluded.updated_at
                """,
                (h.code, h.name, h.cost, h.quantity, h.buy_date, h.now, h.highest, h.high, h.low, h.limit_up, h.limit_down, h.limit_status, h.swing_low, h.ref_high, h.rule_type, "open", _now()),
            )
            conn.commit()

    def get(self, code: str) -> Holding | None:
        with connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM holdings WHERE code=?", (code,)).fetchone()
        return _holding_from_row(row) if row else None

    def list_open(self) -> list[Holding]:
        with connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM holdings ORDER BY updated_at DESC").fetchall()
        return [_holding_from_row(r) for r in rows]

    def add_buy(self, code: str, price: float, quantity: int) -> Holding:
        h = self.get(code)
        if not h:
            raise ValueError(f"Holding not found: {code}")
        total_qty = h.quantity + quantity
        new_cost = ((h.cost * h.quantity) + (price * quantity)) / total_qty
        h.cost = round(new_cost, 4)
        h.quantity = total_qty
        h.highest = max(h.highest, price)
        self.upsert(h)
        return h

    def close(self, code: str, close_price: float, close_date: str, reason: str) -> ClosedHolding:
        h = self.get(code)
        if not h:
            raise ValueError(f"Holding not found: {code}")
        realized_pnl = round((close_price - h.cost) * h.quantity, 4)
        with connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO holding_history(code, name, cost, quantity, buy_date, close_date, close_price, realized_pnl, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (h.code, h.name, h.cost, h.quantity, h.buy_date, close_date, close_price, realized_pnl, reason, _now()),
            )
            conn.execute("DELETE FROM holdings WHERE code=?", (code,))
            conn.commit()
        return ClosedHolding(code=code, realized_pnl=realized_pnl)


def _holding_from_row(row: Any) -> Holding:
    return Holding(
        code=row["code"],
        name=row["name"] or "",
        cost=row["cost"] or 0.0,
        quantity=row["quantity"] or 0,
        buy_date=row["buy_date"] or "",
        now=row["now"] or 0.0,
        highest=row["highest"] or 0.0,
        high=row["high"] or 0.0,
        low=row["low"] or 0.0,
        limit_up=row["limit_up"] or 0.0,
        limit_down=row["limit_down"] or 0.0,
        limit_status=row["limit_status"] or "",
        swing_low=row["swing_low"] or 0.0,
        ref_high=row["ref_high"] or 0.0,
        rule_type=row["rule_type"] or "wolf_swing",
    )


class AlertRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def latest(self, code: str, signal_type: str):
        with connect(self.db_path) as conn:
            return conn.execute(
                "SELECT * FROM alerts WHERE code=? AND signal_type=? ORDER BY id DESC LIMIT 1",
                (code, signal_type),
            ).fetchone()

    def should_alert(self, code: str, signal_type: str, price: float, threshold: float) -> bool:
        row = self.latest(code, signal_type)
        if not row:
            return True
        last_price = row["price"] or 0
        if last_price <= 0:
            return True
        return abs(price - last_price) / last_price >= threshold

    def record(self, code: str, name: str, signal_type: str, level: str, price: float, message: str, trade_date: str) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO alerts(code, name, signal_type, level, price, message, trade_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (code, name, signal_type, level, price, message, trade_date, _now()),
            )
            conn.commit()


class TradeRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def record(self, code: str, name: str, trade_type: str, price: float, quantity: int, trade_date: str, reason: str = "", realized_pnl: float | None = None) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO trades(code, name, trade_type, price, quantity, trade_date, reason, realized_pnl, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (code, name, trade_type, price, quantity, trade_date, reason, realized_pnl, _now()),
            )
            conn.commit()

    def list_by_date(self, trade_date: str) -> list[Any]:
        with connect(self.db_path) as conn:
            return conn.execute("SELECT * FROM trades WHERE trade_date=? ORDER BY id", (trade_date,)).fetchall()
