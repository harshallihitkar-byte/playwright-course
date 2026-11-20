"""
License Lookup Checker
======================
Reads providers.xlsx, logs in to the (practice) provider portal with OTP, looks up each
provider's state license, and writes results.xlsx with status, expiry and a
"expiring within 90 days" flag.

Usage:
    python license_checker.py                     # uses config.toml
    python license_checker.py --config my.toml --headed
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
import tomllib
from datetime import date, datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from excel_io import ProviderRow, ResultRow, read_providers, write_results
from portal import LicensePortal
from rules import assess, days_until, is_valid_npi

HERE = Path(__file__).resolve().parent
log = logging.getLogger("license_checker")


def load_config(path: Path) -> dict:
    with open(path, "rb") as fh:
        cfg = tomllib.load(fh)
    # Secrets can come from environment variables instead of the file
    cfg["portal"]["username"] = os.getenv("PORTAL_USERNAME", cfg["portal"]["username"])
    cfg["portal"]["password"] = os.getenv("PORTAL_PASSWORD", cfg["portal"]["password"])
    cfg["portal"]["otp_code"] = os.getenv("PORTAL_OTP", cfg["portal"]["otp_code"])
    cfg["portal"]["base_url"] = os.getenv("BASE_URL", cfg["portal"]["base_url"])
    return cfg


def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler(sys.stdout)])


def check_provider(portal: LicensePortal, p: ProviderRow, cfg: dict, shots_dir: Path, today: date) -> ResultRow:
    run = cfg["run"]
    result = ResultRow(provider=p)

    if p.npi and not is_valid_npi(p.npi):
        result.lookup_result, result.notes = "Invalid input", f"NPI '{p.npi}' is not 10 digits - fix the input file"
        log.warning("Row %d %s: %s", p.row_number, p.name, result.notes)
        return result
    if not p.npi and not p.license_number:
        result.lookup_result, result.notes = "Invalid input", "Needs an NPI or a license number"
        log.warning("Row %d %s: %s", p.row_number, p.name, result.notes)
        return result

    for attempt in range(1, run["max_attempts"] + 1):
        result.attempts = attempt
        try:
            # NPI is the most reliable key; fall back to license number
            if p.npi:
                records = portal.lookup(npi=p.npi, state=p.state)
            else:
                records = portal.lookup(license_number=p.license_number, state=p.state)
            break
        except Exception as exc:  # noqa: BLE001 - we log, screenshot and retry anything
            shot = shots_dir / f"row{p.row_number}_{p.npi or p.license_number}_try{attempt}_{datetime.now():%H%M%S}.png"
            try:
                portal.screenshot(shot)
            except Exception:  # noqa: BLE001
                shot = None
            log.warning("Row %d %s: attempt %d/%d failed: %s (screenshot: %s)", p.row_number, p.name, attempt,
                        run["max_attempts"], str(exc).splitlines()[0], shot)
            if attempt == run["max_attempts"]:
                result.lookup_result = "Error"
                result.notes = f"Failed after {attempt} attempts: {str(exc).splitlines()[0]}"
                return result
            time.sleep(run["retry_backoff_seconds"] * attempt)

    if not records:
        result.lookup_result, result.status = "Not found", "Not found"
    else:
        rec = records[0]
        result.lookup_result = "Found"
        result.status, result.expiry, result.portal_license = rec.status, rec.expiry, rec.license_number
        if p.license_number and p.license_number != rec.license_number:
            result.notes = f"Input license # {p.license_number} differs from portal {rec.license_number}"
        if not p.state:
            p.state = rec.state
        if not p.npi:
            p.npi = rec.npi
            result.notes = "NPI filled in from portal (input had license # only)"
    result.days_left = days_until(result.expiry, today)
    result.expiring_soon, result.action = assess(result.status, result.expiry, today, run["expiry_warning_days"])
    result.checked_at = datetime.now()
    log.info("Row %d %-22s -> %-10s expiry=%s %s", p.row_number, p.name, result.status,
             result.expiry.strftime("%m/%d/%Y") if result.expiry else "-", result.action)
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check provider license status and expiry on the provider portal.")
    ap.add_argument("--config", default=str(HERE / "config.toml"))
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    args = ap.parse_args(argv)

    cfg = load_config(Path(args.config))
    files = {k: (HERE / v) for k, v in cfg["files"].items()}
    setup_logging(files["log_file"])
    run = cfg["run"]

    providers = read_providers(files["input_file"])
    log.info("Loaded %d providers from %s", len(providers), files["input_file"].name)
    today = date.today()
    results: list[ResultRow] = []
    started = time.time()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=run["headless"] and not args.headed, slow_mo=run["slow_mo_ms"])
        portal = LicensePortal(browser, cfg["portal"]["base_url"], cfg["portal"]["lookup_path"],
                               cfg["portal"]["username"], cfg["portal"]["password"], cfg["portal"]["otp_code"],
                               files["state_file"], run["reuse_session"], run["timeout_ms"])
        try:
            portal.start()
            for p in providers:
                results.append(check_provider(portal, p, cfg, files["screenshot_dir"], today))
        except Exception:
            log.exception("Run stopped early")
            try:
                portal.screenshot(files["screenshot_dir"] / f"fatal_{datetime.now():%Y%m%d_%H%M%S}.png")
            except Exception:  # noqa: BLE001
                pass
            raise
        finally:
            # Always save whatever we have, even if the run crashed half-way
            if results:
                write_results(results, files["output_file"], run["expiry_warning_days"])
                log.info("Results written to %s", files["output_file"])
            portal.close()
            browser.close()

    errors = sum(r.lookup_result == "Error" for r in results)
    log.info("Done in %.1fs: %d checked, %d found, %d expiring within %d days, %d errors",
             time.time() - started, len(results), sum(r.lookup_result == "Found" for r in results),
             sum(r.expiring_soon for r in results), run["expiry_warning_days"], errors)
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
