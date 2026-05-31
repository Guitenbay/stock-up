from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class MarketConfig(BaseModel):
    quote_source: Literal["akshare", "qq"] = "akshare"
    limit_up_source_order: list[str] = Field(default_factory=lambda: ["akshare_em", "akshare_ths"])
    realtime_fallback_order: list[str] = Field(default_factory=lambda: ["akshare", "qq"])


class TickConfig(BaseModel):
    trading_time_only: bool = True
    min_interval_seconds: int = 20


class LimitUpConfig(BaseModel):
    exclude_st: bool = True
    exclude_bj: bool = True
    exclude_new_stock_days: int = 30
    min_amount: float = 500_000_000
    include_first_board: bool = True
    include_multi_board: bool = True


class WatchConfig(BaseModel):
    initial_low_mode: Literal["same_day", "recent_1d"] = "same_day"
    buy_382_tolerance: float = 0.03
    buy_618_tolerance: float = 0.02
    abandon_below_786: bool = True
    abandon_below_low: bool = True


class RsiConfig(BaseModel):
    enabled: bool = True
    short_period: int = 6
    long_period: int = 12
    min_history_days: int = 30
    max_updates_per_daily: int = 50
    watch_golden_cross: bool = True
    holding_dead_cross: bool = True


class TechnicalConfig(BaseModel):
    rsi: RsiConfig = Field(default_factory=RsiConfig)


class WolfSwingConfig(BaseModel):
    stop_loss_pct: float = 0.07
    take_profit_arm_pct: float = 0.20
    profit_drawdown_pct: float = 0.30


class HaiLongConfig(BaseModel):
    swing_low_break_pct: float = 0.03
    validate_days: int = 13


class HoldingRulesConfig(BaseModel):
    wolf_swing: WolfSwingConfig = Field(default_factory=WolfSwingConfig)
    hai_long: HaiLongConfig = Field(default_factory=HaiLongConfig)


class HoldingConfig(BaseModel):
    default_rule: Literal["wolf_swing", "hai_long", "both"] = "wolf_swing"
    rules: HoldingRulesConfig = Field(default_factory=HoldingRulesConfig)
    allow_loss_add_on_618: bool = True


class AlertConfig(BaseModel):
    repeat_price_change_pct: float = 0.01


class NotifyConfig(BaseModel):
    terminal: bool = True
    markdown_report: bool = True


class ReportConfig(BaseModel):
    only_actionable: bool = True
    dir: str = "~/.stock-up/reports"


class AppConfig(BaseModel):
    market: MarketConfig = Field(default_factory=MarketConfig)
    tick: TickConfig = Field(default_factory=TickConfig)
    limit_up: LimitUpConfig = Field(default_factory=LimitUpConfig)
    watch: WatchConfig = Field(default_factory=WatchConfig)
    technical: TechnicalConfig = Field(default_factory=TechnicalConfig)
    holding: HoldingConfig = Field(default_factory=HoldingConfig)
    alert: AlertConfig = Field(default_factory=AlertConfig)
    notify: NotifyConfig = Field(default_factory=NotifyConfig)
    report: ReportConfig = Field(default_factory=ReportConfig)


def default_config_dict() -> dict:
    return AppConfig().model_dump(mode="json")


def write_default_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(default_config_dict(), allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        return AppConfig()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(data)
