from stock_up.db import init_db
from stock_up.market.mock import MockProvider
from stock_up.models import Holding, Quote, WatchItem
from stock_up.repositories import HoldingRepository, WatchRepository
from stock_up.strategy.fib import calculate_fib_levels
from stock_up.services.tick import run_tick


def test_tick_updates_watch_and_holding_quotes(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    WatchRepository(db_path).upsert(WatchItem(code="300308", name="中际旭创", high=120, low=100, now=110))
    HoldingRepository(db_path).upsert(Holding(code="600000", name="浦发银行", cost=10, quantity=100, now=10, highest=10, high=11, low=9))

    provider = MockProvider(quotes={
        "300308": Quote(code="300308", name="中际旭创", now=125, high=126, low=119, pre_close=118, avg=122),
        "600000": Quote(code="600000", name="浦发银行", now=12, high=12.5, low=11.8, pre_close=11, avg=12.1),
    })

    summary = run_tick(db_path, provider)

    watch = WatchRepository(db_path).get("300308")
    holding = HoldingRepository(db_path).get("600000")
    assert watch.now == 125
    assert watch.high == 125
    assert watch.avg == 122
    assert holding.now == 12
    assert holding.highest == 12.5
    assert summary.updated_watch_count == 1
    assert summary.updated_holding_count == 1


def test_tick_returns_watch_buy_signal(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    low = 100
    high = 130
    levels = calculate_fib_levels(high, low)
    WatchRepository(db_path).upsert(WatchItem(code="300308", name="中际旭创", high=high, low=low, now=120))
    provider = MockProvider(quotes={
        "300308": Quote(code="300308", name="中际旭创", now=levels.f382, high=high, low=levels.f382, avg=levels.f382),
    })

    summary = run_tick(db_path, provider, trade_date="2026-05-31")

    assert len(summary.watch_signals) == 1
    assert summary.watch_signals[0].code == "300308"
    assert summary.watch_signals[0].title == "可小仓试错"


def test_tick_returns_holding_stop_loss_signal(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    HoldingRepository(db_path).upsert(Holding(code="600000", name="浦发银行", cost=10, quantity=100, now=10, highest=10, high=11, low=9))
    provider = MockProvider(quotes={
        "600000": Quote(code="600000", name="浦发银行", now=9.2, high=9.3, low=9.1, avg=9.2),
    })

    summary = run_tick(db_path, provider, trade_date="2026-05-31")

    assert len(summary.holding_signals) == 1
    assert summary.holding_signals[0].code == "600000"
    assert summary.holding_signals[0].title == "建议止损/退出"


def test_tick_suppresses_repeated_signal_within_price_threshold(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    HoldingRepository(db_path).upsert(Holding(code="600000", name="浦发银行", cost=10, quantity=100, now=10, highest=10, high=11, low=9))
    provider = MockProvider(quotes={
        "600000": Quote(code="600000", name="浦发银行", now=9.2, high=9.3, low=9.1, avg=9.2),
    })

    first = run_tick(db_path, provider, trade_date="2026-05-31")
    second = run_tick(db_path, provider, trade_date="2026-05-31")

    assert len(first.holding_signals) == 1
    assert second.holding_signals == []
