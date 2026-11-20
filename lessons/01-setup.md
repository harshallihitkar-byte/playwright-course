# Lesson 01 · Setup on Windows + your first script

> **Goal:** install everything once, start the practice portal, and run a 10-line Python script that opens a browser, reads the page and takes a screenshot.
> **Time:** about 45 minutes (most of it is downloads).

## PAD → Playwright mapping

| What you do in PAD | What you do in Python + Playwright |
|---|---|
| Install Power Automate Desktop + browser extension | Install **Python**, then `pip install playwright`, then `playwright install` (downloads its own browsers, no extension needed) |
| Create a new flow | Create a new `.py` file in **VS Code** |
| Flow designer | VS Code editor |
| ▶ Run button | `python my_script.py` in the terminal (or ▶ in VS Code) |
| **Launch new Microsoft Edge / Chrome** | `browser = p.chromium.launch()` then `page = browser.new_page()` |
| **Go to web page** | `page.goto("http://...")` |
| **Get details of web page** (title) | `page.title()` |
| **Get details of element on web page** (text) | `page.get_by_test_id("...").inner_text()` |
| **Take screenshot of web page** | `page.screenshot(path="file.png")` |
| **Close web browser** | `browser.close()` |
| Variables pane | `print(...)` in the terminal, or the VS Code debugger |

## 1. Install Python (5 min)

1. Go to <https://www.python.org/downloads/windows/> and download the latest **Python 3.12 or 3.13** installer (64-bit).
2. Run it and **tick "Add python.exe to PATH"** at the bottom of the first screen. This is the #1 beginner mistake. Then click *Install Now*.
3. Open **Command Prompt** (Win key → type `cmd`) and check:

```bat
python --version
pip --version
```

You should see something like `Python 3.13.x`. If you get "python is not recognized", re-run the installer, choose *Modify*, and tick *Add Python to environment variables*.

## 2. Install VS Code (5 min)

1. Download from <https://code.visualstudio.com/> and install (tick "Add to PATH" and "Open with Code").
2. Open VS Code → Extensions (Ctrl+Shift+X) → install **Python** (by Microsoft).

## 3. Get the course folder and make a virtual environment (10 min)

A **virtual environment ("venv")** is a private box of Python libraries just for this project, so projects never fight over versions. Think of it as a separate PAD *environment* for this course.

```bat
cd C:\Users\<you>\Documents\playwright-course
python -m venv .venv
.venv\Scripts\activate
```

Your prompt now starts with `(.venv)`. You must **activate** it every time you open a new terminal for this project. (In VS Code: Ctrl+Shift+P → *Python: Select Interpreter* → pick the one in `.venv`, and new terminals activate it automatically.)

> If PowerShell says "running scripts is disabled", run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and try again, or just use Command Prompt.

## 4. Install Playwright and its browsers (10 min)

```bat
pip install playwright openpyxl
playwright install chromium
```

- `pip` is Python's app store for libraries. `openpyxl` is for Excel (Lesson 05).
- `playwright install chromium` downloads a browser that Playwright controls directly. No browser extension, unlike PAD.

## 5. Start the practice portal (keep this running)

The portal is just HTML files. Python has a tiny web server built in:

```bat
cd practice-portal
python -m http.server 8000
```

Open <http://localhost:8000> in your normal browser: you should see the **ProviderGate** sign-in page. Leave this terminal open; open a **second** terminal for your scripts (and activate the venv there too).

> **Why a server and not double-clicking the HTML?** Logins are remembered in the browser's storage, and that works reliably only on an `http://` address. Every script reads the address from `BASE_URL` (default `http://localhost:8000`). Later you can point it at the GitHub Pages copy: `set BASE_URL=https://<you>.github.io/practice-portal`.

## 6. Your first script

Create `first.py`:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:                         # start Playwright
    browser = p.chromium.launch(headless=False)      # PAD: Launch new browser (visible)
    page = browser.new_page()                        # a fresh tab
    page.goto("http://localhost:8000/index.html")    # PAD: Go to web page
    print("Title:", page.title())                    # PAD: Get details of web page
    page.screenshot(path="login.png")                # PAD: Take screenshot
    browser.close()                                  # PAD: Close web browser
```

Run it: `python first.py`. A browser flashes open, the title prints, and `login.png` appears.

**Words you just met**
- `with ... as p:` means "start Playwright, and clean it up automatically when the block ends".
- `headless=False` means *show the window*. `headless=True` runs invisibly, which is how unattended bots run (like PAD unattended mode).
- Indentation (4 spaces) is how Python knows which lines belong to the `with` block. In PAD the designer does this for you; in Python the spaces **are** the structure.

**Sync vs async:** Playwright has two styles. We use the **sync API** (`playwright.sync_api`) everywhere: each line finishes before the next starts, exactly like PAD actions.

## Exercises

1. Open the login page and **print its title**. Make the script stop with an error if the title does not contain "Sign in" (`assert "Sign in" in title`).
2. Read the practice **username, password and OTP** printed on the page (`data-testid` values `demo-username`, `demo-password`, `demo-otp`) and print them.
3. Save a **full-page** screenshot to `output/lesson01_login.png` (`full_page=True`).

Solution: [`solutions/01_setup_first_script.py`](../solutions/01_setup_first_script.py)

Tip: all solution files open a visible browser. To run them invisibly: `set HEADLESS=1`. To slow them down so you can watch: `set SLOW_MO=500`.
