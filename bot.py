import requests
import os

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK is not set!")

EXCLUDE = ["needoh", "dumpling"]

seen = set()

# =========================
# DISCORD
# =========================
def send(msg):
    try:
        requests.post(WEBHOOK_URL, json={"content": msg})
    except Exception as e:
        print("Discord error:", e)

# =========================
# SQUISHMART (BEST SOURCE)
# =========================
def check_squishmart():
    url = "https://www.squishmart.com/products.json?limit=250"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        for p in data.get("products", []):
            name = p["title"].lower()

            if any(x in name for x in EXCLUDE):
                continue

            pid = f"sm_{p['id']}"

            if pid in seen:
                continue

            seen.add(pid)

            link = f"https://www.squishmart.com/products/{p['handle']}"
            send(f"🧸 Squishmart: {p['title']}\n{link}")

    except Exception as e:
        print("Squishmart error:", e)

# =========================
# FIVE BELOW
# =========================
def check_fivebelow():
    url = "https://www.fivebelow.com/api/search?q=squish"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        items = data.get("items", [])

        for item in items:
            name = item.get("name", "").lower()

            if any(x in name for x in EXCLUDE):
                continue

            pid = f"fb_{item.get('id', name)}"

            if pid in seen:
                continue

            seen.add(pid)

            link = item.get("url", "https://www.fivebelow.com")
            send(f"🧸 Five Below: {item.get('name')}\n{link}")

    except Exception as e:
        print("Five Below error:", e)

# =========================
# TARGET (SEARCH-BASED)
# =========================
def check_target():
    url = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"

    params = {
        "keyword": "squish",
        "count": 20,
        "channel": "web"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        products = data.get("data", {}).get("search", {}).get("products", [])

        for p in products:
            title = p.get("item", {}).get("product_description", {}).get("title", "").lower()

            if any(x in title for x in EXCLUDE):
                continue

            pid = f"tg_{p.get('tcin')}"

            if pid in seen:
                continue

            seen.add(pid)

            link = f"https://www.target.com/p/-/A-{p.get('tcin')}"
            send(f"🧸 Target: {title}\n{link}")

    except Exception as e:
        print("Target error:", e)

# =========================
# WALMART (SEARCH)
# =========================
def check_walmart():
    url = "https://www.walmart.com/search?q=squish"

    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})

        if "searchResult" not in r.text:
            print("Walmart blocked or changed response")
            return

        # lightweight keyword fallback (not perfect but stable)
        if "squishmallow" in r.text.lower():
            pid = "wm_squish"

            if pid not in seen:
                seen.add(pid)
                send("🧸 Walmart: Squish-related items detected\nhttps://www.walmart.com/search?q=squish")

    except Exception as e:
        print("Walmart error:", e)

# =========================
# AMAZON (SAFE MODE ONLY)
# =========================
def check_amazon():
    # Amazon blocks scraping heavily — so we only do keyword alerting
    try:
        r = requests.get(
            "https://www.amazon.com/s?k=squishmallow",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        if "squishmallow" in r.text.lower():
            pid = "am_squish"

            if pid not in seen:
                seen.add(pid)
                send("🧸 Amazon: Squishmallow search activity detected\nhttps://www.amazon.com/s?k=squishmallow")

    except Exception as e:
        print("Amazon error:", e)

# =========================
# RUN ALL STORES
# =========================
check_squishmart()
check_fivebelow()
check_target()
check_walmart()
check_amazon()