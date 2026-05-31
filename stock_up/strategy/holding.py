from stock_up.models import Holding, SignalResult


def _wolf_swing_reasons(h: Holding) -> list[SignalResult]:
    results: list[SignalResult] = []
    if h.cost > 0 and h.now <= h.cost * 0.93:
        results.append(SignalResult(
            action="stop_loss",
            title="触发 -7% 成本止损",
            reasons=[f"当前价 {h.now:.3f} <= 成本价 -7% {h.cost * 0.93:.3f}"],
            level="danger",
            price=h.now,
        ))
        return results

    if h.cost > 0 and h.highest >= h.cost * 1.2:
        take_profit_line = h.cost + (h.highest - h.cost) * 0.7
        if h.now <= take_profit_line:
            results.append(SignalResult(
                action="take_profit",
                title="触发利润回撤 30% 止盈",
                reasons=[f"当前价 {h.now:.3f} <= 止盈线 {take_profit_line:.3f}"],
                level="warning",
                price=h.now,
            ))
    return results


def _hai_long_reasons(h: Holding, trading_days_since_buy: int | None) -> list[SignalResult]:
    results: list[SignalResult] = []
    days = trading_days_since_buy
    if days is None:
        return results

    if days <= 13 and h.swing_low > 0 and h.now <= h.swing_low * 0.97:
        results.append(SignalResult(
            action="stop_loss",
            title="海指导规则失败：跌破波段低点 -3%",
            reasons=[f"当前价 {h.now:.3f} <= 防守线 {h.swing_low * 0.97:.3f}"],
            level="danger",
            price=h.now,
        ))

    if days > 13 and h.ref_high > 0 and h.highest < h.ref_high:
        results.append(SignalResult(
            action="stop_loss",
            title="海指导规则失败：超过 13 个交易日未创新高",
            reasons=[f"持仓 {days} 个交易日，最高 {h.highest:.3f} 未达到参考新高 {h.ref_high:.3f}"],
            level="danger",
            price=h.now,
        ))
    return results


def evaluate_holding(h: Holding, trading_days_since_buy: int | None = None) -> SignalResult:
    candidates: list[SignalResult] = []

    if h.rule_type in ("wolf_swing", "both"):
        candidates.extend(_wolf_swing_reasons(h))
    if h.rule_type in ("hai_long", "both"):
        candidates.extend(_hai_long_reasons(h, trading_days_since_buy))

    stop_losses = [r for r in candidates if r.action == "stop_loss"]
    if stop_losses:
        return SignalResult(
            action="stop_loss",
            title="建议止损/退出",
            reasons=[reason for r in stop_losses for reason in ([r.title] + r.reasons)],
            level="danger",
            price=h.now,
        )

    take_profits = [r for r in candidates if r.action == "take_profit"]
    if take_profits:
        return SignalResult(
            action="take_profit",
            title="建议止盈",
            reasons=[reason for r in take_profits for reason in ([r.title] + r.reasons)],
            level="warning",
            price=h.now,
        )

    return SignalResult(action="hold", title="持有", reasons=[], level="info", price=h.now)
