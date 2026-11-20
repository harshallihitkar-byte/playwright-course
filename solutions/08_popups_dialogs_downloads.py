"""
Lesson 08 - New tabs, popups, dialogs and downloads (solutions)
"""
import csv
import os

from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, OUTPUT_DIR, SLOW_MO, login, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def exercise_1(page):
    """New tab and popup window."""
    page.goto(f"{BASE_URL}/tools.html")
    # Tell Playwright "a new tab is about to open", THEN click.
    with page.context.expect_page() as tab_info:
        page.get_by_role("link", name="Open enrollment guide (new tab)").click()
    tab = tab_info.value
    tab.wait_for_load_state()
    print("  new tab title:", tab.title())
    expect(tab.get_by_test_id("guide-title")).to_have_text("Enrollment guide")
    tab.close()                                               # PAD: Close web browser (that tab only)

    with page.expect_popup() as popup_info:
        page.get_by_role("button", name="View fee schedule").click()
    popup = popup_info.value
    fee = popup.get_by_test_id("fee-group").inner_text()
    print("  group enrollment fee from popup:", fee)
    assert fee == "$709.00"
    popup.get_by_role("button", name="Close window").click()
    passed("Exercise 1 - handled a new tab and a popup")


def exercise_2(page):
    """alert, confirm (Cancel and OK) and prompt."""
    messages = []

    page.once("dialog", lambda d: (messages.append(d.message), d.accept()))
    page.get_by_role("button", name="Show session notice").click()
    expect(page.get_by_test_id("dialog-result")).to_have_text("Alert acknowledged.")

    page.once("dialog", lambda d: d.dismiss())                # click Cancel
    page.get_by_role("button", name="Withdraw application").click()
    expect(page.get_by_test_id("dialog-result")).to_have_text("Withdrawal cancelled.")

    page.once("dialog", lambda d: d.accept())                 # click OK
    page.get_by_role("button", name="Withdraw application").click()
    expect(page.get_by_test_id("dialog-result")).to_have_text("Application ENR-2026-104882 withdrawn.")

    page.once("dialog", lambda d: d.accept("Called provider office"))   # type into a prompt
    page.get_by_role("button", name="Add case note").click()
    expect(page.get_by_test_id("dialog-result")).to_have_text("Note saved: Called provider office")
    print("  alert text was:", messages[0])
    passed("Exercise 2 - alert, confirm (both ways) and prompt")


def exercise_3(page):
    """Download a static CSV and a generated one, then count the rows."""
    page.goto(f"{BASE_URL}/downloads.html")
    with page.expect_download() as dl_info:
        page.get_by_test_id("download-roster").click()
    roster = OUTPUT_DIR / dl_info.value.suggested_filename
    dl_info.value.save_as(roster)

    with page.expect_download() as dl_info:
        page.get_by_role("button", name="Generate report").click()
    report = OUTPUT_DIR / dl_info.value.suggested_filename
    dl_info.value.save_as(report)

    for f in (roster, report):
        with open(f, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        print(f"  {f.name}: {len(rows)} data rows")
        assert len(rows) == 30
    passed("Exercise 3 - two downloads saved and read")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        login(page, BASE_URL)
        exercise_1(page)
        exercise_2(page)
        exercise_3(page)
        browser.close()
