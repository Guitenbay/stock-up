from stock_up.db import init_db
from stock_up.market.mock import MockProvider
from stock_up.models import Holding, LimitUpStock, Quote
from stock_up.repositories import HoldingRepository
from stock_up.services.daily import run_daily


def test_run_daily_creates_report(tmp_path):
    db_path = tmp_path / "data.db"
    report_dir = tmp_path / "reports"
    init_db(db_path)
    HoldingRepository(db_path).upsert(Holding(code="600000", name="浦发银行", cost=10, quantity=100, now=10, highest=10, rule_type="wolf_swing"))
    provider = MockProvider(
        limit_up_pool=[LimitUpStock(code="300308", name="中际旭创", trade_date="2026-05-31", high=120, low=110, close=120, amount=600_000_000)],
        quotes={"300308": Quote(code="300308", name="中际旭创", now=118, high=120, low=110), "600000": Quote(code="600000", name="浦发银行", now=9, high=9.5, low=8.8)},
    )
    summary = run_daily(db_path, provider, trade_date="2026-05-31", report_dir=report_dir)
    assert summary.report_path.exists()
    assert "stock-up 每日报告" in summary.report_path.read_text(encoding="utf-8")
