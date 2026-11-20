"""
Lesson 03 - Fill and click: logging in (solutions)
"""
import os

from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, OTP_CODE, PASSWORD, SLOW_MO, USERNAME, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def exercise_1(page):
    """Wrong password -> check the error message."""
    page.goto(f"{BASE_URL}/index.html")
    page.get_by_label("User ID").fill(USERNAME)              # PAD: Populate text field on web page
    page.get_by_label("Password").fill("wrong-password")
    page.get_by_role("button", name="Sign in").click()        # PAD: Press button on web page
    error = page.get_by_test_id("login-error")
    expect(error).to_have_text("Invalid user ID or password. Please try again.")
    print("  Error shown:", error.inner_text())
    passed("Exercise 1 - wrong password gives an error")


def exercise_2(page):
    """Full login: user ID, password, then the OTP step."""
    page.goto(f"{BASE_URL}/index.html")
    page.get_by_label("User ID").fill(USERNAME)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_label("One-time passcode").fill(OTP_CODE)    # waits until the OTP box appears
    page.get_by_role("button", name="Verify").click()
    expect(page.get_by_test_id("welcome-message")).to_have_text("Welcome back, Provider Admin")
    passed("Exercise 2 - logged in with OTP")


def exercise_3(page):
    """Use the top menu to open License lookup, search one NPI and read the status."""
    page.get_by_role("navigation", name="Main").get_by_role("link", name="License lookup").click()  # PAD: Click link on web page
    page.get_by_label("NPI").fill("1104332181")
    page.get_by_role("button", name="Search").click()
    row = page.get_by_test_id("license-row")
    expect(row).to_have_count(1)
    status = row.get_by_test_id("lic-status").inner_text()
    print("  Aarav Mehta license status:", status)
    assert status == "Active"
    passed("Exercise 3 - menu click + search + read result")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = browser.new_page()
        exercise_1(page)
        exercise_2(page)
        exercise_3(page)
        browser.close()
