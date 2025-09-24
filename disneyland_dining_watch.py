"""
Disneyland Dining Watcher / Scraper

NOTE: It should be obvious from the title and file name, but this only works
for Disneyland and Disneyland's website. I've not added functionality to
switch between the different parks (Disney World, Euro Disney, etc.) and
do not plan to at the current time.

Scrapes Disneyland dining reservation availability for selected restaurants
and sends an SMS alert when times are found.

Restaurant-Selection:
- To edit which restaurants you wish to recieve notifications for, you must manually edit
the list "target_restaurants" under the main function. 

Security:
- Twilio credentials and phone numbers are read from the "phone.JSON" config
file. You must update that file with your own phone and Twilio information for 
texting notifications to work.

Usage:
    python disneyland_dining_watch.py
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Sequence

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from twilio.rest import Client


# ------------------------------------------------------------------------------
# Selenium stuff 
# ------------------------------------------------------------------------------

def build_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver


# ------------------------------------------------------------------------------
# Webpage Scraping Stuff
# ------------------------------------------------------------------------------

def select_date_and_time(driver, date_str: str, time_index: int, wait: WebDriverWait) -> None:
    date_input = wait.until(EC.element_to_be_clickable((By.ID, "diningAvailabilityForm-searchDate")))
    date_input.click()
    date_input.clear()
    date_input.send_keys(date_str)

    time_base = wait.until(EC.element_to_be_clickable((By.ID, "diningAvailabilityForm-searchTimeid-base")))
    time_base.click()

    time_choice = wait.until(EC.element_to_be_clickable((By.ID, f"diningAvailabilityForm-searchTime-{time_index}")))
    time_choice.click()

    search_btn = wait.until(EC.element_to_be_clickable((By.ID, "dineAvailSearchButton")))
    search_btn.click()


def parse_availability(driver, wait: WebDriverWait) -> Dict[str, List[str]]:
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card.dining.show")))
    found: Dict[str, List[str]] = {}

    for card in driver.find_elements(By.CSS_SELECTOR, ".card.dining.show"):
        try:
            name = card.find_element(By.CSS_SELECTOR, ".cardName").text.strip()
        except Exception:
            continue

        times: List[str] = []
        for t in card.find_elements(By.CSS_SELECTOR, "[data-servicedatetime]"):
            raw = (t.get_attribute("data-servicedatetime") or "").strip()
            if len(raw) >= 16:
                hhmm = raw[11:16]
                try:
                    datetime.strptime(hhmm, "%H:%M")
                    times.append(hhmm)
                except Exception:
                    pass

        if times:
            found[name] = times

    return found


def filter_targets(availability: Dict[str, List[str]], targets: Sequence[str]) -> Dict[str, List[str]]:
    wanted = {t.lower() for t in targets}
    return {name: times for name, times in availability.items() if name.lower() in wanted}


# ------------------------------------------------------------------------------
# SMS Notification Config
# ------------------------------------------------------------------------------

def send_sms(message: str, phone_info: dict) -> None:
    client = Client(phone_info["TWILIO_ACCOUNT_SID"], phone_info["TWILIO_AUTH_TOKEN"])
    client.messages.create(
        to=phone_info["TWILIO_TO_NUMBER"],
        from_=phone_info["TWILIO_FROM_NUMBER"],
        body=message,
    )


def format_alert(date_str: str, time_idx: int, results: Dict[str, List[str]]) -> str:
    lines = [f"Disney Dining openings for {date_str} (time option #{time_idx}):"]
    for name, times in results.items():
        lines.append(f"- {name}: {', '.join(times)}")
    return "\n".join(lines)


# ------------------------------------------------------------------------------
# Main function. The big cheese. The one and only. 
# ------------------------------------------------------------------------------

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    dates_to_check = ["01/04/2022", "01/05/2022"]
    time_indices = [0, 1, 2]

    # EDIT THIS LIST with the names of your preferred disneyland
    # restaurants to recieve notifications for them. 
    target_restaurants = [
        "Blue Bayou Restaurant",
        "Cafe Orleans",
        "Carthay Circle Restaurant",
        "Oga's Cantina at the Disneyland Resort",
    ]

    try:
        phone_info = load_phone_info()
    except Exception as err:
        logging.error("Failed to load phone.json: %s", err)
        return 2

    driver = build_driver(headless=True)
    wait = WebDriverWait(driver, 20)
    driver.get("https://disneyland.disney.go.com/dining/#/reservations-accepted/")

    try:
        for date_str in dates_to_check:
            for time_idx in time_indices:
                try:
                    select_date_and_time(driver, date_str, time_idx, wait)
                    availability = parse_availability(driver, wait)
                    hits = filter_targets(availability, target_restaurants)
                    if hits:
                        msg = format_alert(date_str, time_idx, hits)
                        logging.info("Matches found:\n%s", msg)
                        send_sms(msg, phone_info)
                    else:
                        logging.info("No matches for %s (time option %d).", date_str, time_idx)
                except Exception as exc:
                    logging.exception("Error while checking %s (time %d): %s", date_str, time_idx, exc)
    finally:
        driver.quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())