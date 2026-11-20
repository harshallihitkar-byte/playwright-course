"""
portal_helpers.py - small reusable "subflows" shared by the lesson solutions.

In PAD you would put these steps in a subflow and call it with "Run subflow".
In Python a subflow is simply a function: def login(page, base_url): ...
"""
import os
from pathlib import Path

from playwright.sync_api import Page, expect

# Practice credentials (they are printed on the portal's login page - fake!)
USERNAME = "provider.admin"
PASSWORD = "Enroll@2026"
OTP_CODE = "482913"

# Settings you can change without touching code (like PAD input variables)
HEADLESS = os.getenv("HEADLESS", "0") == "1"      # set HEADLESS=1 to hide the browser
SLOW_MO = int(os.getenv("SLOW_MO", "0"))           # e.g. SLOW_MO=300 to slow every action down

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def login(page: Page, base_url: str) -> None:
    """Sign in with user ID + password, then the one-time passcode (OTP)."""
    page.goto(f"{base_url}/index.html")
    page.get_by_label("User ID").fill(USERNAME)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()

    # The OTP box appears after a short, random delay. fill() waits for it automatically.
    page.get_by_label("One-time passcode").fill(OTP_CODE)
    page.get_by_role("button", name="Verify").click()

    # Don't continue until the dashboard really loaded (PAD: "Wait for web page content")
    expect(page.get_by_test_id("welcome-message")).to_be_visible()


def passed(msg: str) -> None:
    print(f"[PASS] {msg}")
