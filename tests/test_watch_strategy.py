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
