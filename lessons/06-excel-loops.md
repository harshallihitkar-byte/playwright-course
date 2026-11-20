# Lesson 06 · Loop over Excel input rows

> **Goal:** the bread-and-butter RPA pattern: read an Excel file, do something on the portal for each row, write the results back.

## PAD → Python mapping

| PAD | Python |
|---|---|
| **Launch Excel** + **Read from Excel worksheet** | `wb = load_workbook("input.xlsx"); ws = wb.active` |
| "First line of range contains column names" | `ws.iter_rows(min_row=2, values_only=True)` (start after the header) |
| **For each** `%CurrentItem%` in `%ExcelData%` | `for npi, name in ws.iter_rows(...):` |
| **Loop** 1 to N | `for i in range(1, n + 1):` |
| **If** / **Else if** / **Else** | `if ...:` / `elif ...:` / `else:` |
| **Exit loop** / **Next loop** | `break` / `continue` |
| **Set variable** | `status = "Active"` |
| Convert number to text | `str(value)` |
| Trim text | `text.strip()` |
| **Run subflow** with inputs/outputs | `status, expiry = lookup(page, npi)` |

## Reading the rows

```python
from openpyxl import load_workbook

wb = load_workbook("output/lesson06_input.xlsx")
ws = wb.active
for npi, name in ws.iter_rows(min_row=2, values_only=True):
    if not npi:            # skip empty lines (PAD: If CurrentItem is empty -> Next loop)
        continue
    print(npi, name)
```

`values_only=True` gives you plain values instead of cell objects.

**Excel gotcha:** Excel likes to turn `1104332181` into the number `1104332181.0`. Always convert IDs to clean text: `str(npi).strip()`, and strip a trailing `.0` (the capstone shows how).

## A lookup "subflow" with two outputs

```python
def lookup(page, npi):
    page.get_by_label("NPI").fill(npi)
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_test_id("lookup-results-card")).to_be_visible(timeout=10_000)
    if page.get_by_test_id("no-results").is_visible():
        return "Not found", ""
    row = page.get_by_test_id("license-row").first
    return row.get_by_test_id("lic-status").inner_text(), row.get_by_test_id("lic-expiry").inner_text()

status, expiry = lookup(page, "1104332181")   # two output variables at once
```

`is_visible()` answers *right now* (no waiting) and is perfect inside an `if`. `expect(...)` waits and fails loudly, which suits "this must happen" checks.

## Exercises

1. Read `output/lesson06_input.xlsx` (the solution creates it with 5 NPIs on first run) into a list of dicts.
2. For each row, look up the license on **License lookup** and store status + expiry in the row. The NPI `1999999999` doesn't exist: your `if` must handle "Not found".
3. Write `output/lesson06_results.xlsx` with columns NPI, Provider name, License status, Expiry.

Solution: [`solutions/06_excel_loop.py`](../solutions/06_excel_loop.py)

This is the skeleton of the capstone project. Lesson 10 adds the safety net (retries, screenshots, logs).
