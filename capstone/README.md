# License Lookup Checker

**Automated state-license verification for healthcare provider credentialing, built with Python + Playwright.**

Reads a list of providers from Excel, signs in to a provider portal (user ID, password **and OTP**), looks up every provider's state license, and produces a colour-coded Excel report showing license status, expiry date, and which licenses **expire within 90 days**.

> Runs against a purpose-built **practice portal** with fake data (`../practice-portal`), so it can be demoed anywhere without touching a real system or real provider data.

---

## The problem

Credentialing teams must confirm that every enrolled provider holds an active state license and renew it before it lapses. A lapsed license can mean claim denials and compliance findings. Done by hand, this means logging in to a portal, searching each NPI, copying status and expiry into a spreadsheet, and working out who expires soon: roughly 2–3 minutes per provider, every month, with copy-paste errors.

## The approach

| Concern | How it's handled |
|---|---|
| **Input** | `providers.xlsx` (Provider Name, NPI, License Number, State). NPI is the main key; falls back to license number when NPI is missing. Bad rows (e.g. 9-digit NPI) are flagged, not crashed on. |
| **Login + MFA** | Signs in with user ID/password, completes the OTP step, then saves the session (`storage_state`). Next runs **reuse the session** and skip login; if it has expired, the bot logs in again by itself. OTP retrieval is isolated in one method (`get_otp`) so a real email/authenticator source can be plugged in. |
| **Selectors** | Accessible, stable locators only (`get_by_label`, `get_by_role`, `data-testid`). The portal deliberately uses dynamic ASP.NET-style IDs; none are used. |
| **Waiting** | No fixed sleeps: waits for the "Searching…" spinner to finish and for results/errors to appear. |
| **Reliability** | Per-provider retries with back-off (the portal is run in `?flaky=1` mode where ~25% of searches return a 503). A **screenshot is saved on every failed attempt**. One bad provider never stops the run, and results are written even if the run crashes half-way. |
| **Business rules** | Pure, unit-tested functions in `rules.py`: expired, suspended, pending, not found, and "renew within N days" (window configurable, default 90). |
| **Output** | `output/results.xlsx` with a *Results* sheet (colour-coded rows, real Excel dates, filters, frozen header) and a *Summary* sheet for managers. Plus a timestamped log file. |
| **Configuration** | `config.toml`: URLs, timeouts, retries, warning window, file paths, headless mode. Credentials can be overridden with environment variables (`PORTAL_USERNAME`, `PORTAL_PASSWORD`, `PORTAL_OTP`). |

### Project layout

```
capstone/
├── license_checker.py   # entry point: reads Excel, loops providers, retries, writes report
├── portal.py            # all browser work: login + OTP, session reuse, license search (page-object style)
├── excel_io.py          # read providers.xlsx, write formatted results.xlsx + Summary sheet
├── rules.py             # pure business rules (NPI validation, date parsing, expiry assessment)
├── config.toml          # settings
├── providers.xlsx       # sample input (14 fake providers, incl. a not-found and a typo row)
├── tests/test_rules.py  # unit tests for the rules (pytest)
├── requirements.txt
├── sample_output/       # results_sample.xlsx from a real run
└── output/              # created at run time (results, log, screenshots, session) - git-ignored
```

## How to run

```bat
:: 1. one-time setup (Windows)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

:: 2. start the practice portal in a second terminal
cd ..\practice-portal
python -m http.server 8000

:: 3. run the checker
cd ..\capstone
python license_checker.py              :: headless, as configured
python license_checker.py --headed     :: watch the browser work

:: 4. unit tests
python -m pytest -q tests
```

Exit code is `0` when every provider was checked and `2` if any provider still failed after all retries (handy for schedulers such as Windows Task Scheduler or a Power Automate cloud flow that triggers the script).

To run against a hosted copy of the portal: `set BASE_URL=https://<user>.github.io/practice-portal` (or edit `config.toml`).

## Sample output

Console / log (`output/license_checker.log`):

```
17:49:45 | INFO    | Loaded 14 providers from providers.xlsx
17:49:45 | INFO    | Logging in as provider.admin
17:49:47 | INFO    | Login OK, session saved to output/auth_state.json
17:49:48 | INFO    | Row 2 Aarav Mehta            -> Active     expiry=01/06/2028
17:49:50 | INFO    | Row 3 Emily Carter           -> Active     expiry=01/04/2027 Renew within 45 days
17:49:53 | WARNING | Row 5 Daniel Brooks: attempt 1/5 failed: State board service temporarily unavailable (error 503). (screenshot: output/screenshots/row5_1816184959_try1_174953.png)
17:49:55 | INFO    | Row 5 Daniel Brooks          -> Expired    expiry=10/21/2026 EXPIRED - start renewal, check billing hold
17:49:56 | INFO    | Row 6 James Whitfield        -> Suspended  expiry=03/20/2027 SUSPENDED - escalate to credentialing team
17:50:03 | WARNING | Row 13 Typo Example: NPI '110433218' is not 10 digits - fix the input file
17:50:04 | INFO    | Results written to output/results.xlsx
17:50:04 | INFO    | Done in 19.9s: 14 checked, 12 found, 7 expiring within 90 days, 0 errors
```

Second run: `Reused saved session (skipped login + OTP)`.

`output/results.xlsx` → *Results* sheet (excerpt; run on 20 Nov 2026):

| Provider Name | NPI | State | License Status | Expiry Date | Days Until Expiry | Expiring Within 90 Days | Action Needed | Lookup Result | Attempts |
|---|---|---|---|---|---|---|---|---|---|
| Aarav Mehta | 1104332181 | TX | Active | 01/06/2028 | 412 | NO | | Found | 2 |
| Emily Carter | 1013389083 | CA | Active | 01/04/2027 | 45 | **YES** | Renew within 45 days | Found | 1 |
| Priya Shah | 1503056413 | NJ | Active | 12/05/2026 | 15 | **YES** | Renew within 15 days | Found | 1 |
| Daniel Brooks | 1816184959 | TX | Expired | 10/21/2026 | -30 | NO | EXPIRED - start renewal, check billing hold | Found | 1 |
| James Whitfield | 1341928327 | GA | Suspended | 03/20/2027 | 120 | NO | SUSPENDED - escalate to credentialing team | Found | 1 |
| Ethan Clark | 1911718227 | PA | Pending | | | NO | Pending with board - follow up | Found | 1 |
| Rahul Desai | 1133150983 | FL | Active | 12/20/2026 | 30 | **YES** | Renew within 30 days | Found | 1 |
| Jordan Unknown | 1999999999 | TX | Not found | | | NO | Not found on state board - verify NPI / license number | Not found | 1 |
| Typo Example | 110433218 | | | | | NO | *(note: NPI is not 10 digits - fix the input file)* | Invalid input | 0 |
| Neha Kulkarni | 1619399091 | CA | Active | 02/17/2029 | 820 | NO | | Found | 3 |

Rows are shaded **red** (expired / suspended / not found / error), **amber** (expiring soon / pending) or **green** (OK). *Summary* sheet: 14 checked · 12 found · 1 not found · 1 invalid input · 7 expiring within 90 days.

> The practice portal computes expiry dates relative to *today*, so every demo run shows the same mix of expired, expiring-soon and valid licenses.

## What I'd add for production

- OTP from the mailbox via Microsoft Graph (or TOTP via `pyotp` where policy allows), and secrets from Windows Credential Manager / Azure Key Vault.
- Parallel lookups (several browser contexts) with a rate limit that respects the portal's terms of use.
- Trace-on-failure (`context.tracing`) attached to an email/Teams summary from a Power Automate cloud flow.
- Persisting history to SharePoint/SQL to trend renewals month over month.

---

Built by Harshal Lihitkar: RPA Lead (Power Automate Desktop & Cloud Flows) moving into Python + Playwright automation. All data in this project is fictional.
