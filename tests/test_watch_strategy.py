from stock_up.models import WatchItem
from stock_up.strategy.watch import evaluate_watch


def test_watch_abandon_below_f786():
    item = WatchItem(code="x", high=20, low=10, now=12)
    result = evaluate_watch(item)
    assert result.action == "abandon"


def test_watch_small_try_near_f382():
    item = WatchItem(code="x", high=20, low=10, now=16.5)
    result = evaluate_watch(item)
    assert result.action == "watch"
    assert "小仓" in result.title


def test_watch_strong_defense():
    item = WatchItem(code="x", high=20, low=10, now=14.0)
    result = evaluate_watch(item)
    assert result.action == "watch"
    assert "强防" in result.title


def test_watch_returns_data_insufficient_when_range_missing():
    item = WatchItem(code="x", high=0, low=0, now=12)
    result = evaluate_watch(item)
    assert result.action == "hold"
    assert result.title == "数据不足"


def test_watch_returns_data_insufficient_when_price_missing():
    item = WatchItem(code="x", high=20, low=10, now=0)
    result = evaluate_watch(item)
    assert result.action == "hold"
    assert result.title == "数据不足"


def test_watch_returns_data_insufficient_when_range_invalid():
    item = WatchItem(code="x", high=10, low=20, now=12)
    result = evaluate_watch(item)
    assert result.action == "hold"
    assert result.title == "数据不足"


def test_watch_all_day_limit_with_equal_high_low_is_observe():
    item = WatchItem(code="x", high=19.06, low=19.06, now=19.06)
    result = evaluate_watch(item)
    assert result.action == "hold"
    assert result.title == "一字板观望"
