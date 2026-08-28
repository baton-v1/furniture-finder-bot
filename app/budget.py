import re


def parse_budget(raw: str) -> int:
    normalized = raw.replace(",", "").replace(" ", "")
    match = re.search(r"\d+", normalized)
    if not match:
        raise ValueError("budget must contain a number")
    value = int(match.group(0))
    if value <= 0:
        raise ValueError("budget must be positive")
    return value
