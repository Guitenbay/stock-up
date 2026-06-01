from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from stock_up.codes import format_code
from stock_up.config import load_config, write_default_config
from stock_up.db import init_db
from stock_up.market.factory import make_provider
from stock_up.models import Holding, WatchItem
from stock_up.services.daily import run_daily
from stock_up.services.dragon_tiger_scanner import run_dragon_tiger_scan
from stock_up.services.scanner import run_limit_up_scan
from stock_up.services.tick import run_tick
from stock_up.repositories import AlertRepository, HoldingRepository, TradeRepository, WatchRepository
from stock_up.strategy.holding import evaluate_holding
from stock_up.strategy.trading_day import trading_days_since
from stock_up.strategy.watch import evaluate_watch

app = typer.Typer(help="stock-up CLI")
watch_app = typer.Typer(help="观察池")
hold_app = typer.Typer(help="持仓")
scan_app = typer.Typer(help="扫描")
app.add_typer(watch_app, name="watch")
app.add_typer(hold_app, name="hold")
app.add_typer(scan_app, name="scan")
console = Console()


def default_home() -> Path:
    return Path.home() / ".stock-up"


def db_path(home: Path) -> Path:
    return home / "data.db"


@app.command()
def init(home: Path = typer.Option(default_home(), "--home", help="stock-up home directory")):
    """初始化配置和数据库。"""
    home.mkdir(parents=True, exist_ok=True)
    cfg_path = home / "config.yaml"
    if not cfg_path.exists():
        write_default_config(cfg_path)
    (home / "reports").mkdir(exist_ok=True)
    init_db(db_path(home))
    console.print(f"初始化完成: {home}")


def _make_provider(provider: str, purpose: str = "realtime"):
    return make_provider(provider, purpose=purpose)


def _provider_from_config(home: Path, purpose: str) -> str:
    cfg = load_config(home / "config.yaml")
    if purpose == "realtime":
        return cfg.market.realtime_provider
    if purpose == "daily":
        return cfg.market.daily_provider
    if purpose == "dragon_tiger":
        return cfg.market.dragon_tiger_provider
    if purpose == "limit_up":
        return cfg.market.limit_up_provider
    return cfg.market.default_provider


def _resolve_provider(home: Path, provider: str, purpose: str) -> str:
    if provider != "config":
        return provider
    return _provider_from_config(home, purpose)


def _resolve_stock_name(code: str, provided_name: str, provider: str = "qq") -> str:
    if provided_name:
        return provided_name
    full_code = format_code(code) or code
    try:
        quotes = _make_provider(provider, purpose="realtime").get_realtime_quotes([full_code])
    except Exception:
        return full_code
    if quotes and quotes[0].name:
        return quotes[0].name
    return full_code


@app.command()
def quote(
    code: str,
    home: Path = typer.Option(default_home(), "--home"),
    provider: str = typer.Option("config", "--provider", help="config / auto / qq / akshare / mock"),
):
    """查看单只股票行情，便于对比数据源。"""
    full_code = format_code(code) or code
    provider_name = _resolve_provider(home, provider, "realtime")
    quotes = _make_provider(provider_name, purpose="realtime").get_realtime_quotes([full_code])
    if not quotes:
        console.print(f"暂无行情: {full_code}")
        return
    q = quotes[0]
    table = Table("字段", "值")
    table.add_row("代码", q.code)
    table.add_row("名称", q.name)
    table.add_row("当前价", f"{q.now:g}")
    table.add_row("昨收", f"{q.pre_close:g}")
    table.add_row("日高", f"{q.high:g}")
    table.add_row("日低", f"{q.low:g}")
    table.add_row("均价", f"{q.avg:g}")
    table.add_row("成交额", f"{q.amount:g}")
    table.add_row("成交量", f"{q.volume:g}")
    console.print(table)


@app.command()
def tick(
    home: Path = typer.Option(default_home(), "--home"),
    provider: str = typer.Option("config", "--provider", help="config / auto / qq / mock"),
):
    """执行一次盘中检查，由外部定时任务调用。"""
    provider_name = _resolve_provider(home, provider, "realtime")
    summary = run_tick(db_path(home), _make_provider(provider_name, purpose="realtime"))
    console.print(f"tick完成: 观察 {summary.updated_watch_count}，持仓 {summary.updated_holding_count}")


@app.command()
def daily(
    home: Path = typer.Option(default_home(), "--home"),
    provider: str = typer.Option("config", "--provider", help="config / auto / stockapi / mock"),
    trade_date: str = typer.Option("", "--date"),
):
    """执行每日扫描、检查并生成报告。"""
    date_text = trade_date or date.today().isoformat()
    cfg = load_config(home / "config.yaml")
    provider_name = _resolve_provider(home, provider, "daily")
    summary = run_daily(
        db_path(home),
        _make_provider(provider_name, purpose="daily"),
        date_text,
        home / "reports",
        rsi_max_updates=cfg.technical.rsi.max_updates_per_daily,
        enable_hot_leader_scan=cfg.auto_watch.hot_leader_scan_enabled,
        enable_dragon_tiger_scan=cfg.auto_watch.dragon_tiger_scan_enabled,
    )
    console.print(f"daily完成: 新增观察 {summary.new_watch_count}，观察动作 {summary.watch_action_count}，持仓动作 {summary.holding_action_count}")
    console.print(f"日报: {summary.report_path}")


@scan_app.command("dragon-tiger")
def scan_dragon_tiger(
    home: Path = typer.Option(default_home(), "--home"),
    provider: str = typer.Option("config", "--provider", help="config / auto / stockapi / mock"),
    trade_date: str = typer.Option("", "--date"),
):
    """扫描龙虎榜并加入观察池。"""
    date_text = trade_date or date.today().isoformat()
    provider_name = _resolve_provider(home, provider, "dragon_tiger")
    summary = run_dragon_tiger_scan(db_path(home), _make_provider(provider_name, purpose="dragon_tiger"), date_text)
    console.print(f"龙虎榜扫描完成: 总数 {summary.total_count}，加入 {summary.added_count}")


@scan_app.command("limit-up")
def scan_limit_up(
    home: Path = typer.Option(default_home(), "--home"),
    provider: str = typer.Option("config", "--provider", help="config / auto / akshare / mock"),
    trade_date: str = typer.Option("", "--date"),
    low_mode: str = typer.Option("same_day", "--low-mode"),
):
    """扫描涨停池并加入观察池。"""
    date_text = trade_date or date.today().isoformat()
    provider_name = _resolve_provider(home, provider, "limit_up")
    summary = run_limit_up_scan(db_path(home), _make_provider(provider_name, purpose="limit_up"), date_text, initial_low_mode=low_mode)  # type: ignore[arg-type]
    console.print(f"涨停扫描完成: 总数 {summary.total_count}，加入 {summary.added_count}，跳过 {summary.skipped_count}")


@watch_app.command("add")
def watch_add(
    code: str,
    home: Path = typer.Option(default_home(), "--home"),
    name: str = typer.Option("", "--name"),
    reason: str = typer.Option("手动关注", "--reason"),
    high: float = typer.Option(0.0, "--high"),
    low: float = typer.Option(0.0, "--low"),
    now: float = typer.Option(0.0, "--now"),
):
    full_code = format_code(code) or code
    resolved_name = _resolve_stock_name(full_code, name)
    repo = WatchRepository(db_path(home))
    repo.upsert(WatchItem(code=full_code, name=resolved_name, reason=reason, high=high, low=low, now=now))
    console.print(f"已加入观察池: {full_code} {resolved_name}")


@watch_app.command("list")
def watch_list(home: Path = typer.Option(default_home(), "--home")):
    repo = WatchRepository(db_path(home))
    rows = repo.list_active()
    table = Table("代码", "名称", "状态", "高点", "低点", "现价")
    for item in rows:
        table.add_row(item.code, item.name, item.status, f"{item.high:g}", f"{item.low:g}", f"{item.now:g}")
    console.print(table)


@watch_app.command("abandoned")
def watch_abandoned(home: Path = typer.Option(default_home(), "--home")):
    repo = WatchRepository(db_path(home))
    rows = repo.list_abandoned()
    table = Table("代码", "名称", "状态")
    for item in rows:
        table.add_row(item.code, item.name, item.status)
    console.print(table)


@watch_app.command("check")
def watch_check(home: Path = typer.Option(default_home(), "--home")):
    repo = WatchRepository(db_path(home))
    alerts = AlertRepository(db_path(home))
    table = Table("代码", "名称", "动作", "理由")
    today = date.today().isoformat()
    for item in repo.list_active():
        result = evaluate_watch(item)
        if result.action in ("watch", "abandon") and alerts.should_alert(item.code, result.title, result.price, 0.01):
            table.add_row(item.code, item.name, result.title, "; ".join(result.reasons))
            alerts.record(item.code, item.name, result.title, result.level, result.price, "; ".join(result.reasons), today)
            if result.action == "abandon":
                repo.mark_abandoned(item.code, "; ".join(result.reasons), today)
    console.print(table)


@watch_app.command("set")
def watch_set(
    code: str,
    home: Path = typer.Option(default_home(), "--home"),
    high: Optional[float] = typer.Option(None, "--high"),
    low: Optional[float] = typer.Option(None, "--low"),
):
    repo = WatchRepository(db_path(home))
    item = repo.get(code)
    if not item:
        raise typer.BadParameter(f"观察池不存在: {code}")
    if high is not None:
        item.high = high
    if low is not None:
        item.low = low
    repo.upsert(item)
    console.print(f"已更新观察池: {code}")


@hold_app.command("add")
def hold_add(
    code: str,
    home: Path = typer.Option(default_home(), "--home"),
    name: str = typer.Option("", "--name"),
    cost: float = typer.Option(..., "--cost"),
    qty: int = typer.Option(..., "--qty"),
    buy_date: str = typer.Option("", "--date"),
    high: float = typer.Option(0.0, "--high"),
    low: float = typer.Option(0.0, "--low"),
    swing_low: float = typer.Option(0.0, "--swing-low"),
    ref_high: float = typer.Option(0.0, "--ref-high"),
    rule: str = typer.Option("wolf_swing", "--rule"),
):
    watch_repo = WatchRepository(db_path(home))
    holding_repo = HoldingRepository(db_path(home))
    trade_repo = TradeRepository(db_path(home))

    full_code = format_code(code) or code
    watch_item = watch_repo.get(full_code)
    if watch_item:
        high = high or watch_item.high
        low = low or watch_item.low
        name = name or watch_item.name
        watch_repo.delete(full_code)
    resolved_name = _resolve_stock_name(full_code, name)

    h = Holding(
        code=full_code,
        name=resolved_name,
        cost=cost,
        quantity=qty,
        buy_date=buy_date or date.today().isoformat(),
        now=cost,
        highest=max(cost, high),
        high=high,
        low=low,
        swing_low=swing_low,
        ref_high=ref_high,
        rule_type=rule,  # type: ignore[arg-type]
    )
    holding_repo.upsert(h)
    trade_repo.record(full_code, resolved_name, "buy", cost, qty, h.buy_date)
    console.print(f"已加入持仓: {full_code} {resolved_name}")


@hold_app.command("list")
def hold_list(home: Path = typer.Option(default_home(), "--home")):
    repo = HoldingRepository(db_path(home))
    table = Table("代码", "名称", "成本", "数量", "规则")
    for h in repo.list_open():
        table.add_row(h.code, h.name, f"{h.cost:g}", str(h.quantity), h.rule_type)
    console.print(table)


@hold_app.command("add-buy")
def hold_add_buy(
    code: str,
    home: Path = typer.Option(default_home(), "--home"),
    price: float = typer.Option(..., "--price"),
    qty: int = typer.Option(..., "--qty"),
    trade_date: str = typer.Option("", "--date"),
):
    full_code = format_code(code) or code
    repo = HoldingRepository(db_path(home))
    trades = TradeRepository(db_path(home))
    h = repo.add_buy(full_code, price, qty)
    trades.record(full_code, h.name, "add_buy", price, qty, trade_date or date.today().isoformat())
    console.print(f"已加仓: {full_code} 新成本 {h.cost:g} 数量 {h.quantity}")


@hold_app.command("close")
def hold_close(
    code: str,
    home: Path = typer.Option(default_home(), "--home"),
    price: float = typer.Option(..., "--price"),
    reason: str = typer.Option("", "--reason"),
    trade_date: str = typer.Option("", "--date"),
    watch: bool = typer.Option(False, "--watch"),
):
    full_code = format_code(code) or code
    holdings = HoldingRepository(db_path(home))
    trades = TradeRepository(db_path(home))
    h = holdings.get(full_code)
    if not h:
        raise typer.BadParameter(f"持仓不存在: {full_code}")
    close_date = trade_date or date.today().isoformat()
    closed = holdings.close(full_code, price, close_date, reason)
    trades.record(full_code, h.name, "close", price, h.quantity, close_date, reason, closed.realized_pnl)
    if watch:
        WatchRepository(db_path(home)).upsert(WatchItem(code=full_code, name=h.name, reason=f"卖出后重新观察: {reason}", high=h.high, low=h.low, now=price))
    console.print(f"已关闭持仓: {full_code} 已实现盈亏 {closed.realized_pnl:g}")


@hold_app.command("check")
def hold_check(
    home: Path = typer.Option(default_home(), "--home"),
    today: str = typer.Option("", "--today"),
):
    repo = HoldingRepository(db_path(home))
    alerts = AlertRepository(db_path(home))
    table = Table("代码", "名称", "动作", "理由")
    today_text = today or date.today().isoformat()
    for h in repo.list_open():
        days = trading_days_since(h.buy_date, today_text) if h.buy_date else None
        result = evaluate_holding(h, trading_days_since_buy=days)
        reasons = "; ".join(result.reasons) if result.reasons else "暂无动作"
        if alerts.should_alert(h.code, result.title, result.price or h.now or h.cost, 0.01):
            table.add_row(h.code, h.name, result.title, reasons)
            alerts.record(h.code, h.name, result.title, result.level, result.price or h.now or h.cost, reasons, today_text)
    console.print(table)


@hold_app.command("set")
def hold_set(
    code: str,
    home: Path = typer.Option(default_home(), "--home"),
    highest: Optional[float] = typer.Option(None, "--highest"),
    swing_low: Optional[float] = typer.Option(None, "--swing-low"),
    ref_high: Optional[float] = typer.Option(None, "--ref-high"),
    rule: Optional[str] = typer.Option(None, "--rule"),
):
    full_code = format_code(code) or code
    repo = HoldingRepository(db_path(home))
    h = repo.get(full_code)
    if not h:
        raise typer.BadParameter(f"持仓不存在: {full_code}")
    if highest is not None:
        h.highest = highest
    if swing_low is not None:
        h.swing_low = swing_low
    if ref_high is not None:
        h.ref_high = ref_high
    if rule is not None:
        h.rule_type = rule  # type: ignore[assignment]
    repo.upsert(h)
    console.print(f"已更新持仓: {full_code}")
