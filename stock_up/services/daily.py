from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stock_up.market.base import MarketDataProvider
from stock_up.repositories import HoldingRepository, TradeRepository, WatchRepository
from stock_up.services.dragon_tiger_scanner import run_dragon_tiger_scan
from stock_up.services.hot_leader_scanner import run_hot_leader_scan
from stock_up.services.reporter import DailyReport, write_daily_report
from stock_up.services.rsi import latest_two_rsi, update_rsi_for_code
from stock_up.services.rsi_budget import plan_rsi_updates
from stock_up.services.scanner import run_limit_up_scan
from stock_up.services.tick import run_tick
from stock_up.strategy.holding import evaluate_holding
from stock_up.strategy.technical import detect_rsi_cross
from stock_up.strategy.trading_day import trading_days_since
from stock_up.strategy.watch import evaluate_watch


@dataclass(frozen=True)
class DailySummary:
    report_path: Path
    new_watch_count: int
    watch_action_count: int
    holding_action_count: int


def run_daily(
    db_path: Path,
    provider: MarketDataProvider,
    trade_date: str,
    report_dir: Path,
    rsi_max_updates: int = 50,
    enable_hot_leader_scan: bool = False,
    enable_dragon_tiger_scan: bool = True,
) -> DailySummary:
    hot_summary = run_hot_leader_scan(db_path, provider, trade_date) if enable_hot_leader_scan else None
    dragon_summary = run_dragon_tiger_scan(db_path, provider, trade_date) if enable_dragon_tiger_scan else None
    run_tick(db_path, provider)

    watch_repo = WatchRepository(db_path)
    holding_repo = HoldingRepository(db_path)
    trade_repo = TradeRepository(db_path)

    watch_actions: list[str] = []
    watch_items = watch_repo.list_active()
    holdings = holding_repo.list_open()
    rsi_codes = plan_rsi_updates(
        holding_codes=[h.code for h in holdings],
        watch_codes=[item.code for item in watch_items],
        max_updates=rsi_max_updates,
    )
    for code in rsi_codes:
        update_rsi_for_code(db_path, provider, code, cache_date=trade_date)

    for item in watch_items:
        result = evaluate_watch(item)
        if result.action in ("watch", "abandon"):
            watch_actions.append(f"{item.code} {item.name}: {result.title}；{'；'.join(result.reasons)}")
        rsi_pair = latest_two_rsi(db_path, item.code)
        if rsi_pair:
            prev, curr = rsi_pair
            if detect_rsi_cross(prev[0], prev[1], curr[0], curr[1]) == "golden":
                watch_actions.append(f"{item.code} {item.name}: 特别买点，RSI 金叉，可小仓试错")

    holding_actions: list[str] = []
    for h in holdings:
        days = trading_days_since(h.buy_date, trade_date) if h.buy_date else None
        result = evaluate_holding(h, trading_days_since_buy=days)
        if result.action in ("stop_loss", "take_profit"):
            holding_actions.append(f"{h.code} {h.name}: {result.title}；{'；'.join(result.reasons)}")
        rsi_pair = latest_two_rsi(db_path, h.code)
        if rsi_pair:
            prev, curr = rsi_pair
            if detect_rsi_cross(prev[0], prev[1], curr[0], curr[1]) == "dead":
                holding_actions.append(f"{h.code} {h.name}: 特别卖点，RSI 死叉，建议减仓/止盈观察")

    trades = []
    for row in trade_repo.list_by_date(trade_date):
        trades.append(f"{row['trade_type']} {row['code']} {row['quantity']}股 @{row['price']:g}")

    hot_added = hot_summary.added_count if hot_summary else 0
    dragon_added = dragon_summary.added_count if dragon_summary else 0
    added_count = hot_added + dragon_added
    new_watch = []
    if dragon_added:
        new_watch.append(f"新增 {dragon_added} 只龙虎榜观察")
    if hot_added:
        new_watch.append(f"新增 {hot_added} 只热点板块龙头观察")
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
        new_watch_count=added_count,
        watch_action_count=len(watch_actions),
        holding_action_count=len(holding_actions),
    )
