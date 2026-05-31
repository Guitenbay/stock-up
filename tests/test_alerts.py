from stock_up.db import init_db
from stock_up.repositories import AlertRepository


def test_alert_dedupe_by_price_change(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    repo = AlertRepository(db_path)

    assert repo.should_alert("300308", "buy", 100, threshold=0.01)
    repo.record("300308", "中际旭创", "buy", "info", 100, "msg", "2026-05-31")
    assert not repo.should_alert("300308", "buy", 100.5, threshold=0.01)
    assert repo.should_alert("300308", "buy", 101.1, threshold=0.01)
