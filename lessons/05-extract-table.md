# Lesson 05 · Extract a table to CSV and Excel

> **Goal:** scrape every page of the provider table and save it as CSV and as a nicely formatted Excel file.

## PAD → Playwright / Python mapping

| PAD | Python |
|---|---|
| **Extract data from web page** (table) | loop over `page.get_by_test_id("provider-row").all()` and read `locator("td").all_inner_texts()` |
| Extract → "Handle pagination" with Next button | `while next_button.is_enabled(): next_button.click() ...` |
| DataTable variable | a **list of dicts**: `[{"NPI": "...", "Provider name": "..."}, ...]` |
| DataRow / `%CurrentItem['NPI']%` | `row["NPI"]` |
| **Write to CSV file** | `csv.DictWriter(...).writerows(rows)` |
| **Launch Excel** (blank) | `wb = Workbook()` (openpyxl, no Excel install needed!) |
| **Write to Excel worksheet** | `ws.append([...])` (one row at a time) |
| **Close Excel** → Save as | `wb.save("file.xlsx")` |
| Set cell font bold / colour | `cell.font = Font(bold=True)`, `cell.fill = PatternFill(...)` |

## Python data, explained like PAD

```python
row = {"NPI": "1104332181", "Provider name": "Aarav Mehta, MD"}   # dict  ≈ one DataRow
rows = [row, row2, row3]                                          # list  ≈ DataTable
rows.append(row4)                                                 # PAD: Add item to list
print(row["NPI"])                                                 # %CurrentItem['NPI']%
print(len(rows))                                                  # %ExcelData.RowsCount%
```

## Reading one page of the table

```python
COLUMNS = ["NPI", "Provider name", "Specialty", "State", "Enrollment status"]
rows = []
for tr in page.get_by_test_id("provider-row").all():       # each <tr>
    cells = tr.locator("td").all_inner_texts()               # ['1013389083', 'Emily Carter, DO', ...]
    rows.append(dict(zip(COLUMNS, cells)))                   # glue column names to values
```

`zip` pairs two lists side by side; `dict(...)` turns the pairs into a row.

## Pagination without getting the same page twice

```python
next_btn = page.get_by_role("button", name="Next page")
while next_btn.is_enabled():                        # PAD: Loop condition
    before = page.get_by_test_id("page-info").inner_text()        # "Page 1 of 4"
    next_btn.click()
    expect(page.get_by_test_id("page-info")).not_to_have_text(before)   # wait for the NEW page
    rows += read_current_page(page)
```

## Saving

```python
import csv
with open("providers.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLUMNS)
    w.writeheader()
    w.writerows(rows)

from openpyxl import Workbook
wb = Workbook(); ws = wb.active
ws.append(COLUMNS)
for r in rows:
    ws.append([r[c] for c in COLUMNS])
wb.save("providers.xlsx")
```

`newline=""` stops Windows adding blank lines between CSV rows. `encoding="utf-8"` keeps names like "Women's Health" or "–" safe.

## Exercises

1. Read **page 1** of *Provider search* into a list of dicts and print the first 3 (there should be 8 rows).
2. Click through **all pages** and collect all **30** providers. Save them to `output/providers_extract.csv`.
3. Write the same rows to `output/providers_extract.xlsx` with a **bold, blue header**, column widths that fit, and the top row **frozen**.

Solution: [`solutions/05_extract_table.py`](../solutions/05_extract_table.py)
