"""
Lesson 04 - Waits: no more "Wait 5 seconds" (solutions)
"""
import os
import time

from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, SLOW_MO, login, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def exercise_1(page):
    """Slow page: wait for the spinner to go away, then count rows."""
    start = time.time()
    page.goto(f"{BASE_URL}/status-queue.html")
    page.get_by_test_id("spinner").wait_for(state="hidden", timeout=10_000)   # PAD: Wait for web page content (disappear)
    expect(page.get_by_test_id("queue-table")).to_be_visible()
    rows = page.get_by_test_id("queue-row")
    print(f"  table appeared after {time.time() - start:.1f}s with {rows.count()} rows")
    assert rows.count() == 12
    passed("Exercise 1 - waited for the spinner, not a fixed sleep")


def exercise_2(page):
    """Click 'Refresh queue' 3 times; each time wait for the 'Loaded in' text."""
    for i in range(3):
        page.get_by_role("button", name="Refresh queue").click()
        expect(page.get_by_test_id("spinner")).to_be_visible()
        # expect() keeps retrying until true or until the timeout (5 s default; we allow 10 s)
        expect(page.get_by_test_id("load-time")).to_contain_text("Loaded in", timeout=10_000)
        print(f"  refresh {i + 1}: {page.get_by_test_id('load-time').inner_text()}")
    passed("Exercise 2 - expect().to_contain_text waits automatically")


def exercise_3(page):
    """Filter the provider list and wait for the summary text to change."""
    page.goto(f"{BASE_URL}/providers.html")
    expect(page.get_by_test_id("results-summary")).to_have_text("Showing 1–8 of 30 providers")
    page.get_by_role("button", name="Filter by name").click()
    page.get_by_label("Provider name").fill("pat")
    page.get_by_role("button", name="Apply filters").click()
    expect(page.get_by_test_id("results-summary")).to_have_text("Showing 1–1 of 1 providers")
    expect(page.get_by_test_id("provider-row")).to_have_count(1)
    print("  filtered row:", page.get_by_test_id("provider-row").inner_text().replace("\t", " | "))
    passed("Exercise 3 - waited for the filtered result")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = browser.new_page()
        login(page, BASE_URL)
        exercise_1(page)
        exercise_2(page)
        exercise_3(page)
        browser.close()
