import requests
import json
import os

# ======================
# CONFIG
# ======================

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK is not set!")

URL = "https://www.squishmart.com/products.json?limit=250"

EXCLUDE = ["needoh", "dumpling"]

# ======================
# ENSURE FILE EXISTS
# ======================

if not os.path.exists("seen.json"):
    with open("seen.json", "w") as f:
        json.dump([], f)

try:
    with open("seen.json", "r") as f:
        seen_ids = set(json.load(f))
except:
    seen_ids = set()

# ======================
# DISCORD SEND (DEBUG)
# ======================

def send(name, link):
    print("➡️ Sending to Discord...")

    try:
        res = requests.post(
            WEBHOOK_URL,
            json={"content": f"🧸 {name}\n{link}"}
        )

        print("Discord status:", res.status_code)

        if res.status_code != 204:
            print("⚠️ Discord response:", res.text)

    except Exception as e:
        print("❌ Discord error:", e)

# ======================
# SAVE STATE
# ======================

def save():
    with open("seen.json", "w") as f:
        json.dump(list(seen_ids), f)

# ======================
# MAIN CHECK
# ======================

def check():
    global seen_ids

    try:
        print("🔍 Checking Squishmart...")

        r = requests.get(
            URL,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        print("Shopify status:", r.status_code)

        if r.status_code != 200:
            print("Bad response:", r.text)
            return

        data = r.json()

        for product in data.get("products", []):
            name = product["title"].lower()
            pid = product["id"]

            if any(word in name for word in EXCLUDE):
                continue

            if pid not in seen_ids:
                seen_ids.add(pid)

                link = f"https://www.squishmart.com/products/{product['handle']}"

                print("🆕 New product found:", name)

                send(product["title"], link)

        save()

        # ======================
        # 🔥 TEST ALERT (REMOVE LATER)
        # ======================
        send("TEST ALERT - BOT WORKING", "https://squishmart.com")

    except Exception as e:
        print("❌ Bot error:", e)

# RUN
check()