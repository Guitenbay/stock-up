from stock_up.models import Holding
from stock_up.strategy.holding import evaluate_holding


def test_wolf_swing_triggers_stop_loss():
    h = Holding(code="300308", name="x", cost=100, quantity=100, now=92, highest=110, rule_type="wolf_swing")
    result = evaluate_holding(h, trading_days_since_buy=5)
    assert result.action == "stop_loss"
    assert "-7%" in result.reasons[0]


def test_wolf_swing_triggers_take_profit_after_drawdown():
    h = Holding(code="300308", name="x", cost=100, quantity=100, now=113, highest=120, rule_type="wolf_swing")
    result = evaluate_holding(h, trading_days_since_buy=5)
    assert result.action == "take_profit"


def test_hai_long_triggers_timeout_exit():
    h = Holding(code="300308", name="x", cost=100, quantity=100, now=105, highest=108, ref_high=110, swing_low=95, rule_type="hai_long")
    result = evaluate_holding(h, trading_days_since_buy=14)
    assert result.action == "stop_loss"
    assert "未创新高" in "".join(result.reasons)


def test_both_collects_reasons():
    h = Holding(code="300308", name="x", cost=100, quantity=100, now=92, highest=108, ref_high=110, swing_low=95, rule_type="both")
    result = evaluate_holding(h, trading_days_since_buy=14)
    assert result.action == "stop_loss"
    assert len(result.reasons) >= 2
