Disneyland Dining Watcher / Scraper
====================================

This is a Python script that scrapes the Disneyland dining reservation website
for availability at specific restaurants and sends you a text message (via Twilio)
when times are found.

IMPORTANT NOTES
---------------
- This only works for **Disneyland** and Disneyland’s website.
  It does NOT currently support Disney World, Euro Disney, or other parks.
- You must set up a Twilio account and edit the included "phone.json" file
  with your own Twilio account info and phone numbers for texting to work.

How it Works
------------
1. The script uses Selenium (a web automation library) to load the Disneyland
   dining reservation page and search for available times.
2. It checks the restaurants you list in the code under "target_restaurants".
3. If it finds openings, it sends you an SMS message using Twilio.

Editing Restaurants
-------------------
To change which restaurants you are notified about:
- Open "disneyland_dining_watch.py"
- Find the list called "target_restaurants" in the main() function.
- Replace or add restaurant names (make sure they match how Disneyland lists them).

Configuration (phone.json)
--------------------------
All Twilio and phone info is stored in a JSON file called "phone.json".
You must edit this file with your own values before running the script.

Example phone.json:

{
  "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "TWILIO_AUTH_TOKEN": "your_auth_token_here",
  "TWILIO_TO_NUMBER": "+1YOUR_CELL_PHONE",
  "TWILIO_FROM_NUMBER": "+1YOUR_TWILIO_NUMBER"
}

Dependencies
------------
You will need to install:
- selenium
- twilio

You also need to have Chrome installed and the matching ChromeDriver.

Usage
-----
From the same folder as "disneyland_dining_watch.py" and "phone.json", run:

    python disneyland_dining_watch.py

If times are found for your chosen restaurants, you’ll get a text message.