"""
Lesson 06 - Loop over Excel input rows (solutions)

Input : output/lesson06_input.xlsx (created automatically the first time)
Output: output/lesson06_results.xlsx
"""
import os

from openpyxl import Workbook, load_workbook
from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, OUTPUT_DIR, SLOW_MO, login, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
INPUT_FILE = OUTPUT_DIR / "lesson06_input.xlsx"
RESULT_FILE = OUTPUT_DIR / "lesson06_results.xlsx"


def create_sample_input():
    wb = Workbook()
    ws = wb.active
    ws.append(["NPI", "Provider name"])
    ws.append(["1104332181", "Aarav Mehta"])
    ws.append(["1816184959", "Daniel Brooks"])
    ws.append(["1503056413", "Priya Shah"])
    ws.append(["1999999999", "Not A Real Provider"])
    ws.append(["1911718227", "Ethan Clark"])
    wb.save(INPUT_FILE)


def exercise_1():
    """Read the rows (PAD: Read from Excel worksheet -> For each)."""
    if not INPUT_FILE.exists():
        create_sample_input()
    wb = load_workbook(INPUT_FILE)
    ws = wb.active
    rows = []
    for npi, name in ws.iter_rows(min_row=2, values_only=True):   # skip the header row
        if npi:                                                    # skip blank lines
            rows.append({"npi": str(npi).strip(), "name": name})
    for r in rows:
        print("  ", r)
    assert len(rows) == 5
    passed("Exercise 1 - read Excel rows")
    return rows


def lookup(page, npi):
    """One license lookup = one 'subflow'. Returns (status, expiry)."""
    page.get_by_label("NPI").fill(npi)
    page.get_by_role("button", name="Search").click()
    results = page.get_by_test_id("lookup-results-card")
    expect(results).to_be_visible(timeout=10_000)
    if page.get_by_test_id("no-results").is_visible():     # PAD: If ... then
        return "Not found", ""
    row = page.get_by_test_id("license-row").first
    return row.get_by_test_id("lic-status").inner_text(), row.get_by_test_id("lic-expiry").inner_text()


def exercise_2(page, rows):
    page.goto(f"{BASE_URL}/license-lookup.html")
    for r in rows:                                          # PAD: For each CurrentItem in ExcelData
        r["status"], r["expiry"] = lookup(page, r["npi"])
        print(f"  {r['npi']} {r['name']:<22} -> {r['status']:<10} {r['expiry']}")
    assert rows[3]["status"] == "Not found"
    passed("Exercise 2 - looked up every row")
    return rows


def exercise_3(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["NPI", "Provider name", "License status", "Expiry"])
    for r in rows:
        ws.append([r["npi"], r["name"], r["status"], r["expiry"]])
    wb.save(RESULT_FILE)
    print("  results saved:", RESULT_FILE)
    passed("Exercise 3 - results written to a new Excel file")


if __name__ == "__main__":
    rows = exercise_1()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = browser.new_page()
        login(page, BASE_URL)
        exercise_2(page, rows)
        browser.close()
    exercise_3(rows)
