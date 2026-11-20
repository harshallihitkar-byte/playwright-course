# Python + Playwright for Power Automate Desktop Developers

A hands-on course that takes you from **PAD expert / Python beginner** to building a real, recruiter-ready **Python + Playwright** bot, using a practice portal that looks and behaves like the provider-enrollment and credentialing sites you automate every day (login + OTP, drawers, paginated tables, multi-step forms, uploads, popups, slow pages, dynamic IDs).

Everything maps back to the PAD actions you already know. All data is **fake**.

## What's inside

| Folder | What it is |
|---|---|
| [`practice-portal/`](practice-portal/) | "ProviderGate", a static practice site (HTML/CSS/JS, flat layout, GitHub Pages-ready) |
| [`lessons/`](lessons/) | 12 lessons in Markdown, each with a PAD → Playwright table, explanation, example and exercises |
| [`solutions/`](solutions/) | One runnable `.py` per lesson that solves all of its exercises (+ `portal_helpers.py`) |
| [`capstone/`](capstone/) | **Portfolio project:** License Lookup Checker (Excel in → login with OTP → lookups with retries → Excel report) |
| [`preview/`](preview/) | Screenshots of the practice portal |

## Quick start (Windows)

```bat
cd playwright-course
python -m venv .venv
.venv\Scripts\activate
pip install playwright openpyxl pytest
playwright install chromium

:: terminal 1 - start the portal (leave it running)
cd practice-portal
python -m http.server 8000

:: terminal 2 - run any solution
cd solutions
python 01_setup_first_script.py
```

Practice login (also printed on the sign-in page): **provider.admin** / **Enroll@2026**, OTP **482913**.

Handy switches for every solution script:

| Setting | Example | Effect |
|---|---|---|
| `BASE_URL` | `set BASE_URL=https://<you>.github.io/practice-portal` | point at a hosted copy (default `http://localhost:8000`) |
| `HEADLESS` | `set HEADLESS=1` | run without showing the browser |
| `SLOW_MO` | `set SLOW_MO=500` | pause 0.5 s between actions so you can watch |

## Lessons

| # | Lesson | You'll learn | PAD actions it replaces | Solution |
|---|---|---|---|---|
| 01 | [Setup + first script](lessons/01-setup.md) | Python, pip, venv, VS Code, `playwright install`, first script | Launch new browser, Go to web page, Take screenshot | [01](solutions/01_setup_first_script.py) |
| 02 | [Selectors](lessons/02-selectors.md) | `get_by_role`, `get_by_label`, `get_by_test_id`, placeholder, text; avoiding dynamic IDs and ordinals | UI elements / selector builder | [02](solutions/02_selectors.py) |
| 03 | [Fill and click](lessons/03-fill-and-click.md) | `fill`, `click`, `expect`, login with OTP, functions = subflows | Populate text field, Press button, Click link | [03](solutions/03_fill_and_click.py) |
| 04 | [Waits](lessons/04-waits.md) | auto-waiting, `wait_for`, `expect(...)` with timeouts, spinners | Wait, Wait for web page content | [04](solutions/04_waits.py) |
| 05 | [Extract a table to CSV & Excel](lessons/05-extract-table.md) | rows → list of dicts, pagination, `csv`, `openpyxl` | Extract data from web page, Write to CSV/Excel | [05](solutions/05_extract_table.py) |
| 06 | [Loop over Excel rows](lessons/06-excel-loops.md) | `load_workbook`, `for`, `if`, functions with outputs | Read from Excel, For each, If, Run subflow | [06](solutions/06_excel_loop.py) |
| 07 | [Dropdowns, checkboxes, dates, uploads](lessons/07-forms-dropdowns-dates-uploads.md) | `select_option`, `check`, date inputs, **`set_input_files`** | Set drop-down value, Set check box state, (file upload PAD can't do with JS) | [07](solutions/07_forms.py) |
| 08 | [Popups, tabs, dialogs, downloads](lessons/08-popups-tabs-dialogs-downloads.md) | `expect_page`, `expect_popup`, dialog handlers, `expect_download` | Attach to browser, Handle web page dialog, Download from web | [08](solutions/08_popups_dialogs_downloads.py) |
| 09 | [Login with OTP + storage_state](lessons/09-login-otp-storage-state.md) | browser/context/page, save & reuse sessions, OTP strategies | Browser profile, Login subflow | [09](solutions/09_login_storage_state.py) |
| 10 | [Error handling, screenshots, logging](lessons/10-error-handling-logging.md) | `try/except/finally`, retries with back-off, `logging` | On block error, Retry, Get last error, Write text to file | [10](solutions/10_errors_logging.py) |
| 11 | [Codegen and Trace Viewer](lessons/11-codegen-trace-viewer.md) | recording scripts, cleaning them up, traces, `PWDEBUG` | Recorder, step-by-step debugging, run history | [11](solutions/11_codegen_trace.py) |
| 12 | [Git and GitHub basics](lessons/12-git-github-basics.md) | commit, diff, log, branches, `.gitignore`, pushing to GitHub, GitHub Pages | Flow versions, export/import | [12](solutions/12_git_basics.py) |

Then build the **[capstone](capstone/README.md)**.

## The practice portal

| Page | File | What it teaches |
|---|---|---|
| Sign in + OTP | `index.html` | fill/click, waiting for the OTP step, error messages |
| Dashboard | `dashboard.html` | tiles that **shuffle order** on every visit (ordinal trap) |
| Provider search | `providers.html` | *Filter by name* drawer, paginated table (30 providers, 8 per page) |
| Provider detail | `provider.html?npi=…` | reading labelled fields |
| Enrollment | `enroll.html` | 4-step form: dropdowns, radios, checkboxes, date pickers, file uploads, validation |
| License lookup | `license-lookup.html` | search by NPI / license # / state → status + expiry. `?flaky=1` simulates 503 errors |
| Downloads | `downloads.html` | static CSV + browser-generated CSV |
| Status queue | `status-queue.html` | spinner with a random 1–3 s delay |
| Help & tools | `tools.html`, `help.html` | new tab, popup window, alert, confirm, prompt |

Every input has a **dynamic id** (e.g. `ctl00_Main_txtUserId_qskpfxjrn`, different on each load) **and** stable hooks (`data-testid`, `name`, labels, placeholders), so you learn to choose well.

**Host it on GitHub Pages** (optional): push the *contents* of `practice-portal/` to a repo, then *Settings → Pages → Deploy from branch → main / (root)*. See Lesson 12.

## Suggested pace

About one lesson per day (45–60 min) alongside work. Lessons 01–06 cover 80% of everyday bots; do the capstone after Lesson 10. Type the code yourself before peeking at the solutions.
