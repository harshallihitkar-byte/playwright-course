"""
Lesson 01 - Setup & your first script (solutions)

Run:  python 01_setup_first_script.py
The portal must be running:  cd practice-portal  then  python -m http.server 8000
"""
import os

from playwright.sync_api import sync_playwright

from portal_helpers import HEADLESS, OUTPUT_DIR, SLOW_MO, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def exercise_1(page):
    """Open the login page and print its title."""
    page.goto(f"{BASE_URL}/index.html")          # PAD: Launch new browser + Go to web page
    title = page.title()
    print("Page title is:", title)
    assert "Sign in" in title
    passed("Exercise 1 - opened the portal and read the title")


def exercise_2(page):
    """Read the practice username, password and OTP shown on the page."""
    username = page.get_by_test_id("demo-username").inner_text()   # PAD: Get details of element on web page
    password = page.get_by_test_id("demo-password").inner_text()
    otp = page.get_by_test_id("demo-otp").inner_text()
    print(f"Username={username}  Password={password}  OTP={otp}")
    assert username == "provider.admin" and otp == "482913"
    passed("Exercise 2 - read text from the page")


def exercise_3(page):
    """Take a full-page screenshot."""
    path = OUTPUT_DIR / "lesson01_login.png"
    page.screenshot(path=str(path), full_page=True)            # PAD: Take screenshot of web page
    assert path.exists()
    print("Screenshot saved to", path)
    passed("Exercise 3 - screenshot saved")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = browser.new_page()
        exercise_1(page)
        exercise_2(page)
        exercise_3(page)
        browser.close()
