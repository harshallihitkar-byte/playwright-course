"""
Lesson 11 - Codegen and the Trace Viewer (solutions)

Codegen itself is interactive:   playwright codegen http://localhost:8000/index.html
This file shows (1) a cleaned-up version of what codegen records, and (2) how to record traces.
Open a trace with:   playwright show-trace output/trace_lesson11.zip
"""
import os

from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, OUTPUT_DIR, SLOW_MO, OTP_CODE, PASSWORD, USERNAME, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def recorded_flow(page):
    """Exercise 1: codegen output for 'log in and look up a license', tidied up by hand."""
    page.goto(f"{BASE_URL}/index.html")
    page.get_by_role("textbox", name="User ID").fill(USERNAME)
    page.get_by_role("textbox", name="Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("textbox", name="One-time passcode").fill(OTP_CODE)
    page.get_by_role("button", name="Verify").click()
    page.get_by_test_id("nav-license").click()
    page.get_by_role("combobox", name="State").select_option("TX")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_test_id("lookup-count")).to_have_text("4 records found")


def exercise_1_and_2(browser):
    """Run the recorded flow with tracing switched on, save trace.zip."""
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    recorded_flow(page)
    trace = OUTPUT_DIR / "trace_lesson11.zip"
    context.tracing.stop(path=str(trace))
    context.close()
    print("  trace saved. Open it with:  playwright show-trace", trace)
    assert trace.exists() and trace.stat().st_size > 10_000
    passed("Exercise 1+2 - recorded flow ran, trace saved")


def exercise_3(browser):
    """Keep a trace ONLY when something fails (saves disk space on big runs)."""
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    trace = OUTPUT_DIR / "trace_on_failure.zip"
    trace.unlink(missing_ok=True)
    try:
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_role("button", name="Sign in with SSO").click(timeout=1_500)   # not on the page
        context.tracing.stop()                     # success -> throw the trace away
    except Exception as exc:
        context.tracing.stop(path=str(trace))      # failure -> keep it for debugging
        print(f"  step failed ({type(exc).__name__}); trace kept at {trace}")
    context.close()
    assert trace.exists()
    passed("Exercise 3 - trace kept only on failure")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        exercise_1_and_2(browser)
        exercise_3(browser)
        browser.close()
