from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from stock_up.config import write_default_config
from stock_up.db import init_db
from stock_up.market.akshare_provider import AkShareProvider
from stock_up.market.mock import MockProvider
from stock_up.market.qq import TencentProvider
from stock_up.models import Holding, WatchItem
from stock_up.services.scanner import run_limit_up_scan
from stock_up.services.tick import run_tick
from stock_up.repositories import AlertRepository, HoldingRepository, TradeRepository, WatchRepository
from stock_up.strategy.holding import evaluate_holding
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


@app.command()
def tick(
    home: Path = typer.Option(default_home(), "--home"),
    provider: str = typer.Option("qq", "--provider", help="qq / mock"),
):
    """执行一次盘中检查，由外部定时任务调用。"""
    market_provider = MockProvider() if provider == "mock" else TencentProvider()
    summary = run_tick(db_path(home), market_provider)
    console.print(f"tick完成: 观察 {summary.updated_watch_count}，持仓 {summary.updated_holding_count}")


@scan_app.command("limit-up")
def scan_limit_up(
    home: Path = typer.Option(default_home(), "--home"),
    provider: str = typer.Option("akshare", "--provider", help="akshare / mock"),
    trade_date: str = typer.Option("", "--date"),
):
    """扫描涨停池并加入观察池。"""
    date_text = trade_date or date.today().isoformat()
    if provider == "mock":
        market_provider = MockProvider(limit_up_pool=[])
    else:
        market_provider = AkShareProvider()
    summary = run_limit_up_scan(db_path(home), market_provider, date_text)
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
    repo = WatchRepository(db_path(home))
    repo.upsert(WatchItem(code=code, name=name or code, reason=reason, high=high, low=low, now=now))
    console.print(f"已加入观察池: {code} {name or code}")


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

    watch_item = watch_repo.get(code)
    if watch_item:
        high = high or watch_item.high
        low = low or watch_item.low
        name = name or watch_item.name
        watch_repo.delete(code)

    h = Holding(
        code=code,
        name=name or code,
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
    trade_repo.record(code, name or code, "buy", cost, qty, h.buy_date)
    console.print(f"已加入持仓: {code} {name or code}")


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
    repo = HoldingRepository(db_path(home))
    trades = TradeRepository(db_path(home))
    h = repo.add_buy(code, price, qty)
    trades.record(code, h.name, "add_buy", price, qty, trade_date or date.today().isoformat())
    console.print(f"已加仓: {code} 新成本 {h.cost:g} 数量 {h.quantity}")


@hold_app.command("close")
def hold_close(
    code: str,
    home: Path = typer.Option(default_home(), "--home"),
    price: float = typer.Option(..., "--price"),
    reason: str = typer.Option("", "--reason"),
    trade_date: str = typer.Option("", "--date"),
    watch: bool = typer.Option(False, "--watch"),
):
    holdings = HoldingRepository(db_path(home))
    trades = TradeRepository(db_path(home))
    h = holdings.get(code)
    if not h:
        raise typer.BadParameter(f"持仓不存在: {code}")
    close_date = trade_date or date.today().isoformat()
    closed = holdings.close(code, price, close_date, reason)
    trades.record(code, h.name, "close", price, h.quantity, close_date, reason, closed.realized_pnl)
    if watch:
        WatchRepository(db_path(home)).upsert(WatchItem(code=code, name=h.name, reason=f"卖出后重新观察: {reason}", high=h.high, low=h.low, now=price))
    console.print(f"已关闭持仓: {code} 已实现盈亏 {closed.realized_pnl:g}")


@hold_app.command("check")
def hold_check(home: Path = typer.Option(default_home(), "--home")):
    repo = HoldingRepository(db_path(home))
    alerts = AlertRepository(db_path(home))
    table = Table("代码", "名称", "动作", "理由")
    today = date.today().isoformat()
    for h in repo.list_open():
        result = evaluate_holding(h, trading_days_since_buy=None)
        reasons = "; ".join(result.reasons) if result.reasons else "暂无动作"
        if alerts.should_alert(h.code, result.title, result.price or h.now or h.cost, 0.01):
            table.add_row(h.code, h.name, result.title, reasons)
            alerts.record(h.code, h.name, result.title, result.level, result.price or h.now or h.cost, reasons, today)
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
    repo = HoldingRepository(db_path(home))
    h = repo.get(code)
    if not h:
        raise typer.BadParameter(f"持仓不存在: {code}")
    if highest is not None:
        h.highest = highest
    if swing_low is not None:
        h.swing_low = swing_low
    if ref_high is not None:
        h.ref_high = ref_high
    if rule is not None:
        h.rule_type = rule  # type: ignore[assignment]
    repo.upsert(h)
    console.print(f"已更新持仓: {code}")
