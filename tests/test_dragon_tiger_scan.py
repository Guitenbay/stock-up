from stock_up.db import init_db
from stock_up.models import DragonTigerStock, Quote
from stock_up.repositories import WatchRepository
from stock_up.services.dragon_tiger_scanner import run_dragon_tiger_scan


class DragonProvider:
    def get_dragon_tiger(self, trade_date):
        return [DragonTigerStock(code="000858", name="五粮液", trade_date=trade_date, reason="龙虎榜", close=84.89)]

    def get_realtime_quotes(self, codes):
        return [Quote(code="sz000858", name="五粮液", now=84.89, high=85.59, low=80.88, avg=83)]


class DuplicateDragonProvider:
    def get_dragon_tiger(self, trade_date):
        return [
            DragonTigerStock(code="000858", name="五粮液", trade_date=trade_date, reason="机构买入", close=84.89),
            DragonTigerStock(code="000858", name="五粮液", trade_date=trade_date, reason="深股通买入", close=84.89),
        ]

    def get_realtime_quotes(self, codes):
        assert codes == ["sz000858"]
        return [Quote(code="sz000858", name="五粮液", now=84.89, high=85.59, low=80.88, avg=83)]


def test_dragon_tiger_scan_adds_watch_item(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    summary = run_dragon_tiger_scan(db_path, DragonProvider(), "2026-05-29")
    assert summary.added_count == 1
    item = WatchRepository(db_path).get("sz000858")
    assert item is not None
    assert "龙虎榜" in item.reason


def test_dragon_tiger_scan_deduplicates_same_stock(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    summary = run_dragon_tiger_scan(db_path, DuplicateDragonProvider(), "2026-05-29")
    assert summary.total_count == 2
    assert summary.added_count == 1
    rows = WatchRepository(db_path).list_active()
    assert len(rows) == 1
    assert rows[0].code == "sz000858"
    assert "机构买入" in rows[0].reason
    assert "深股通买入" in rows[0].reason
