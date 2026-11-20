# Lesson 04 · Waits: no more "Wait 5 seconds"

> **Goal:** make bots that are fast when the site is fast and patient when it is slow.

## PAD → Playwright mapping

| PAD | Playwright |
|---|---|
| **Wait** (fixed 5 s) | ❌ `time.sleep(5)` / `page.wait_for_timeout(5000)`, only for debugging |
| **Wait for web page content** → element *appears* | `locator.wait_for()` or `expect(locator).to_be_visible()` |
| **Wait for web page content** → element *disappears* (spinner) | `locator.wait_for(state="hidden")` or `expect(locator).to_be_hidden()` |
| **Wait for web page content** → text appears | `expect(locator).to_contain_text("...")` |
| "Wait for page to load" on Go to web page | `page.goto(url)` already waits for the `load` event; also `page.wait_for_load_state("networkidle")` |
| Wait until URL changes | `page.wait_for_url("**/dashboard.html")` / `expect(page).to_have_url(...)` |
| Timeout setting on an action | `timeout=10_000` (milliseconds) on any call, or `page.set_default_timeout(10_000)` |

## Why fixed waits are bad

The portal's **Status queue** page takes a *random* 1–3 seconds.
- `sleep(2)` fails about half the time (when it takes 2.5 s).
- `sleep(5)` always works but wastes ~3 s every time. Across 200 providers that's 10 minutes of nothing.
- Waiting for the *condition* takes exactly as long as needed.

## Three kinds of waits you'll actually use

```python
# 1) Auto-wait: built into click/fill. Usually all you need.
page.get_by_role("button", name="Refresh queue").click()

# 2) Wait for a spinner to go away
page.get_by_test_id("spinner").wait_for(state="hidden", timeout=10_000)

# 3) Wait for something to become true (retries until true or timeout)
expect(page.get_by_test_id("load-time")).to_contain_text("Loaded in", timeout=10_000)
```

`wait_for(state=...)` accepts `"visible"` (default), `"hidden"`, `"attached"` (in the HTML, maybe invisible) and `"detached"` (removed from the HTML).

**Trap: waiting for the old content.** On *Provider search*, after *Apply filters*, the old table stays on screen for a moment. If you read rows immediately you may read the *old* page. Wait for something that proves the *new* data is there, e.g. the summary text changing:

```python
expect(page.get_by_test_id("results-summary")).to_have_text("Showing 1–1 of 1 providers")
```

## Exercises

1. Open **Status queue**, wait for the spinner to disappear, then check there are **12** rows. Print how long it took.
2. Click **Refresh queue** three times. Each time wait for the spinner to *appear* and then for "Loaded in" text. No sleeps.
3. On **Provider search**, open *Filter by name*, type `pat`, apply, and wait until the summary says `Showing 1–1 of 1 providers`.

Solution: [`solutions/04_waits.py`](../solutions/04_waits.py)
