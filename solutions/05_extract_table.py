"""
Lesson 05 - Extract a table to CSV and Excel (solutions)
"""
import csv
import os

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, OUTPUT_DIR, SLOW_MO, login, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
COLUMNS = ["NPI", "Provider name", "Specialty", "State", "Enrollment status"]


def read_current_page(page):
    """Turn the visible table rows into a list of dicts (PAD: Extract data from web page)."""
    expect(page.get_by_test_id("table-loading")).to_be_hidden()
    results = []
    for row in page.get_by_test_id("provider-row").all():
        cells = row.locator("td").all_inner_texts()     # ['1013389083', 'Emily Carter, DO', ...]
        results.append(dict(zip(COLUMNS, cells)))
    return results


def exercise_1(page):
    page.goto(f"{BASE_URL}/providers.html")
    first_page = read_current_page(page)
    for r in first_page[:3]:
        print("  ", r)
    assert len(first_page) == 8
    passed("Exercise 1 - read page 1 (8 rows)")


def exercise_2(page):
    """Walk through every page with Next until it is disabled; save CSV."""
    page.goto(f"{BASE_URL}/providers.html")
    all_rows = read_current_page(page)
    next_btn = page.get_by_role("button", name="Next page")
    while next_btn.is_enabled():
        current = page.get_by_test_id("page-info").inner_text()
        next_btn.click()
        expect(page.get_by_test_id("page-info")).not_to_have_text(current)   # wait until the page really changed
        all_rows += read_current_page(page)
    print(f"  collected {len(all_rows)} rows")
    assert len(all_rows) == 30

    csv_path = OUTPUT_DIR / "providers_extract.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:   # PAD: Write to CSV file
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)
    print("  CSV saved:", csv_path)
    passed("Exercise 2 - all pages -> CSV")
    return all_rows


def exercise_3(rows):
    """Same data into a tidy Excel file."""
    wb = Workbook()                       # PAD: Launch Excel (blank document)
    ws = wb.active
    ws.title = "Providers"
    ws.append(COLUMNS)
    for r in rows:
        ws.append([r[c] for c in COLUMNS])   # PAD: Write to Excel worksheet
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="0B5CAD")
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = max(len(str(c.value)) for c in col) + 2
    ws.freeze_panes = "A2"
    xlsx_path = OUTPUT_DIR / "providers_extract.xlsx"
    wb.save(xlsx_path)                    # PAD: Close Excel (save as)
    print("  Excel saved:", xlsx_path)
    assert xlsx_path.exists()
    passed("Exercise 3 - Excel with bold header and frozen top row")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = browser.new_page()
        login(page, BASE_URL)
        exercise_1(page)
        rows = exercise_2(page)
        browser.close()
    exercise_3(rows)
