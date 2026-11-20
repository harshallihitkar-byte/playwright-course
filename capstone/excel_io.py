"""Reading the input workbook and writing a formatted results workbook."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from rules import clean_npi

REQUIRED_COLUMNS = ["Provider Name", "NPI", "License Number", "State"]


@dataclass
class ProviderRow:
    row_number: int
    name: str
    npi: str
    license_number: str
    state: str


@dataclass
class ResultRow:
    provider: ProviderRow
    lookup_result: str = ""          # Found / Not found / Invalid input / Error
    status: str = ""
    portal_license: str = ""
    expiry: date | None = None
    days_left: int | None = None
    expiring_soon: bool = False
    action: str = ""
    attempts: int = 0
    checked_at: datetime = field(default_factory=datetime.now)
    notes: str = ""


def read_providers(path: Path) -> list[ProviderRow]:
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    header = [str(h).strip() if h else "" for h in next(rows)]
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        raise ValueError(f"{path.name} is missing column(s): {', '.join(missing)}")
    idx = {name: header.index(name) for name in REQUIRED_COLUMNS}
    providers = []
    for n, values in enumerate(rows, start=2):
        if not values or all(v in (None, "") for v in values):
            continue
        get = lambda col: "" if values[idx[col]] is None else str(values[idx[col]]).strip()
        providers.append(ProviderRow(n, get("Provider Name"), clean_npi(values[idx["NPI"]]),
                                     get("License Number").upper(), get("State").upper()))
    wb.close()
    return providers


HEADERS = ["Provider Name", "NPI", "State", "License Number (portal)", "License Status", "Expiry Date",
           "Days Until Expiry", "Expiring Within 90 Days", "Action Needed", "Lookup Result", "Attempts",
           "Checked At", "Notes"]
RED = PatternFill("solid", fgColor="FDE8E7")
AMBER = PatternFill("solid", fgColor="FFF1DB")
GREEN = PatternFill("solid", fgColor="E3F6EC")
HEADER_FILL = PatternFill("solid", fgColor="0B5CAD")


def write_results(results: list[ResultRow], path: Path, warning_days: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"
    headers = [h.replace("90", str(warning_days)) for h in HEADERS]
    ws.append(headers)
    for r in results:
        ws.append([r.provider.name, r.provider.npi, r.provider.state, r.portal_license, r.status, r.expiry,
                   r.days_left, "YES" if r.expiring_soon else "NO", r.action, r.lookup_result, r.attempts,
                   r.checked_at, r.notes])
        fill = None
        if r.lookup_result in ("Error", "Not found", "Invalid input") or r.status in ("Expired", "Suspended"):
            fill = RED
        elif r.expiring_soon or r.status == "Pending":
            fill = AMBER
        elif r.lookup_result == "Found":
            fill = GREEN
        if fill:
            for cell in ws[ws.max_row]:
                cell.fill = fill
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=2):
        row[5].number_format = "mm/dd/yyyy"
        row[11].number_format = "yyyy-mm-dd hh:mm"
    widths = [24, 13, 7, 22, 14, 13, 10, 12, 44, 14, 9, 17, 40]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    # Summary sheet for the manager
    s = wb.create_sheet("Summary")
    s.append(["Metric", "Count"])
    s.append(["Providers checked", len(results)])
    for label, n in Counter(r.lookup_result for r in results).items():
        s.append([f"Lookup: {label}", n])
    for label, n in Counter(r.status for r in results if r.status).items():
        s.append([f"Status: {label}", n])
    s.append([f"Expiring within {warning_days} days", sum(r.expiring_soon for r in results)])
    s.append(["Run finished", datetime.now().strftime("%Y-%m-%d %H:%M")])
    for cell in s[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
    s.column_dimensions["A"].width = 32
    s.column_dimensions["B"].width = 18
    wb.save(path)
