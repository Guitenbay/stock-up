from stock_up.db import init_db
from stock_up.models import HotBoard, HotLeader, Quote
from stock_up.repositories import WatchRepository
from stock_up.services.hot_leader_scanner import run_hot_leader_scan


class HotProvider:
    def get_hot_boards(self, trade_date):
        return [HotBoard(bk_code="801004", bk_name="锂电池", trade_date=trade_date, qiangdu=100)]

    def get_hot_leaders(self, trade_date, plate_id):
        return [HotLeader(code="002083", name="孚日股份", bk_code=plate_id, board_name="电解液", trade_date=trade_date, qjzf=61.23)]

    def get_realtime_quotes(self, codes):
        return [Quote(code="sz002083", name="孚日股份", now=10, high=11, low=9, avg=10)]


def test_hot_leader_scan_adds_leaders_to_watch(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    summary = run_hot_leader_scan(db_path, HotProvider(), trade_date="2025-11-14")
    assert summary.added_count == 1
    item = WatchRepository(db_path).get("sz002083")
    assert item is not None
    assert "热点板块" in item.reason
