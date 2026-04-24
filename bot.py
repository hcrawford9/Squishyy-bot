import requests
import json
import os

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK is not set!")

URL = "https://squishmart.com/products.json?limit=250"

EXCLUDE = ["needoh", "dumpling"]

try:
    with open("seen.json", "r") as f:
        seen_ids = set(json.load(f))
except:
    seen_ids = set()

def send(name, link):
    requests.post(WEBHOOK_URL, json={
        "content": f"🧸 New Squishy Found!\n{name}\n{link}"
    })

def save():
    with open("seen.json", "w") as f:
        json.dump(list(seen_ids), f)

def check():
    global seen_ids

    r = requests.get(URL, timeout=10)

    if r.status_code != 200:
        print("Bad response:", r.status_code)
        return

    data = r.json()

    for product in data["products"]:
        name = product["title"].lower()
        pid = product["id"]

        if any(word in name for word in EXCLUDE):
            continue

        if pid not in seen_ids:
            seen_ids.add(pid)

            link = f"https://squishmart.com/products/{product['handle']}"
            send(product["title"], link)

    save()

check()
