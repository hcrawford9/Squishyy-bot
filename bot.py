import requests
import os
from datetime import datetime

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK is not set!")

EXCLUDE = ["needoh", "dumpling"]

seen = set()

# =========================
# DISCORD EMBED (PRO)
# =========================
def send_embed(title, url, image=None, store="Store"):
    embed = {
        "title": f"🧸 {store}: {title}",
        "url": url,
        "color": 0xFF69B4,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "Squishy Monitor Bot"}
    }

    if image:
        embed["image"] = {"url": image}

    payload = {
        "embeds": [embed]
    }

    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        print("Discord status:", res.status_code)
    except Exception as e:
        print("Discord error:", e)

# =========================
# SQUISHMART (BEST QUALITY)
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

            image = p.get("images", [{}])[0].get("src")
            link = f"https://www.squishmart.com/products/{p['handle']}"

            send_embed(p["title"], link, image, "Squishmart")

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

        for item in data.get("items", []):
            name = item.get("name", "").lower()

            if any(x in name for x in EXCLUDE):
                continue

            pid = f"fb_{item.get('id', name)}"

            if pid in seen:
                continue

            seen.add(pid)

            image = item.get("image")
            link = item.get("url")

            send_embed(item.get("name", "Unknown"), link, image, "Five Below")

    except Exception as e:
        print("Five Below error:", e)

# =========================
# TARGET (BEST EFFORT)
# =========================
def check_target():
    url = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"

    try:
        r = requests.get(url, params={"keyword": "squish", "count": 20, "channel": "web"}, timeout=10)
        data = r.json()

        products = data.get("data", {}).get("search", {}).get("products", [])

        for p in products:
            item = p.get("item", {})
            title = item.get("product_description", {}).get("title", "")

            if any(x in title.lower() for x in EXCLUDE):
                continue

            pid = f"tg_{p.get('tcin')}"

            if pid in seen:
                continue

            seen.add(pid)

            image = item.get("enrichment", {}).get("images", {}).get("primary_image_url")
            link = f"https://www.target.com/p/-/A-{p.get('tcin')}"

            send_embed(title, link, image, "Target")

    except Exception as e:
        print("Target error:", e)

# =========================
# WALMART (LIMITED BUT STABLE)
# =========================
def check_walmart():
    try:
        r = requests.get(
            "https://www.walmart.com/search?q=squishmallow",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        if "squish" in r.text.lower():
            pid = "wm_squish"

            if pid not in seen:
                seen.add(pid)

                send_embed(
                    "Squishmallow Search Results",
                    "https://www.walmart.com/search?q=squishmallow",
                    None,
                    "Walmart"
                )

    except Exception as e:
        print("Walmart error:", e)

# =========================
# RUN ALL STORES
# =========================
check_squishmart()
check_fivebelow()
check_target()
check_walmart()