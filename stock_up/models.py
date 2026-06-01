from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


RuleType = Literal["wolf_swing", "hai_long", "both"]
Action = Literal["none", "hold", "add", "take_profit", "stop_loss", "watch", "abandon"]


@dataclass(frozen=True)
class FibLevels:
    f382: float
    f618: float
    f786: float


@dataclass
class Quote:
    code: str
    name: str = ""
    trade_date: str = ""
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    pre_close: float = 0.0
    now: float = 0.0
    amount: float = 0.0
    volume: float = 0.0
    avg: float = 0.0
    limit_up: float = 0.0
    limit_down: float = 0.0
    limit_status: str = ""


@dataclass
class DailyBar:
    code: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    amount: float = 0.0


@dataclass
class LimitUpStock:
    code: str
    name: str
    trade_date: str
    high: float
    low: float
    close: float
    amount: float = 0.0
    reason: str = ""
    board_count: int = 1


@dataclass(frozen=True)
class HotBoard:
    bk_code: str
    bk_name: str
    trade_date: str
    plate_id: str = ""
    qjzf: float = 0.0
    qjje: float = 0.0
    jlrts: int = 0
    qiangdu: float = 0.0


@dataclass(frozen=True)
class HotLeader:
    code: str
    name: str
    bk_code: str
    board_name: str
    trade_date: str
    qjzf: float = 0.0
    jlrts: int = 0


@dataclass(frozen=True)
class DragonTigerStock:
    code: str
    name: str
    trade_date: str
    reason: str = ""
    close: float = 0.0
    chg: float = 0.0
    turnover: float = 0.0
    buy_amount: float = 0.0
    sell_amount: float = 0.0
    top_amount: float = 0.0


@dataclass
class WatchItem:
    code: str
    name: str = ""
    reason: str = ""
    high: float = 0.0
    low: float = 0.0
    avg: float = 0.0
    now: float = 0.0
    limit_up: float = 0.0
    limit_down: float = 0.0
    limit_status: str = ""
    status: str = "watching"


@dataclass
class Holding:
    code: str
    name: str = ""
    cost: float = 0.0
    quantity: int = 0
    buy_date: str = ""
    now: float = 0.0
    highest: float = 0.0
    high: float = 0.0
    low: float = 0.0
    limit_up: float = 0.0
    limit_down: float = 0.0
    limit_status: str = ""
    swing_low: float = 0.0
    ref_high: float = 0.0
    rule_type: RuleType = "wolf_swing"


@dataclass
class SignalResult:
    action: Action
    title: str
    reasons: list[str] = field(default_factory=list)
    level: str = "info"
    price: float = 0.0
