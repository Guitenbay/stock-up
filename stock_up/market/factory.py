from __future__ import annotations

from stock_up.market.akshare_provider import AkShareProvider
from stock_up.market.base import MarketDataProvider
from stock_up.market.mock import MockProvider
from stock_up.market.qq import TencentProvider


def make_provider(name: str, purpose: str = "realtime") -> MarketDataProvider:
    if name == "mock":
        return MockProvider()
    if name == "qq":
        return TencentProvider()
    if name == "akshare":
        return AkShareProvider()
    if name == "auto":
        if purpose == "realtime":
            return TencentProvider()
        return AkShareProvider()
    raise ValueError(f"Unknown provider: {name}")
