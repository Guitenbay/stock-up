from __future__ import annotations


def format_code(code: str) -> str | None:
    value = str(code or "").strip().lower()
    if not value:
        return None
    if value.startswith(("sh", "sz", "hk", "bj")):
        return value
    if not value.isdigit():
        return value

    if len(value) <= 4 or (len(value) == 5 and value.startswith("0")):
        return "hk" + value.zfill(5)

    if len(value) == 6:
        if value.startswith(("4", "8")):
            return "bj" + value
        if value.startswith("6") or value.startswith(("51", "56", "58")):
            return "sh" + value
        if value.startswith(("0", "1", "3")):
            return "sz" + value

    return value
