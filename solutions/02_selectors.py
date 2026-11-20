"""
Lesson 02 - Selectors: finding elements the stable way (solutions)
"""
import os
import re

from playwright.sync_api import expect, sync_playwright

from portal_helpers import HEADLESS, SLOW_MO, login, passed

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def exercise_1(page):
    """Prove the id is dynamic, then find the User ID box 4 stable ways."""
    page.goto(f"{BASE_URL}/index.html")
    box = page.locator("input[name='username']")
    first_id = box.get_attribute("id")
    page.reload()
    second_id = box.get_attribute("id")
    print("id on load 1:", first_id)
    print("id on load 2:", second_id)
    assert first_id != second_id, "ids should change on every load - that's the trap!"

    stable_ways = {
        "get_by_label": page.get_by_label("User ID"),
        "get_by_placeholder": page.get_by_placeholder("Enter user ID"),
        "name attribute": page.locator("[name='username']"),
        "get_by_test_id": page.get_by_test_id("username-input"),
    }
    for how, loc in stable_ways.items():
        assert loc.count() == 1, how
        print(f"  {how:20} -> found exactly 1 element")
    passed("Exercise 1 - dynamic id spotted, 4 stable selectors work")


def exercise_2(page):
    """Click the 'License lookup' tile by its text/test id, never by position."""
    for attempt in range(2):
        page.goto(f"{BASE_URL}/dashboard.html")
        tiles = page.get_by_test_id("quick-links").locator("a")
        print(f"  visit {attempt + 1}: 1st tile is '{tiles.first.locator('strong').inner_text()}'")
    # The top menu ALSO has a "License lookup" link, so search only inside the tiles area:
    tiles_area = page.get_by_test_id("quick-links")
    tiles_area.get_by_role("link", name=re.compile(r"^License lookup")).click()
    # (page.get_by_test_id("tile-license").click() would work just as well)
    expect(page).to_have_url(f"{BASE_URL}/license-lookup.html")
    passed("Exercise 2 - clicked the right tile even though the order shuffles")


def exercise_3(page):
    """Use get_by_role for a button and filter table rows by text."""
    page.goto(f"{BASE_URL}/providers.html")
    expect(page.get_by_role("button", name="Filter by name")).to_be_visible()
    # Patel is on page 3 of the table (sorted by last name), so first go to page 3
    page.get_by_role("button", name="Page 3", exact=True).click()
    patel_row = page.get_by_test_id("provider-row").filter(has_text="Patel")
    expect(patel_row).to_have_count(1)
    print("  Patel row:", patel_row.inner_text().replace("\t", " | "))
    passed("Exercise 3 - get_by_role + filter(has_text=...)")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = browser.new_page()
        exercise_1(page)
        login(page, BASE_URL)   # ready-made helper; Lesson 03 shows how it works
        exercise_2(page)
        exercise_3(page)
        browser.close()
