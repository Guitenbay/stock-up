from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stock_up.market.base import MarketDataProvider
from stock_up.repositories import HoldingRepository, TradeRepository, WatchRepository
from stock_up.services.reporter import DailyReport, write_daily_report
from stock_up.services.scanner import run_limit_up_scan
from stock_up.services.tick import run_tick
from stock_up.strategy.holding import evaluate_holding
from stock_up.strategy.watch import evaluate_watch


@dataclass(frozen=True)
class DailySummary:
    report_path: Path
    new_watch_count: int
    watch_action_count: int
    holding_action_count: int


def run_daily(db_path: Path, provider: MarketDataProvider, trade_date: str, report_dir: Path) -> DailySummary:
    scan_summary = run_limit_up_scan(db_path, provider, trade_date)
    run_tick(db_path, provider)

    watch_repo = WatchRepository(db_path)
    holding_repo = HoldingRepository(db_path)
    trade_repo = TradeRepository(db_path)

    watch_actions: list[str] = []
    for item in watch_repo.list_active():
        result = evaluate_watch(item)
        if result.action in ("watch", "abandon"):
            watch_actions.append(f"{item.code} {item.name}: {result.title}；{'；'.join(result.reasons)}")

    holding_actions: list[str] = []
    for h in holding_repo.list_open():
        result = evaluate_holding(h, trading_days_since_buy=None)
        if result.action in ("stop_loss", "take_profit"):
            holding_actions.append(f"{h.code} {h.name}: {result.title}；{'；'.join(result.reasons)}")

    trades = []
    for row in trade_repo.list_by_date(trade_date):
        trades.append(f"{row['trade_type']} {row['code']} {row['quantity']}股 @{row['price']:g}")

    new_watch = [f"新增 {scan_summary.added_count} 只涨停观察"] if scan_summary.added_count else []
    report = DailyReport(
        trade_date=trade_date,
        new_watch=new_watch,
        watch_actions=watch_actions,
        holding_actions=holding_actions,
        trades=trades,
    )
    report_path = write_daily_report(report, report_dir)
    return DailySummary(
        report_path=report_path,
        new_watch_count=scan_summary.added_count,
        watch_action_count=len(watch_actions),
        holding_action_count=len(holding_actions),
    )
