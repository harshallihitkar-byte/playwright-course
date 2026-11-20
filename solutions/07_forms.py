"""
Lesson 07 - Dropdowns, radio buttons, checkboxes, dates and file uploads (solutions)
"""
import os
import re

from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, OUTPUT_DIR, SLOW_MO, login, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def exercise_1(page):
    """Step 1: text boxes, a date and two dropdowns."""
    page.goto(f"{BASE_URL}/enroll.html")
    page.get_by_label("First name").fill("Harshal")
    page.get_by_label("Last name").fill("Practice")
    page.get_by_label("NPI").fill("1234567890")
    page.get_by_label("Date of birth").fill("1995-04-12")       # date inputs ALWAYS take YYYY-MM-DD
    page.get_by_label("Provider type").select_option(label="Nurse Practitioner (NP)")   # by visible text
    page.get_by_label("Primary specialty").select_option("Family Medicine")             # by value
    assert page.get_by_label("Provider type").input_value() == "NP"
    page.get_by_role("button", name="Next").click()
    expect(page.get_by_test_id("step-2")).to_be_visible()
    passed("Exercise 1 - step 1 filled (text, date, dropdowns)")


def exercise_2(page):
    """Step 2: radio button, checkboxes and another date. First try Next with nothing filled."""
    page.get_by_role("button", name="Next").click()
    expect(page.get_by_test_id("form-error")).to_have_text("Choose an enrollment type.")
    print("  validation message seen:", page.get_by_test_id("form-error").inner_text())

    page.get_by_label("Revalidation").check()                  # radio button
    page.get_by_label("Practice state").select_option("TX")
    page.get_by_label("Effective date").fill("2027-01-01")
    page.get_by_label("In-person visits").check()              # checkboxes
    page.get_by_label("Telehealth").check()
    page.get_by_label("Accepting new patients").set_checked(True)   # set_checked = "make it this value"
    expect(page.get_by_label("Telehealth")).to_be_checked()
    expect(page.get_by_label("Home visits")).not_to_be_checked()
    page.get_by_role("button", name="Next").click()
    expect(page.get_by_test_id("step-3")).to_be_visible()
    passed("Exercise 2 - radio, checkboxes, date")


def exercise_3(page):
    """Step 3: upload files (impossible with PAD's JavaScript), then review and submit."""
    license_pdf = OUTPUT_DIR / "sample_license.pdf"
    license_pdf.write_bytes(b"%PDF-1.4\n% fake practice license\n")
    page.get_by_label("State license copy").set_input_files(license_pdf)     # from a file on disk
    page.get_by_label("W-9 form").set_input_files(                          # or straight from memory
        {"name": "w9.pdf", "mimeType": "application/pdf", "buffer": b"%PDF-1.4 fake w9"}
    )
    expect(page.get_by_test_id("uploaded-files")).to_have_text("sample_license.pdf, w9.pdf")
    page.get_by_role("button", name="Next").click()

    expect(page.get_by_test_id("review-services")).to_have_text("In-person visits, Telehealth")
    page.get_by_label("I attest").check()
    page.get_by_role("button", name="Submit application").click()
    conf = page.get_by_test_id("confirmation-id")
    expect(conf).to_have_text(re.compile(r"^ENR-\d{4}-\d{6}$"))
    print("  Application ID:", conf.inner_text())
    passed("Exercise 3 - uploads + submit, confirmation captured")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = browser.new_page()
        login(page, BASE_URL)
        exercise_1(page)
        exercise_2(page)
        exercise_3(page)
        browser.close()
