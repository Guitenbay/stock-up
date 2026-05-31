from stock_up.db import init_db
from stock_up.market.mock import MockProvider
from stock_up.models import Holding, Quote, WatchItem
from stock_up.repositories import HoldingRepository, WatchRepository
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
