# Lesson 11 · Codegen (the recorder) and the Trace Viewer (the flight recorder)

> **Goal:** let Playwright write the first draft of your script, then debug failures by replaying exactly what happened, step by step, with screenshots.

## PAD → Playwright mapping

| PAD | Playwright |
|---|---|
| **Recorder** (record web actions) | `playwright codegen <url>` |
| Add UI element → pick on screen | *Pick locator* button in the codegen / Inspector window |
| Run flow step-by-step / breakpoints | `page.pause()` in your code, or run with `PWDEBUG=1` (Playwright Inspector) |
| Run history / flow run details | **Trace Viewer**: `playwright show-trace trace.zip` |
| Screenshots in error handlers | trace contains a screenshot + full page snapshot **for every step** |

## Codegen: record a script

With the portal running:

```bat
playwright codegen http://localhost:8000/index.html
```

Two windows open: a browser and the **Playwright Inspector**. Log in, open License lookup, pick state TX, click Search. Watch Python code appear as you click. Set the *Target* dropdown to **Python** (sync, not "Library async/pytest" variants).

Useful options:

```bat
playwright codegen --target python -o recorded.py http://localhost:8000/index.html   # save to a file
playwright codegen --save-storage=auth.json http://localhost:8000/index.html         # save the login session
playwright codegen --load-storage=auth.json http://localhost:8000/dashboard.html     # start already logged in
```

### Clean up what codegen gives you

Codegen is a great *starting point*, like PAD's recorder, but it is not the finished bot:

| Codegen wrote | Change it to | Why |
|---|---|---|
| `page.get_by_role("textbox", name="User ID").click()` then `.fill(...)` | just `.fill(...)` | extra clicks add nothing |
| Hard-coded `"provider.admin"` / password | variables / config / env vars | never hard-code secrets |
| `page.locator("#ctl00_Main_txtUserId_x8k2")` (rare) | `get_by_label(...)` / `get_by_test_id(...)` | dynamic id trap (Lesson 02) |
| `.nth(2)` | `.filter(has_text=...)` | ordinal trap |
| No checks at the end | `expect(...)` | a bot should *prove* it worked |
| One long block | functions (`login`, `lookup`) | reuse = PAD subflows |

## Trace Viewer: see exactly what happened

Add tracing around your steps:

```python
context = browser.new_context()
context.tracing.start(screenshots=True, snapshots=True, sources=True)
page = context.new_page()
# ... your steps ...
context.tracing.stop(path="output/trace.zip")
```

Open it:

```bat
playwright show-trace output/trace.zip
```

You get a timeline. Click any action to see **before/after** snapshots of the page (you can even inspect the HTML), the locator used, how long it waited, console errors, and network calls. It's the single best tool for "it failed at 3 AM and I wasn't watching".

**Trace only on failure** to save disk space on big runs: start tracing, and in your `except` block call `tracing.stop(path=...)`; on success call `tracing.stop()` with no path (the trace is thrown away).

## Debug mode

```bat
set PWDEBUG=1
python my_script.py
```

The browser opens with the Inspector, paused before the first action. Use *Step over* to run one action at a time, like PAD's *Run next action*. Or put `page.pause()` where you want to stop.

## Exercises

1. Record *log in → License lookup → state TX → Search* with codegen. Clean it up using the table above, and add `expect(page.get_by_test_id("lookup-count")).to_have_text("4 records found")`.
2. Run your cleaned script with **tracing on** and open the trace with `playwright show-trace`. Find the step where the OTP box appeared and check how long *fill* waited.
3. Make a script that keeps a trace **only when it fails** (try clicking a button that doesn't exist).

Solution: [`solutions/11_codegen_trace.py`](../solutions/11_codegen_trace.py)
