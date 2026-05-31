from __future__ import annotations

import re
import urllib.parse
import urllib.request
from datetime import date

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


def parse_daily_js(code: str, text: str) -> list[DailyBar]:
    match = re.search(r'="([\s\S]*?)";', text)
    if not match:
        return []
    rows: list[DailyBar] = []
    payload = match.group(1).replace("\\\n", "\n").replace("\\", "")
    for raw_line in payload.splitlines():
        parts = raw_line.strip().split()
        if len(parts) < 6:
            continue
        day = parts[0]
        if len(day) == 6:
            trade_date = f"20{day[:2]}-{day[2:4]}-{day[4:6]}"
        elif len(day) == 8:
            trade_date = f"{day[:4]}-{day[4:6]}-{day[6:8]}"
        else:
            continue
        rows.append(DailyBar(
            code=code,
            trade_date=trade_date,
            open=_to_float(parts[1]),
            close=_to_float(parts[2]),
            high=_to_float(parts[3]),
            low=_to_float(parts[4]),
            volume=_to_float(parts[5]),
            amount=_to_float(parts[6]) if len(parts) > 6 else 0.0,
        ))
    return rows


def _daily_year_suffixes(days: int) -> list[str]:
    current = date.today().year
    # Request enough recent yearly files for the desired window.
    years = max(1, min(5, days // 220 + 2))
    return [str(y)[-2:] for y in range(current - years + 1, current + 1)]


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
        all_rows: list[DailyBar] = []
        for yy in _daily_year_suffixes(days):
            url = f"http://data.gtimg.cn/flashdata/hushen/daily/{yy}/{code}.js"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    text = resp.read().decode("gbk", errors="ignore")
            except Exception:
                continue
            all_rows.extend(parse_daily_js(code, text))
        all_rows.sort(key=lambda bar: bar.trade_date)
        return all_rows[-days:]

    def get_limit_up_pool(self, trade_date: str) -> list[LimitUpStock]:
        return []

    def get_trade_calendar(self) -> list[str]:
        return []
