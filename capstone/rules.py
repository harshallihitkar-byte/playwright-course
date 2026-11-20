"""Business rules: pure functions with no browser, so they are easy to unit test."""
from __future__ import annotations

import re
from datetime import date, datetime

NPI_PATTERN = re.compile(r"^\d{10}$")


def clean_npi(value) -> str:
    """Excel often turns 1104332181 into 1104332181.0 or a number. Normalise to a 10-char string."""
    if value is None:
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def is_valid_npi(npi: str) -> bool:
    return bool(NPI_PATTERN.match(npi))


def parse_us_date(text: str) -> date | None:
    """'01/06/2028' -> date(2028, 1, 6). Returns None for 'N/A' or blank."""
    text = (text or "").strip()
    if not text or text.upper() == "N/A":
        return None
    return datetime.strptime(text, "%m/%d/%Y").date()


def days_until(expiry: date | None, today: date) -> int | None:
    return None if expiry is None else (expiry - today).days


def assess(status: str, expiry: date | None, today: date, warning_days: int = 90) -> tuple[bool, str]:
    """Return (expiring_within_window, action_needed)."""
    days = days_until(expiry, today)
    expiring = days is not None and 0 <= days <= warning_days and status == "Active"
    if status == "Not found":
        return False, "Not found on state board - verify NPI / license number"
    if status == "Expired" or (days is not None and days < 0):
        return False, "EXPIRED - start renewal, check billing hold"
    if status == "Suspended":
        return False, "SUSPENDED - escalate to credentialing team"
    if status == "Pending":
        return False, "Pending with board - follow up"
    if expiring:
        return True, f"Renew within {days} days"
    return False, ""
