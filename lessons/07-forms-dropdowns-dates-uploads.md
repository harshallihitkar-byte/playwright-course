# Lesson 07 · Dropdowns, radio buttons, checkboxes, dates and file uploads

> **Goal:** complete the 4-step **Enrollment** form, including the file upload that PAD can't do with JavaScript.

## PAD → Playwright mapping

| PAD | Playwright |
|---|---|
| **Set drop-down list value** → by name | `locator.select_option(label="Physician (MD)")` |
| **Set drop-down list value** → by index | ❌ avoid (ordinal!). Use value or label: `select_option("MD")` |
| Get selected option | `locator.input_value()` (the value) |
| **Select radio button on web page** | `page.get_by_label("Revalidation").check()` |
| **Set check box state** → Checked / Unchecked | `.check()` / `.uncheck()` / `.set_checked(True)` |
| Typing a date into a date picker (and fighting the calendar pop-up) | `page.get_by_label("Date of birth").fill("1995-04-12")` (always **YYYY-MM-DD** for `<input type="date">`) |
| File upload: click *Browse*, then drive the Windows "Open" dialog with UI automation (or a JavaScript hack that browsers block) | `locator.set_input_files("C:/docs/license.pdf")`. No dialog ever opens |
| "If check box is checked" | `expect(locator).to_be_checked()` or `locator.is_checked()` |

## Dropdowns

```python
page.get_by_label("Provider type").select_option(label="Nurse Practitioner (NP)")  # by the text you see
page.get_by_label("Practice state").select_option("TX")                            # by the hidden value
```

Inspect the `<option value="NP">Nurse Practitioner (NP)</option>` to see both. Labels are friendlier; values survive wording changes.

## Radio buttons and checkboxes

```python
page.get_by_label("Revalidation").check()             # radio
page.get_by_label("Telehealth").check()               # checkbox
page.get_by_label("Accepting new patients").set_checked(True)   # "make it ticked", safe to repeat
```

`.check()` on something already ticked does nothing, unlike a PAD *click*, which would untick it.

## Dates

A browser date input always takes the ISO format `YYYY-MM-DD`, whatever it *displays* (`04/12/1995` in the US). If your Excel has `04/12/1995`, convert it:

```python
from datetime import datetime
iso = datetime.strptime("04/12/1995", "%m/%d/%Y").strftime("%Y-%m-%d")   # '1995-04-12'
```

Some portals use custom JavaScript calendars instead of `type="date"`. For those, try `fill()` first; if it won't take it, click the calendar like a human (`get_by_role("button", name="Next month")`, `get_by_role("gridcell", name="12")`).

## File uploads: the big win over PAD

In PAD you have to click *Browse…*, then automate the Windows *Open* dialog (fragile) or inject JavaScript, and browsers **don't allow** JavaScript to set a file input. Playwright talks to the browser engine directly:

```python
page.get_by_label("State license copy").set_input_files("output/sample_license.pdf")

# or a file created in memory, no disk needed:
page.get_by_label("W-9 form").set_input_files(
    {"name": "w9.pdf", "mimeType": "application/pdf", "buffer": b"%PDF-1.4 ..."}
)

page.get_by_label("W-9 form").set_input_files([])     # clear the selection
```

If the site uses a custom "Drop files here" area with a hidden input, use `with page.expect_file_chooser() as fc: page.get_by_text("Browse").click()` then `fc.value.set_files(...)`.

## Exercises

1. **Step 1:** fill first/last name, NPI `1234567890`, date of birth, choose *Nurse Practitioner (NP)* by label and *Family Medicine* by value. Click *Next*.
2. **Step 2:** first click *Next* with nothing filled and check the validation error *"Choose an enrollment type."* Then pick *Revalidation*, state TX, an effective date, tick *In-person visits* + *Telehealth* + *Accepting new patients*, and check that *Home visits* is **not** ticked.
3. **Step 3–4:** upload a license PDF from disk and a W-9 from memory, check the review page lists your services, tick the attestation, submit, and print the **Application ID** (format `ENR-2026-123456`).

Solution: [`solutions/07_forms.py`](../solutions/07_forms.py)
