from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DailyReport:
    trade_date: str
    new_watch: list[str] = field(default_factory=list)
    watch_actions: list[str] = field(default_factory=list)
    holding_actions: list[str] = field(default_factory=list)
    trades: list[str] = field(default_factory=list)


def _section(title: str, rows: list[str]) -> str:
    if not rows:
        return f"## {title}\n\n无。\n"
    body = "\n".join(f"- {row}" for row in rows)
    return f"## {title}\n\n{body}\n"


def render_daily_report(report: DailyReport) -> str:
    parts = [
        f"# stock-up 每日报告 {report.trade_date}\n",
        _section("新增观察", report.new_watch),
        _section("观察动作", report.watch_actions),
        _section("持仓动作", report.holding_actions),
        _section("今日交易", report.trades),
        "## 免责声明\n\n本工具仅用于个人复盘和策略辅助，不构成投资建议。\n",
    ]
    return "\n".join(parts)


def write_daily_report(report: DailyReport, report_dir: Path) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{report.trade_date}.md"
    path.write_text(render_daily_report(report), encoding="utf-8")
    return path
