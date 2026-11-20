# Lesson 03 · Fill and click: logging in

> **Goal:** type into text boxes, press buttons, follow links, and check the result. By the end you can log in with the OTP step.

## PAD → Playwright mapping

| PAD | Playwright |
|---|---|
| **Populate text field on web page** | `locator.fill("text")` (clears the box first, then types) |
| Populate text field with "Emulate typing" ON | `locator.press_sequentially("text", delay=50)` (for fussy boxes that need real keystrokes) |
| **Press button on web page** | `locator.click()` |
| **Click link on web page** | `page.get_by_role("link", name="...").click()` |
| **Send keys** {Enter} / {Tab} | `locator.press("Enter")` / `locator.press("Tab")` |
| **Focus text field** | `locator.focus()` |
| **Get details of element** → Own text | `locator.inner_text()` |
| **Get details of element** → Value (text box) | `locator.input_value()` |
| **If web page contains** element/text | `expect(locator).to_be_visible()` / `.to_have_text("...")` |

## How Playwright clicks (and why it's less flaky than PAD)

Before every `fill()` or `click()`, Playwright automatically waits until the element is:
**attached** to the page → **visible** → **stable** (not animating) → **enabled** → **not covered** by something else.

That's why you rarely need "Wait" actions. On the portal, the OTP box appears ~1 second after *Sign in*, and `page.get_by_label("One-time passcode").fill(...)` simply waits for it.

## `expect`: the "check" step

`expect(...)` is an *assertion*: it says "this must be true". It keeps retrying for up to 5 seconds and stops the script with a clear message if it never becomes true.

```python
from playwright.sync_api import expect
expect(page.get_by_test_id("welcome-message")).to_have_text("Welcome back, Provider Admin")
```

## Example: log in with OTP

```python
page.goto(f"{BASE_URL}/index.html")
page.get_by_label("User ID").fill("provider.admin")
page.get_by_label("Password").fill("Enroll@2026")
page.get_by_role("button", name="Sign in").click()

page.get_by_label("One-time passcode").fill("482913")   # waits for the OTP step to appear
page.get_by_role("button", name="Verify").click()

expect(page.get_by_test_id("welcome-message")).to_be_visible()
```

### Your first "subflow"

You'll log in at the start of nearly every lesson, so the solutions keep these steps in a function inside [`solutions/portal_helpers.py`](../solutions/portal_helpers.py):

```python
def login(page, base_url):
    ...the steps above...

login(page, BASE_URL)     # PAD: Run subflow "Login"
```

A **function** = a PAD **subflow**. `def` creates it; the names in brackets are its *input variables*; `return value` is its *output variable*.

## Exercises

1. Type the right User ID but a **wrong password**, click *Sign in*, and check the red error says `Invalid user ID or password. Please try again.`
2. Do the **full login with OTP** and check the welcome message is `Welcome back, Provider Admin`.
3. From the dashboard, click **License lookup** in the *top menu* (hint: `page.get_by_role("navigation", name="Main")`), search NPI `1104332181`, and print the license status (expected: `Active`).

Solution: [`solutions/03_fill_and_click.py`](../solutions/03_fill_and_click.py)
