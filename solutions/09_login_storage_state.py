"""
Lesson 09 - Login with OTP once, then reuse the session with storage_state (solutions)
"""
import os

from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, OUTPUT_DIR, SLOW_MO, login, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
STATE_FILE = OUTPUT_DIR / "auth_state.json"


def exercise_1(browser):
    """Log in (with OTP) and save the session to a file."""
    context = browser.new_context()
    page = context.new_page()
    login(page, BASE_URL)
    context.storage_state(path=str(STATE_FILE))    # saves cookies + localStorage
    context.close()
    print("  session saved to", STATE_FILE)
    assert STATE_FILE.exists()
    passed("Exercise 1 - logged in once, session saved")


def exercise_2(browser):
    """Open a brand-new browser context with the saved session: no login screen."""
    context = browser.new_context(storage_state=str(STATE_FILE))
    page = context.new_page()
    page.goto(f"{BASE_URL}/license-lookup.html")
    expect(page).to_have_url(f"{BASE_URL}/license-lookup.html")     # not bounced to index.html
    expect(page.get_by_test_id("signed-in-user")).to_be_visible()
    context.close()
    passed("Exercise 2 - reused the session, skipped login + OTP")


def get_logged_in_context(browser):
    """Reuse the saved session if it still works, otherwise log in again and re-save."""
    if STATE_FILE.exists():
        context = browser.new_context(storage_state=str(STATE_FILE))
        page = context.new_page()
        page.goto(f"{BASE_URL}/dashboard.html")
        if "index.html" not in page.url:          # still logged in
            print("  saved session is still valid")
            return context, page
        print("  saved session expired - logging in again")
        context.close()
    context = browser.new_context()
    page = context.new_page()
    login(page, BASE_URL)
    context.storage_state(path=str(STATE_FILE))
    return context, page


def exercise_3(browser):
    context, page = get_logged_in_context(browser)
    expect(page.get_by_test_id("welcome-message")).to_be_visible()
    context.close()

    # Simulate an expired session: an empty state file
    STATE_FILE.write_text('{"cookies": [], "origins": []}')
    context, page = get_logged_in_context(browser)
    expect(page.get_by_test_id("welcome-message")).to_be_visible()
    context.close()
    passed("Exercise 3 - smart login that only logs in when needed")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        exercise_1(browser)
        exercise_2(browser)
        exercise_3(browser)
        browser.close()
