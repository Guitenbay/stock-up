from stock_up.services.rsi_budget import plan_rsi_updates


def test_plan_rsi_updates_prioritizes_holdings():
    planned = plan_rsi_updates(
        holding_codes=["h1", "h2"],
        watch_codes=["w1", "h1", "w2"],
        max_updates=3,
    )
    assert planned == ["h1", "h2", "w1"]


def test_plan_rsi_updates_stops_when_budget_reached():
    planned = plan_rsi_updates(
        holding_codes=["h1", "h2"],
        watch_codes=["w1"],
        max_updates=1,
    )
    assert planned == ["h1"]
