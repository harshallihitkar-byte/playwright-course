# Lesson 09 · Login with OTP, then reuse the session (storage_state)

> **Goal:** log in (with the OTP) **once**, save the session to a file, and let later runs skip the login entirely, the way a browser "remembers" you.

## PAD → Playwright mapping

| PAD | Playwright |
|---|---|
| Use a browser **profile** that stays logged in | `context.storage_state(path="auth_state.json")` to save, `browser.new_context(storage_state="auth_state.json")` to reuse |
| Login subflow called at the start of every flow | `get_logged_in_context(browser)`: log in only if the saved session no longer works |
| Read OTP from Outlook / authenticator in a separate subflow | a `get_otp()` function. The practice portal uses a fixed code `482913` |
| Credential stored in Power Automate / Key Vault | environment variable (`os.getenv("PORTAL_PASSWORD")`) or Windows Credential Manager. **Never commit passwords to Git** |

## Browser → context → page

| Playwright | Think of it as |
|---|---|
| `browser` | The Chrome application |
| `context` | A fresh **incognito profile** with its own cookies and logins |
| `page` | A tab in that profile |

`browser.new_page()` is a shortcut that makes a context + page in one go. For sessions you create the context yourself.

## Save the session

```python
context = browser.new_context()
page = context.new_page()
login(page, BASE_URL)                             # user ID, password, OTP
context.storage_state(path="output/auth_state.json")
```

The JSON file holds **cookies and localStorage**, i.e. the "I'm logged in" token. Treat it like a password: it's in `.gitignore` for a reason.

## Reuse it

```python
context = browser.new_context(storage_state="output/auth_state.json")
page = context.new_page()
page.goto(f"{BASE_URL}/license-lookup.html")      # straight in, no login, no OTP
```

## Smart login: reuse if valid, otherwise log in again

Sessions expire (this portal: after 8 hours; real portals: often 15–30 minutes of inactivity). Check, don't assume:

```python
def get_logged_in_context(browser):
    if STATE_FILE.exists():
        context = browser.new_context(storage_state=str(STATE_FILE))
        page = context.new_page()
        page.goto(f"{BASE_URL}/dashboard.html")
        if "index.html" not in page.url:          # not bounced back to the sign-in page
            return context, page
        context.close()
    context = browser.new_context()
    page = context.new_page()
    login(page, BASE_URL)
    context.storage_state(path=str(STATE_FILE))
    return context, page
```

## About real OTPs

Real portals send the code by SMS, email or an authenticator app. Common patterns:
- **Email OTP:** read the latest email with Microsoft Graph / IMAP in `get_otp()`, pull out the 6 digits with a regular expression.
- **Authenticator (TOTP):** if your company allows it, the `pyotp` library can generate the same codes from the secret key.
- **Human-in-the-loop:** `input("Enter the OTP: ")` pauses the script and you type it. Combined with storage_state you only do this once a day.

Always follow the portal's terms of use and your company's security policy for automating MFA.

## Exercises

1. Log in with OTP and save the session to `output/auth_state.json`.
2. In a **new** context loaded from that file, open *License lookup* directly and prove you were **not** sent back to the sign-in page.
3. Write `get_logged_in_context()`. Test it twice: once with a valid file, once after overwriting the file with an empty session `{"cookies": [], "origins": []}`. It should log in again by itself.

Solution: [`solutions/09_login_storage_state.py`](../solutions/09_login_storage_state.py)
