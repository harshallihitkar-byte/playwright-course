"""Everything that touches the browser lives here (Page-Object style)."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, expect

from rules import parse_us_date

log = logging.getLogger("license_checker.portal")


class PortalError(Exception):
    """The portal answered with an error (e.g. 503) - worth retrying."""


@dataclass
class LicenseRecord:
    name: str
    npi: str
    license_number: str
    state: str
    status: str
    expiry: date | None


class LicensePortal:
    def __init__(self, browser: Browser, base_url: str, lookup_path: str, username: str, password: str,
                 otp_code: str, state_file: Path, reuse_session: bool, timeout_ms: int):
        self.browser = browser
        self.base_url = base_url.rstrip("/")
        self.lookup_url = f"{self.base_url}/{lookup_path.lstrip('/')}"
        self.username, self.password, self.otp_code = username, password, otp_code
        self.state_file = state_file
        self.reuse_session = reuse_session
        self.timeout_ms = timeout_ms
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    # ---------- session ----------
    def start(self) -> None:
        if self.reuse_session and self.state_file.exists():
            self._new_context(self.state_file)
            if self._session_is_valid():
                log.info("Reused saved session (skipped login + OTP)")
                return
            log.info("Saved session expired - logging in again")
            self.context.close()
        self._new_context(None)
        self.login()

    def _new_context(self, state: Path | None) -> None:
        self.context = self.browser.new_context(storage_state=str(state) if state else None)
        self.context.set_default_timeout(self.timeout_ms)
        self.page = self.context.new_page()

    def _session_is_valid(self) -> bool:
        self.page.goto(f"{self.base_url}/dashboard.html")
        return "index.html" not in self.page.url

    def login(self) -> None:
        page = self.page
        log.info("Logging in as %s", self.username)
        page.goto(f"{self.base_url}/index.html")
        page.get_by_label("User ID").fill(self.username)
        page.get_by_label("Password").fill(self.password)
        page.get_by_role("button", name="Sign in").click()
        # Either the OTP box appears (good) or a visible error message (bad) - wait for whichever comes first
        login_error = page.locator("[data-testid=login-error]:visible")
        otp_box = page.get_by_label("One-time passcode")
        expect(login_error.or_(otp_box)).to_be_visible()
        if login_error.is_visible():
            raise RuntimeError(f"Login failed: {login_error.inner_text()}")
        otp_box.fill(self.get_otp())
        page.get_by_role("button", name="Verify").click()
        expect(page.get_by_test_id("welcome-message")).to_be_visible()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.context.storage_state(path=str(self.state_file))
        log.info("Login OK, session saved to %s", self.state_file)

    def get_otp(self) -> str:
        """Practice portal: fixed code. Real portal: read it from email/SMS/authenticator here."""
        return self.otp_code

    # ---------- lookup ----------
    def lookup(self, npi: str = "", license_number: str = "", state: str = "") -> list[LicenseRecord]:
        page = self.page
        if not page.url.startswith(self.lookup_url):
            page.goto(self.lookup_url)
            if "index.html" in page.url:            # session timed out mid-run
                log.warning("Session expired mid-run - logging in again")
                self.login()
                page.goto(self.lookup_url)
        page.get_by_role("button", name="Clear").click()
        if npi:
            page.get_by_label("NPI").fill(npi)
        if license_number:
            page.get_by_label("License number").fill(license_number)
        if state:
            page.get_by_label("State").select_option(state)
        page.get_by_role("button", name="Search").click()
        expect(page.get_by_test_id("lookup-loading")).to_be_hidden()

        error = page.get_by_test_id("lookup-error")
        if error.is_visible():
            raise PortalError(error.inner_text())
        expect(page.get_by_test_id("lookup-results-card")).to_be_visible()
        records = []
        for row in page.get_by_test_id("license-row").all():
            records.append(LicenseRecord(
                name=row.get_by_test_id("lic-name").inner_text(),
                npi=row.get_by_test_id("lic-npi").inner_text(),
                license_number=row.get_by_test_id("lic-number").inner_text(),
                state=row.get_by_test_id("lic-state").inner_text(),
                status=row.get_by_test_id("lic-status").inner_text(),
                expiry=parse_us_date(row.get_by_test_id("lic-expiry").inner_text()),
            ))
        return records

    def screenshot(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(path), full_page=True)

    def close(self) -> None:
        if self.context:
            self.context.close()
