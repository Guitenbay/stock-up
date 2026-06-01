from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from stock_up.market.base import MarketDataProvider
from stock_up.repositories import AlertRepository, HoldingRepository, WatchRepository
from stock_up.strategy.fib import calculate_fib_levels
from stock_up.strategy.holding import evaluate_holding
from stock_up.strategy.trading_day import trading_days_since
from stock_up.strategy.watch import evaluate_watch


@dataclass(frozen=True)
class TickSignal:
    code: str
    name: str
    title: str
    reasons: list[str] = field(default_factory=list)
    level: str = "info"
    price: float = 0.0


@dataclass(frozen=True)
class TickSummary:
    updated_watch_count: int = 0
    updated_holding_count: int = 0
    watch_signals: list[TickSignal] = field(default_factory=list)
    holding_signals: list[TickSignal] = field(default_factory=list)


def run_tick(db_path: Path, provider: MarketDataProvider, trade_date: str | None = None) -> TickSummary:
    watch_repo = WatchRepository(db_path)
    holding_repo = HoldingRepository(db_path)
    alerts = AlertRepository(db_path)
    today = trade_date or date.today().isoformat()

    watch_items = watch_repo.list_active()
    holdings = holding_repo.list_open()
    codes = sorted({item.code for item in watch_items} | {h.code for h in holdings})
    quote_map = {q.code: q for q in provider.get_realtime_quotes(codes)}

    updated_watch = 0
    watch_signals: list[TickSignal] = []
    for item in watch_items:
        quote = quote_map.get(item.code)
        if not quote:
            continue
        item.name = quote.name or item.name
        item.now = quote.now
        item.avg = quote.avg or item.avg
        if quote.high > item.high:
            item.high = quote.high
        levels = calculate_fib_levels(item.high, item.low)
        # persist current levels through raw update fields supported by table
        watch_repo.upsert(item)
        _update_watch_levels(db_path, item.code, levels.f382, levels.f618, levels.f786)
        updated_watch += 1

        if quote.limit_status == "涨停":
            _append_watch_limit_signal(watch_signals, alerts, item.code, item.name, "涨停不追", ["当前涨停，暂不按买点处理"], "warning", quote.now, today)
            continue
        if quote.limit_status == "跌停":
            _append_watch_limit_signal(watch_signals, alerts, item.code, item.name, "跌停回避", ["当前跌停，流动性和趋势风险高，暂不观察买点"], "danger", quote.now, today)
            continue

        result = evaluate_watch(item)
        if result.action in ("watch", "abandon") and alerts.should_alert(item.code, result.title, result.price, 0.01):
            message = "; ".join(result.reasons)
            alerts.record(item.code, item.name, result.title, result.level, result.price, message, today)
            if result.action == "abandon":
                watch_repo.mark_abandoned(item.code, message, today)
            watch_signals.append(TickSignal(
                code=item.code,
                name=item.name,
                title=result.title,
                reasons=result.reasons,
                level=result.level,
                price=result.price,
            ))

    updated_holdings = 0
    holding_signals: list[TickSignal] = []
    for holding in holdings:
        quote = quote_map.get(holding.code)
        if not quote:
            continue
        holding.name = quote.name or holding.name
        holding.now = quote.now
        if quote.high > 0:
            holding.highest = max(holding.highest, quote.high)
            if quote.high > holding.high:
                holding.high = quote.high
        elif quote.now > 0:
            holding.highest = max(holding.highest, quote.now)
        holding_repo.upsert(holding)
        updated_holdings += 1

        days = trading_days_since(holding.buy_date, today) if holding.buy_date else None
        result = evaluate_holding(holding, trading_days_since_buy=days)
        if result.action in ("stop_loss", "take_profit") and alerts.should_alert(holding.code, result.title, result.price, 0.01):
            message = "; ".join(result.reasons)
            alerts.record(holding.code, holding.name, result.title, result.level, result.price, message, today)
            holding_signals.append(TickSignal(
                code=holding.code,
                name=holding.name,
                title=result.title,
                reasons=result.reasons,
                level=result.level,
                price=result.price,
            ))
        if quote.limit_status == "跌停":
            _append_holding_limit_signal(holding_signals, alerts, holding.code, holding.name, "跌停风险", ["当前跌停，可能无法成交，优先关注止损计划"], "danger", quote.now, today)
        elif quote.limit_status == "涨停":
            _append_holding_limit_signal(holding_signals, alerts, holding.code, holding.name, "涨停持有观察", ["当前涨停，趋势较强，暂不主动止盈"], "info", quote.now, today)

    return TickSummary(
        updated_watch_count=updated_watch,
        updated_holding_count=updated_holdings,
        watch_signals=watch_signals,
        holding_signals=holding_signals,
    )


def _append_watch_limit_signal(
    signals: list[TickSignal],
    alerts: AlertRepository,
    code: str,
    name: str,
    title: str,
    reasons: list[str],
    level: str,
    price: float,
    today: str,
) -> None:
    if not alerts.should_alert(code, title, price, 0.01):
        return
    message = "; ".join(reasons)
    alerts.record(code, name, title, level, price, message, today)
    signals.append(TickSignal(code=code, name=name, title=title, reasons=reasons, level=level, price=price))


def _append_holding_limit_signal(
    signals: list[TickSignal],
    alerts: AlertRepository,
    code: str,
    name: str,
    title: str,
    reasons: list[str],
    level: str,
    price: float,
    today: str,
) -> None:
    if not alerts.should_alert(code, title, price, 0.01):
        return
    message = "; ".join(reasons)
    alerts.record(code, name, title, level, price, message, today)
    signals.append(TickSignal(code=code, name=name, title=title, reasons=reasons, level=level, price=price))


def _update_watch_levels(db_path: Path, code: str, f382: float, f618: float, f786: float) -> None:
    from stock_up.db import connect

    with connect(db_path) as conn:
        conn.execute(
            "UPDATE watchlist SET f382=?, f618=?, f786=? WHERE code=?",
            (f382, f618, f786, code),
        )
        conn.commit()
