import requests
import os
from datetime import datetime

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK is not set!")

URL = "https://www.squishmart.com/products.json?limit=250"

EXCLUDE = ["needoh", "dumpling"]

# 🧠 memory (resets each GitHub run, but fine for daily summary logic)
previous_stock = {}

daily_new = []
daily_restocks = []

def send(message):
    requests.post(WEBHOOK_URL, json={"content": message})

def send_summary():
    today = datetime.now().strftime("%Y-%m-%d")

    msg = f"📊 **Daily Squishy Summary ({today})**\n\n"

    if not daily_new and not daily_restocks:
        msg += "No new squishies or restocks today 💤"
    else:
        if daily_new:
            msg += "🆕 **New Drops:**\n"
            msg += "\n".join(daily_new[:10]) + "\n\n"

        if daily_restocks:
            msg += "🔄 **Restocks:**\n"
            msg += "\n".join(daily_restocks[:10])

    send(msg)

def check():
    global previous_stock, daily_new, daily_restocks

    try:
        r = requests.get(
            URL,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if r.status_code != 200:
            print("Bad response:", r.status_code)
            return

        data = r.json()

        current_stock = {}

        for product in data.get("products", []):
            name = product["title"].lower()

            if any(word in name for word in EXCLUDE):
                continue

            pid = product["id"]
            link = f"https://www.squishmart.com/products/{product['handle']}"

            stock = sum(v.get("inventory_quantity", 0) for v in product.get("variants", []))

            current_stock[pid] = stock

            # 🆕 NEW PRODUCT
            if pid not in previous_stock:
                msg = f"🆕 {product['title']}\n{link}"
                send(msg)
                daily_new.append(product["title"])
                continue

            # 🔄 RESTOCK
            if previous_stock[pid] == 0 and stock > 0:
                msg = f"🔄 RESTOCK: {product['title']}\n{link}"
                send(msg)
                daily_restocks.append(product["title"])

        previous_stock = current_stock

    except Exception as e:
        print("Bot error:", e)

def maybe_send_daily_summary():
    # ⚠️ runs only once per execution
    # (GitHub runs every 30 min, so this behaves like daily summary spam unless we gate it)
    now = datetime.now()

    # Example: send summary at 11:59 PM server time
    if now.hour == 23 and now.minute < 30:
        send_summary()

check()
maybe_send_daily_summary()