from __future__ import annotations

from stock_up.models import DailyBar, LimitUpStock, Quote


class AkShareProvider:
    """AkShare data provider.

    AkShare is an optional dependency. Import lazily so the CLI remains usable
    without installing it when users only need Tencent realtime quotes.
    """

    def __init__(self):
        try:
            import akshare as ak  # type: ignore
        except ImportError as exc:
            raise RuntimeError("AkShare 未安装，请执行: pip install 'stock-up[akshare]'") from exc
        self.ak = ak

    def get_realtime_quotes(self, codes: list[str]) -> list[Quote]:
        # MVP uses Tencent for realtime by default; keep this conservative.
        return []

    def get_daily_bars(self, code: str, days: int) -> list[DailyBar]:
        symbol = code.replace("sh", "").replace("sz", "").replace("bj", "")
        df = self.ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="")
        rows = []
        for _, row in df.tail(days).iterrows():
            rows.append(DailyBar(
                code=code,
                trade_date=str(row.get("日期", "")),
                open=float(row.get("开盘", 0) or 0),
                high=float(row.get("最高", 0) or 0),
                low=float(row.get("最低", 0) or 0),
                close=float(row.get("收盘", 0) or 0),
                volume=float(row.get("成交量", 0) or 0),
                amount=float(row.get("成交额", 0) or 0),
            ))
        return rows

    def get_limit_up_pool(self, trade_date: str) -> list[LimitUpStock]:
        date_text = trade_date.replace("-", "")
        df = self.ak.stock_zt_pool_em(date=date_text)
        items: list[LimitUpStock] = []
        for _, row in df.iterrows():
            code = str(row.get("代码", ""))
            name = str(row.get("名称", ""))
            items.append(LimitUpStock(
                code=code,
                name=name,
                trade_date=trade_date,
                high=float(row.get("最新价", 0) or 0),
                low=float(row.get("最新价", 0) or 0),
                close=float(row.get("最新价", 0) or 0),
                amount=float(row.get("成交额", 0) or 0),
                reason=str(row.get("涨停原因类别", "") or ""),
                board_count=int(row.get("连板数", 1) or 1),
            ))
        return items

    def get_trade_calendar(self) -> list[str]:
        try:
            df = self.ak.tool_trade_date_hist_sina()
        except Exception:
            return []
        return [str(v) for v in df.get("trade_date", []).tolist()]
