# Lesson 10 · Error handling, screenshots, retries and logging

> **Goal:** a bot that survives a bad row, retries a flaky portal, leaves a screenshot when something breaks, and writes a log you can read the next morning.

## PAD → Python mapping

| PAD | Python |
|---|---|
| **On block error** (wrap a group of actions) | `try:` … `except SomeError:` … |
| On error → **Continue flow run** / go to next action | `except ...: log it` then carry on (inside the `for` loop) |
| On error → **Retry action** N times with interval | a `for attempt in range(1, N+1):` loop with `try/except` and `time.sleep(...)` |
| On error → **Throw error** / stop | `raise` |
| *Finally* block (always runs) | `finally:` |
| **Get last error** | `except Exception as exc:` then `str(exc)` |
| **Take screenshot** in the error handler | `page.screenshot(path=...)` inside `except` |
| **Write text to file** (log) | the `logging` module: `log.info(...)`, `log.warning(...)`, `log.error(...)` |
| "Element not found" / action timed out | `playwright.sync_api.TimeoutError` |

## try / except / finally

```python
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

try:
    page.get_by_role("button", name="Approve all").click(timeout=2_000)
except PlaywrightTimeoutError:
    log.warning("Button not there, skipping")
    page.screenshot(path="output/missing_button.png")
finally:
    log.info("step finished")      # runs whether it worked or not
```

Catch the **specific** error you expect when you can. `except Exception` catches everything, which is fine at the "one row" level so one bad provider never stops the other 199.

## Retries with back-off

The license lookup page has a practice switch: add `?flaky=1` to the URL and ~25% of searches fail with *"State board service temporarily unavailable (error 503)"*, just like real state board sites at night.

```python
def with_retry(func, *args, attempts=4, wait_seconds=1.0):
    for attempt in range(1, attempts + 1):
        try:
            return func(*args)                       # success -> leave immediately
        except Exception as exc:
            log.warning("Attempt %d/%d failed: %s", attempt, attempts, exc)
            if attempt == attempts:
                raise                                # give up, let the caller decide
            time.sleep(wait_seconds * attempt)       # wait 1s, 2s, 3s...

status = with_retry(lookup_once, page, "1104332181")
```

Only retry things that can succeed on a second try (timeouts, 503s). Retrying "NPI must be exactly 10 digits" is pointless; that's a data problem to report.

## Logging

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    handlers=[logging.FileHandler("output/bot.log", encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("bot")
log.info("NPI %s -> %s", npi, status)
```

Output: `2026-11-20 17:47:42,160 | INFO    | NPI 1104332181 -> Active`, printed on screen **and** saved to the file. Levels: `DEBUG` < `INFO` < `WARNING` < `ERROR`. Raise `level` to `WARNING` to see only problems.

## Exercises

1. Click a button that doesn't exist with a 2-second timeout; catch the `TimeoutError`, log a warning and save a screenshot.
2. Open `license-lookup.html?flaky=1` and look up 6 NPIs with a retry helper. All 6 must succeed even though the portal fails randomly.
3. Loop over `["1104332181", "12345", "1816184959"]`. The middle one is invalid. Use `try/except` **inside** the loop so the run continues, take a screenshot of the failure, use `finally` to log each finished row, and print a summary *2 ok, 1 failed*.

Solution: [`solutions/10_errors_logging.py`](../solutions/10_errors_logging.py)
