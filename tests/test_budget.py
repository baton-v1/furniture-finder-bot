import pytest

from app.budget import parse_budget


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("500", 500),
        ("$1,200", 1200),
        ("до 850 долларов", 850),
        ("1000 usd", 1000),
    ],
)
def test_parse_budget_accepts_common_formats(raw, expected):
    assert parse_budget(raw) == expected


def test_parse_budget_rejects_missing_number():
    with pytest.raises(ValueError, match="budget"):
        parse_budget("не знаю")
