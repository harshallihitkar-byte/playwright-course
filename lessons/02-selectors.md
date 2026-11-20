# Lesson 02 · Selectors: finding elements the stable way

> **Goal:** stop bots from breaking when the page reloads. Learn the Playwright "locators" that replace PAD UI elements.

## PAD → Playwright mapping

| PAD | Playwright |
|---|---|
| UI element in the *UI elements* pane | a **locator**: `page.get_by_...(...)` |
| Selector builder / `input[Id="ctl00_Main_txtUserId_8f3k2"]` | `page.get_by_label("User ID")` |
| Editing the selector text by hand | Choosing a better `get_by_*` method |
| Selector with `:eq(2)` / "nth element" | **Avoid.** Use text, role, or a test id instead |
| Several selectors on one UI element (fallbacks) | `locator.or_(other_locator)` |
| "Element not found" error | Playwright waits up to 5 s for the element, then raises `TimeoutError` |

## The problem: dynamic IDs

Open the portal's sign-in page, right-click the *User ID* box → *Inspect*. You'll see something like:

```html
<input id="ctl00_Main_txtUserId_qskpfxjrn" name="username" placeholder="Enter user ID" data-testid="username-input">
```

Reload the page: the id changes to `..._gipjkxjt6`. ASP.NET, Salesforce and many payer portals do exactly this. If your PAD selector used `Id`, it breaks on every visit. That's the classic "it worked yesterday" bug.

## The fix: pick the most *meaningful* attribute

Use this order of preference:

| Rank | Locator | Example on the portal | Why |
|---|---|---|---|
| 1 | `get_by_role(role, name=...)` | `page.get_by_role("button", name="Sign in")` | How a human sees it: "the Sign in button" |
| 2 | `get_by_label("...")` | `page.get_by_label("User ID")` | The text label next to a field |
| 3 | `get_by_placeholder("...")` | `page.get_by_placeholder("Enter user ID")` | Grey hint text inside the box |
| 4 | `get_by_text("...")` | `page.get_by_text("No providers match")` | Visible text for non-buttons |
| 5 | `get_by_test_id("...")` | `page.get_by_test_id("username-input")` | `data-testid` attributes that developers add for testing. Rock solid when they exist |
| 6 | CSS by `name` / `aria-label` | `page.locator("[name='username']")` | Stable attributes, but not visible to users |
| ✗ | dynamic id, `nth(3)`, long XPath | `#ctl00_Main_txtUserId_qskpfxjrn`, `//div[3]/table/tr[2]` | Break on reload or when the layout changes |

**Common roles:** `button`, `link`, `textbox`, `checkbox`, `radio`, `combobox` (dropdown), `row`, `cell`, `heading`, `dialog`, `navigation`.

## Narrowing down: locators inside locators

The portal's top menu **and** the dashboard tiles both have a "License lookup" link. A plain `get_by_role("link", name="License lookup")` would find 2 and Playwright refuses to guess ("strict mode violation"). Narrow the search area first, just like picking a parent element in PAD:

```python
tiles = page.get_by_test_id("quick-links")                   # the tiles area only
tiles.get_by_role("link", name=re.compile("^License lookup")).click()
```

Filtering rows by their text, a lifesaver for tables:

```python
row = page.get_by_test_id("provider-row").filter(has_text="Patel")
```

## The ordinal trap

The dashboard shuffles its tiles on every visit. A PAD recording that clicked "the 3rd tile" works once, then opens a random page. Always describe **what** the element is, never **where** it is.

## Example

```python
page.goto(f"{BASE_URL}/index.html")
user_box = page.get_by_label("User ID")
print(user_box.get_attribute("id"))   # changes every load. Don't use it!
print(user_box.count())               # 1  -> the locator is unique
```

## Exercises

1. Print the User ID box's `id` twice (reload in between) to prove it changes. Then find the same box **four stable ways**: label, placeholder, `name` attribute, test id. Check that each finds exactly 1 element (`.count() == 1`).
2. On the dashboard, click the **License lookup tile** (not the menu link) without using its position. Run it twice and notice the tile order is different each time.
3. On *Provider search*, find the "Filter by name" button with `get_by_role`, go to page 3 and find the row for **Patel** with `.filter(has_text=...)`.

Solution: [`solutions/02_selectors.py`](../solutions/02_selectors.py)

**Pro tip:** `playwright codegen http://localhost:8000` opens a browser with a **Pick locator** button: hover any element and it shows the best `get_by_*` locator for it (Lesson 11).
