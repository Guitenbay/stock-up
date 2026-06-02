from stock_up.models import SignalResult, WatchItem
from stock_up.strategy.fib import calculate_fib_levels


def evaluate_watch(item: WatchItem, buy_382_tolerance: float = 0.03, buy_618_tolerance: float = 0.02) -> SignalResult:
    now = item.now
    if item.high <= 0 or item.low <= 0 or item.high < item.low or now <= 0:
        return SignalResult(
            action="hold",
            title="数据不足",
            reasons=["缺少有效高点、低点或当前价，无法计算观察信号"],
            level="info",
            price=now,
        )

    if item.limit_status == "涨停":
        return SignalResult(
            action="hold",
            title="涨停观望",
            reasons=["当前涨停，走势较强，不移入废弃"],
            level="info",
            price=now,
        )

    levels = calculate_fib_levels(item.high, item.low)

    if now <= levels.f786 or now <= item.low:
        return SignalResult(
            action="abandon",
            title="放弃/移入废弃",
            reasons=[f"当前价 {now:.3f} 触及/跌破 f786 {levels.f786:.3f} 或阶段低点 {item.low:.3f}"],
            level="danger",
            price=now,
        )

    if item.high == item.low == now:
        return SignalResult(
            action="hold",
            title="一字板观望",
            reasons=["高点、低点、现价相同，可能为全程涨停/跌停，暂不按回撤买点判断"],
            level="info",
            price=now,
        )

    if now <= levels.f618 * (1 + buy_618_tolerance):
        return SignalResult(
            action="watch",
            title="谨慎小仓，仅强防试错",
            reasons=[f"当前价 {now:.3f} 接近 0.618 强防线 {levels.f618:.3f}"],
            level="warning",
            price=now,
        )

    if now <= levels.f382 * (1 + buy_382_tolerance) and now > levels.f618:
        return SignalResult(
            action="watch",
            title="可小仓试错",
            reasons=[f"当前价 {now:.3f} 接近 0.382 常规买点 {levels.f382:.3f}"],
            level="info",
            price=now,
        )

    return SignalResult(
        action="hold",
        title="谨慎观察，不追",
        reasons=["尚未到策略买点"],
        level="info",
        price=now,
    )
