"""
Lesson 10 - Error handling, screenshots, retries and logging (solutions)
"""
import logging
import os
import time
from datetime import datetime

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, OUTPUT_DIR, SLOW_MO, login, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# ---- Logging: like PAD's "Write text to file" log, but with levels and timestamps ----
LOG_FILE = OUTPUT_DIR / "lesson10.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("lesson10")


def screenshot_on_error(page, label):
    path = OUTPUT_DIR / f"error_{label}_{datetime.now():%Y%m%d_%H%M%S}.png"
    page.screenshot(path=str(path), full_page=True)
    log.error("Screenshot saved: %s", path)
    return path


def exercise_1(page):
    """Catch a timeout (PAD: On block error) and take a screenshot."""
    page.goto(f"{BASE_URL}/dashboard.html")
    try:
        page.get_by_role("button", name="Approve all applications").click(timeout=2_000)  # does not exist
    except PlaywrightTimeoutError:
        log.warning("Button not found within 2 s - continuing")
        shot = screenshot_on_error(page, "missing_button")
        assert shot.exists()
    passed("Exercise 1 - timeout caught, screenshot taken")


def lookup_once(page, npi):
    page.get_by_label("NPI").fill(npi)
    page.get_by_role("button", name="Search").click()
    error = page.get_by_test_id("lookup-error")
    # Wait until the "Searching..." spinner is gone, then see what we got
    expect(page.get_by_test_id("lookup-loading")).to_be_hidden(timeout=10_000)
    if error.is_visible():
        raise RuntimeError(error.inner_text())
    return page.get_by_test_id("license-row").first.get_by_test_id("lic-status").inner_text()


def with_retry(func, *args, attempts=4, wait_seconds=1.0):
    """Try up to `attempts` times, waiting a bit longer each time (PAD: On error -> Retry)."""
    for attempt in range(1, attempts + 1):
        try:
            return func(*args)
        except Exception as exc:
            log.warning("Attempt %d/%d failed: %s", attempt, attempts, exc)
            if attempt == attempts:
                raise
            time.sleep(wait_seconds * attempt)


def exercise_2(page):
    """The flaky page fails ~25% of the time. Retries make the bot reliable."""
    page.goto(f"{BASE_URL}/license-lookup.html?flaky=1")
    for npi in ["1104332181", "1013389083", "1637940265", "1511615594", "1341316475", "1503056413"]:
        status = with_retry(lookup_once, page, npi)
        log.info("NPI %s -> %s", npi, status)
    passed("Exercise 2 - flaky lookups survived with retries")


def exercise_3(page):
    """One bad row must not stop the whole run (try/except inside the loop + finally)."""
    page.goto(f"{BASE_URL}/license-lookup.html")
    ok, failed = 0, 0
    for npi in ["1104332181", "12345", "1816184959"]:   # "12345" is invalid on purpose
        try:
            status = with_retry(lookup_once, page, npi, attempts=2, wait_seconds=0.2)
            log.info("NPI %s -> %s", npi, status)
            ok += 1
        except Exception as exc:
            failed += 1
            log.error("NPI %s failed for good: %s", npi, exc)
            screenshot_on_error(page, f"npi_{npi}")
        finally:
            log.info("finished row %s", npi)
    log.info("Summary: %d ok, %d failed. Log file: %s", ok, failed, LOG_FILE)
    assert ok == 2 and failed == 1
    passed("Exercise 3 - kept going after a bad row")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = browser.new_page()
        login(page, BASE_URL)
        exercise_1(page)
        exercise_2(page)
        exercise_3(page)
        browser.close()
