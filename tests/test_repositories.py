from stock_up.db import init_db
from stock_up.models import Holding, WatchItem
from stock_up.repositories import HoldingRepository, TradeRepository, WatchRepository


def test_watch_repository_upsert_and_list(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    repo = WatchRepository(db_path)
    repo.upsert(WatchItem(code="300308", name="中际旭创", high=130, low=110, now=120))

    items = repo.list_active()
    assert len(items) == 1
    assert items[0].code == "300308"

    repo.mark_abandoned("300308", reason="跌破 f786", date="2026-05-31")
    assert repo.list_active() == []
    assert repo.list_abandoned()[0].status == "abandoned"


def test_holding_repository_add_buy_close(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    holdings = HoldingRepository(db_path)
    trades = TradeRepository(db_path)

    holdings.upsert(Holding(code="300308", name="中际旭创", cost=100, quantity=100, now=100, highest=100))
    trades.record("300308", "中际旭创", "buy", price=100, quantity=100, trade_date="2026-05-31")

    updated = holdings.add_buy("300308", price=120, quantity=100)
    assert updated.cost == 110
    assert updated.quantity == 200

    closed = holdings.close("300308", close_price=130, close_date="2026-06-01", reason="止盈")
    assert closed.realized_pnl == 4000
    assert holdings.get("300308") is None

    rows = trades.list_by_date("2026-05-31")
    assert rows[0]["trade_type"] == "buy"
