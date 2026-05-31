from stock_up.market.mock import MockProvider
from stock_up.models import Quote


def test_mock_provider_returns_quotes():
    provider = MockProvider(quotes={"300308": Quote(code="300308", name="中际旭创", now=121, high=123, low=118)})
    quotes = provider.get_realtime_quotes(["300308", "600000"])
    assert len(quotes) == 1
    assert quotes[0].now == 121
