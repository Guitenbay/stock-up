from stock_up.db import init_db
from stock_up.market.mock import MockProvider
from stock_up.models import HotBoard, HotLeader, Quote
from stock_up.repositories import WatchRepository
from stock_up.services.daily import run_daily


def test_daily_does_not_scan_hot_leaders_when_disabled(tmp_path):
    db_path = tmp_path / "data.db"
    report_dir = tmp_path / "reports"
    init_db(db_path)
    provider = MockProvider(
        hot_boards=[HotBoard(bk_code="801004", bk_name="锂电池", trade_date="2026-05-31")],
        hot_leaders={"801004": [HotLeader(code="002083", name="孚日股份", bk_code="801004", board_name="电解液", trade_date="2026-05-31")]},
        quotes={"sz002083": Quote(code="sz002083", name="孚日股份", now=10, high=11, low=9)},
    )
    summary = run_daily(db_path, provider, "2026-05-31", report_dir, enable_hot_leader_scan=False)
    assert summary.new_watch_count == 0
    assert WatchRepository(db_path).list_active() == []


def test_daily_scans_hot_leaders_when_enabled(tmp_path):
    db_path = tmp_path / "data.db"
    report_dir = tmp_path / "reports"
    init_db(db_path)
    provider = MockProvider(
        hot_boards=[HotBoard(bk_code="801004", bk_name="锂电池", trade_date="2026-05-31")],
        hot_leaders={"801004": [HotLeader(code="002083", name="孚日股份", bk_code="801004", board_name="电解液", trade_date="2026-05-31")]},
        quotes={"sz002083": Quote(code="sz002083", name="孚日股份", now=10, high=11, low=9)},
    )
    summary = run_daily(db_path, provider, "2026-05-31", report_dir, enable_hot_leader_scan=True)
    assert summary.new_watch_count == 1
