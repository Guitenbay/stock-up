from __future__ import annotations


def plan_rsi_updates(holding_codes: list[str], watch_codes: list[str], max_updates: int) -> list[str]:
    if max_updates <= 0:
        return []
    planned: list[str] = []
    seen: set[str] = set()

    for code in list(holding_codes) + list(watch_codes):
        if code in seen:
            continue
        seen.add(code)
        planned.append(code)
        if len(planned) >= max_updates:
            break
    return planned
