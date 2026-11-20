"""Unit tests for the business rules (no browser needed):  python -m pytest tests"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rules import assess, clean_npi, is_valid_npi, parse_us_date  # noqa: E402

TODAY = date(2026, 11, 20)


def test_clean_npi_handles_excel_floats():
    assert clean_npi(1104332181.0) == "1104332181"
    assert clean_npi(" 1104332181 ") == "1104332181"
    assert clean_npi(None) == ""


def test_npi_validation():
    assert is_valid_npi("1104332181")
    assert not is_valid_npi("12345")
    assert not is_valid_npi("11043321AB")


def test_parse_us_date():
    assert parse_us_date("01/06/2028") == date(2028, 1, 6)
    assert parse_us_date("N/A") is None


def test_expiring_within_90_days_is_flagged():
    flag, action = assess("Active", date(2027, 1, 19), TODAY, 90)   # 60 days
    assert flag and action == "Renew within 60 days"


def test_day_90_is_inside_the_window_day_91_is_not():
    assert assess("Active", date(2027, 2, 18), TODAY, 90)[0] is True    # exactly 90
    assert assess("Active", date(2027, 2, 19), TODAY, 90)[0] is False   # 91


def test_expired_and_suspended_are_not_just_expiring():
    assert assess("Expired", date(2026, 10, 1), TODAY)[1].startswith("EXPIRED")
    assert assess("Suspended", date(2027, 3, 1), TODAY)[1].startswith("SUSPENDED")
    assert assess("Not found", None, TODAY)[1].startswith("Not found")
