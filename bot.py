import requests
import os

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK is not set!")

URL = "https://www.squishmart.com/products.json?limit=250"

EXCLUDE = ["needoh", "dumpling"]

# In-memory tracking (resets each run, but avoids Git entirely)
seen_ids = set()

def send(name, link):
    print("➡️ Sending:", name)

    res = requests.post(
        WEBHOOK_URL,
        json={"content": f"🧸 {name}\n{link}"}
    )

    print("Discord status:", res.status_code)
    print("Response:", res.text)
    try:
        res = requests.post(
            WEBHOOK_URL,
            json={"content": f"🧸 New Squishy Found!\n{name}\n{link}"}
        )
        print("Discord status:", res.status_code)
    except Exception as e:
        print("Discord error:", e)

def check():
    global seen_ids

    try:
        r = requests.get(
            URL,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        print("Shopify status:", r.status_code)

        if r.status_code != 200:
            return

        data = r.json()

        for product in data.get("products", []):
            name = product["title"].lower()
            pid = product["id"]

            if any(word in name for word in EXCLUDE):
                continue

            # prevents spam within same run
            if pid in seen_ids:
                continue

            seen_ids.add(pid)

            link = f"https://www.squishmart.com/products/{product['handle']}"

            send(product["title"], link)

    except Exception as e:
        print("Bot error:", e)

check()

send("TEST ALERT - IF YOU SEE THIS, DISCORD WORKS", "https://example.com")

