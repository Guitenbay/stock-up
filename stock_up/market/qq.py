from __future__ import annotations

import urllib.parse
import urllib.request

from stock_up.models import DailyBar, LimitUpStock, Quote


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_qt_line(line: str) -> Quote | None:
    line = line.strip().rstrip(";")
    if not line.startswith("v_") or "=" not in line:
        return None
    key, value = line.split("=", 1)
    code = key[2:]
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    fields = value.split("~")
    if len(fields) < 38:
        return None

    name = fields[1]
    now = _to_float(fields[3])
    pre_close = _to_float(fields[4])
    high = _to_float(fields[33], now)
    low = _to_float(fields[34], now)
    volume = _to_float(fields[36])
    amount = _to_float(fields[37])
    avg = _calc_avg(code, pre_close, now, volume, amount)

    return Quote(
        code=code,
        name=name,
        now=round(now, 3),
        pre_close=round(pre_close, 3),
        high=round(high, 3),
        low=round(low, 3),
        close=round(pre_close, 3),
        volume=volume,
        amount=amount,
        avg=round(avg, 3),
    )


def _calc_avg(code: str, pre_close: float, now: float, volume: float, amount: float) -> float:
    if volume <= 0:
        return pre_close or now
    if code.startswith("hk"):
        return amount / volume
    avg_hand = (amount * 10000) / (volume * 100)
    avg_share = (amount * 10000) / volume
    if now > 0 and avg_hand > 0 and (now / avg_hand) >= 10:
        return avg_share
    if now > 0:
        return avg_hand if abs(avg_hand - now) <= abs(avg_share - now) else avg_share
    return avg_hand


class TencentProvider:
    def get_realtime_quotes(self, codes: list[str]) -> list[Quote]:
        clean = [c.strip().lower() for c in codes if c and c.strip()]
        if not clean:
            return []
        url = "https://qt.gtimg.cn/q=" + urllib.parse.quote(",".join(clean))
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("gbk", errors="ignore")
        quotes = []
        for line in text.splitlines():
            q = parse_qt_line(line)
            if q:
                quotes.append(q)
        return quotes

    def get_daily_bars(self, code: str, days: int) -> list[DailyBar]:
        return []

    def get_limit_up_pool(self, trade_date: str) -> list[LimitUpStock]:
        return []

    def get_trade_calendar(self) -> list[str]:
        return []
