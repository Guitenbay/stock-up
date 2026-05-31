from stock_up.market.factory import make_provider
from stock_up.market.mock import MockProvider
from stock_up.market.qq import TencentProvider
from stock_up.market.stockapi import StockApiProvider


def test_make_mock_provider():
    assert isinstance(make_provider("mock"), MockProvider)


def test_make_qq_provider():
    assert isinstance(make_provider("qq"), TencentProvider)


def test_make_realtime_auto_falls_back_to_qq_without_akshare():
    provider = make_provider("auto", purpose="realtime")
    assert isinstance(provider, TencentProvider)


def test_make_stockapi_provider():
    assert isinstance(make_provider("stockapi"), StockApiProvider)


def test_make_daily_auto_uses_stockapi():
    assert isinstance(make_provider("auto", purpose="daily"), StockApiProvider)
