from __future__ import annotations

from stock_up.market.akshare_provider import AkShareProvider
from stock_up.market.base import MarketDataProvider
from stock_up.market.mock import MockProvider
from stock_up.market.qq import TencentProvider
from stock_up.market.stockapi import StockApiProvider


def make_provider(name: str, purpose: str = "realtime") -> MarketDataProvider:
    if name == "mock":
        return MockProvider()
    if name == "qq":
        return TencentProvider()
    if name == "akshare":
        return AkShareProvider()
    if name == "stockapi":
        return StockApiProvider()
    if name == "auto":
        if purpose == "realtime":
            return TencentProvider()
        if purpose in ("daily", "rsi", "dragon_tiger"):
            return StockApiProvider()
        return AkShareProvider()
    raise ValueError(f"Unknown provider: {name}")
