from __future__ import annotations

import json
from datetime import date, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from stock_up.models import DailyBar, HotBoard, HotLeader, LimitUpStock, Quote


BASE_URL = "https://www.stockapi.com.cn/v1/base/day"
RSI_URL = "https://www.stockapi.com.cn/v1/quota/rsi2"
HOT_BOARD_URL = "https://www.stockapi.com.cn/v1/hotBkJlrDr"
HOT_LEADER_URL = "https://www.stockapi.com.cn/v1/hotBkJlrLongTou"


def build_date_windows(start: date, end: date, max_days: int = 5) -> list[tuple[str, str]]:
    windows: list[tuple[str, str]] = []
    cur = start
    while cur <= end:
        window_end = min(cur + timedelta(days=max_days - 1), end)
        windows.append((cur.isoformat(), window_end.isoformat()))
        cur = window_end + timedelta(days=1)
    return windows


def strip_market_prefix(code: str) -> str:
    value = str(code or "").strip().lower()
    for prefix in ("sh", "sz", "bj"):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_hot_boards(payload: dict) -> list[HotBoard]:
    if payload.get("code") != 20000:
        return []
    data = payload.get("data") or []
    if not isinstance(data, list):
        return []
    rows: list[HotBoard] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        rows.append(HotBoard(
            bk_code=str(item.get("bkCode", "")),
            bk_name=str(item.get("bkName", "")),
            trade_date=str(item.get("time", "")),
            plate_id=str(item.get("id", "") or item.get("plateId", "") or item.get("bkCode", "")),
            qjzf=_to_float(item.get("qjzf")),
            qjje=_to_float(item.get("qjje")),
            jlrts=_to_int(item.get("jlrts")),
            qiangdu=_to_float(item.get("qiangdu")),
        ))
    return [row for row in rows if row.bk_code]


def parse_hot_leaders(payload: dict) -> list[HotLeader]:
    if payload.get("code") != 20000:
        return []
    data = payload.get("data") or []
    if not isinstance(data, list):
        return []
    rows: list[HotLeader] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        rows.append(HotLeader(
            code=str(item.get("code", "")),
            name=str(item.get("name", "")),
            bk_code=str(item.get("bkCode", "")),
            board_name=str(item.get("bk", "")),
            trade_date=str(item.get("time", "")),
            qjzf=_to_float(item.get("qjzf")),
            jlrts=_to_int(item.get("jlrts")),
        ))
    return [row for row in rows if row.code]


def parse_stockapi_rsi(payload: dict) -> list[tuple[str, float, float]]:
    if payload.get("code") != 20000:
        return []
    data = payload.get("data") or []
    if isinstance(data, list):
        return _parse_stockapi_rsi_row_list(data)
    if isinstance(data, dict):
        return _parse_stockapi_rsi_array_object(data)
    return []


def _parse_stockapi_rsi_row_list(data: list) -> list[tuple[str, float, float]]:
    rows: list[tuple[str, float, float]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            rows.append((str(item["date"]), float(item["rsi1"]), float(item["rsi2"])))
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def _parse_stockapi_rsi_array_object(data: dict) -> list[tuple[str, float, float]]:
    dates = data.get("date") or []
    rsi1 = data.get("rsi1") or []
    rsi2 = data.get("rsi2") or []
    rows: list[tuple[str, float, float]] = []
    for idx, trade_date in enumerate(dates):
        try:
            rows.append((str(trade_date), float(rsi1[idx]), float(rsi2[idx])))
        except (IndexError, TypeError, ValueError):
            continue
    return rows


def parse_stockapi_daily(code: str, payload: dict) -> list[DailyBar]:
    if payload.get("code") != 20000:
        return []
    data = payload.get("data") or {}
    if isinstance(data, list):
        return _parse_stockapi_row_list(code, data)
    if not isinstance(data, dict):
        return []

    dates = data.get("date") or data.get("dates") or data.get("tradeDate") or data.get("trade_date")
    if not dates:
        return []

    opens = data.get("open") or []
    highs = data.get("high") or []
    lows = data.get("low") or []
    closes = data.get("close") or []
    volumes = data.get("volume") or []
    amounts = data.get("amount") or data.get("transactionAmount") or []

    rows: list[DailyBar] = []
    for idx, trade_date in enumerate(dates):
        try:
            rows.append(DailyBar(
                code=code,
                trade_date=str(trade_date),
                open=float(opens[idx]),
                high=float(highs[idx]),
                low=float(lows[idx]),
                close=float(closes[idx]),
                volume=float(volumes[idx]) if idx < len(volumes) else 0.0,
                amount=float(amounts[idx]) if idx < len(amounts) else 0.0,
            ))
        except (IndexError, TypeError, ValueError):
            continue
    return rows


def _parse_stockapi_row_list(code: str, rows_data: list) -> list[DailyBar]:
    rows: list[DailyBar] = []
    for item in rows_data:
        if not isinstance(item, dict):
            continue
        try:
            rows.append(DailyBar(
                code=code,
                trade_date=str(item.get("time") or item.get("date") or item.get("tradeDate")),
                open=float(item.get("open", 0) or 0),
                high=float(item.get("high", 0) or 0),
                low=float(item.get("low", 0) or 0),
                close=float(item.get("close", 0) or 0),
                volume=float(item.get("volume", 0) or 0),
                amount=float(item.get("amount", 0) or item.get("transactionAmount", 0) or 0),
            ))
        except (TypeError, ValueError):
            continue
    return rows


class StockApiProvider:
    def __init__(self, token: str = ""):
        self.token = token

    def get_realtime_quotes(self, codes: list[str]) -> list[Quote]:
        return []

    def get_daily_bars(self, code: str, days: int) -> list[DailyBar]:
        end = date.today()
        start = end - timedelta(days=max(days * 2 + 10, 40))
        all_rows: list[DailyBar] = []
        max_window_days = 30 if self.token else 5
        for start_date, end_date in build_date_windows(start, end, max_days=max_window_days):
            params = {
                "code": strip_market_prefix(code),
                "startDate": start_date,
                "endDate": end_date,
                "calculationCycle": "100",
            }
            if self.token:
                params["token"] = self.token
            url = BASE_URL + "?" + urlencode(params)
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(req, timeout=10) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
            except Exception:
                continue
            all_rows.extend(parse_stockapi_daily(code, payload))
        unique = {bar.trade_date: bar for bar in all_rows}
        return [unique[k] for k in sorted(unique)][-days:]

    def get_rsi_rows(self, code: str, days: int, cycle1: int = 6, cycle2: int = 12, cycle3: int = 24) -> list[tuple[str, float, float]]:
        end = date.today()
        start = end - timedelta(days=max(days * 2 + 10, 40))
        all_rows: list[tuple[str, float, float]] = []
        max_window_days = 30 if self.token else 5
        for start_date, end_date in build_date_windows(start, end, max_days=max_window_days):
            params = {
                "code": strip_market_prefix(code),
                "cycle1": cycle1,
                "cycle2": cycle2,
                "cycle3": cycle3,
                "startDate": start_date,
                "endDate": end_date,
                "calculationCycle": "100",
            }
            if self.token:
                params["token"] = self.token
            url = RSI_URL + "?" + urlencode(params)
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(req, timeout=10) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
            except Exception:
                continue
            all_rows.extend(parse_stockapi_rsi(payload))
        unique = {trade_date: (trade_date, rsi1, rsi2) for trade_date, rsi1, rsi2 in all_rows}
        return [unique[k] for k in sorted(unique)][-days:]

    def get_limit_up_pool(self, trade_date: str) -> list[LimitUpStock]:
        return []

    def get_trade_calendar(self) -> list[str]:
        return []

    def get_hot_boards(self, trade_date: str) -> list[HotBoard]:
        params = {"date": trade_date}
        if self.token:
            params["token"] = self.token
        try:
            req = Request(HOT_BOARD_URL + "?" + urlencode(params), headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=10) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception:
            return []
        return parse_hot_boards(payload)

    def get_hot_leaders(self, trade_date: str, plate_id: str) -> list[HotLeader]:
        params = {"date": trade_date, "plateId": plate_id}
        if self.token:
            params["token"] = self.token
        try:
            req = Request(HOT_LEADER_URL + "?" + urlencode(params), headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=10) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception:
            return []
        return parse_hot_leaders(payload)
