from __future__ import annotations

from datetime import date, timedelta


def parse_ymd(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def is_trading_day(day: date, holidays: set[str] | None = None) -> bool:
    holidays = holidays or set()
    if day.weekday() >= 5:
        return False
    return day.isoformat() not in holidays


def trading_days_since(start_date: str, end_date: str, holidays: set[str] | None = None) -> int:
    start = parse_ymd(start_date)
    end = parse_ymd(end_date)
    if not start or not end or start > end:
        return 0

    count = 0
    cur = start
    while cur <= end:
        if is_trading_day(cur, holidays):
            count += 1
        cur += timedelta(days=1)
    return count
