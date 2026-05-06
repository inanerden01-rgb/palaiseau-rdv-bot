import os
import time
import random
import requests
from playwright.sync_api import sync_playwright

URL = os.getenv("RDV_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

NO_SLOT_KEYWORDS = [
    "Aucun rendez-vous disponible",
    "Il n'existe plus de plage horaire libre",
    "Aucun créneau disponible",
]

already_alerted = False


def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )


def check_slots():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle", timeout=60000)

        content = page.content()

        browser.close()

        for keyword in NO_SLOT_KEYWORDS:
            if keyword.lower() in content.lower():
                return False

        return True


print("Bot started")

send_telegram("🟢 Palaiseau RDV Alarm aktif.")

while True:
    try:
        found = check_slots()

        if found and not already_alerted:
            send_telegram(
                f"🚨 SLOT AÇILDI!\n{URL}"
            )
            already_alerted = True

        elif not found:
            already_alerted = False

    except Exception as e:
        print(e)

    time.sleep(random.randint(70, 110))
