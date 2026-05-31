from stock_up.db import init_db
from stock_up.market.mock import MockProvider
from stock_up.models import LimitUpStock
from stock_up.repositories import WatchRepository
from stock_up.services.scanner import run_limit_up_scan


def test_limit_up_scan_adds_filtered_watch_items(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    provider = MockProvider(limit_up_pool=[
        LimitUpStock(code="300308", name="中际旭创", trade_date="2026-05-31", high=120, low=110, close=120, amount=600_000_000, reason="AI"),
        LimitUpStock(code="600001", name="ST测试", trade_date="2026-05-31", high=10, low=9, close=10, amount=800_000_000),
        LimitUpStock(code="830001", name="北交测试", trade_date="2026-05-31", high=10, low=9, close=10, amount=800_000_000),
        LimitUpStock(code="002001", name="低额测试", trade_date="2026-05-31", high=10, low=9, close=10, amount=100_000_000),
    ])

    summary = run_limit_up_scan(db_path, provider, trade_date="2026-05-31")

    assert summary.added_count == 1
    items = WatchRepository(db_path).list_active()
    assert len(items) == 1
    assert items[0].code == "300308"
    assert items[0].high == 120
    assert items[0].low == 110
