from stock_up.market.akshare_provider import AkShareProvider


class BrokenAk:
    def stock_zh_a_hist(self, **kwargs):
        raise RuntimeError("network failed")


def test_get_daily_bars_returns_empty_on_error():
    provider = AkShareProvider.__new__(AkShareProvider)
    provider.ak = BrokenAk()
    assert provider.get_daily_bars("sz300308", 30) == []
