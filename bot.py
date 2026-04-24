import requests
import os
import time
from datetime import datetime

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK is not set!")

# =========================
# CONFIG
# =========================
KEYWORDS = ["squish", "squishy", "squishmallow", "plush", "soft"]
EXCLUDE = ["needoh", "dumpling"]

seen = {}
COOLDOWN = 60 * 60 * 4  # 4 hours

# =========================
# DISCORD
# =========================
def send(title, url, image=None, store="Store", tag="NEW"):
    color_map = {
        "NEW": 0x00FF99,
        "RESTOCK": 0xFFA500,
        "HOT": 0xFF4D4D
    }

    embed = {
        "title": f"🧸 {store}: {title}",
        "url": url,
        "color": color_map.get(tag, 0x00FF99),
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": f"Insane Mode • {tag}"}
    }

    if image:
        embed["image"] = {"url": image}

    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]})
    except Exception as e:
        print("Discord error:", e)

# =========================
# SMART FILTER ENGINE
# =========================
def score_item(name):
    name = name.lower()

    score = 0

    if any(x in name for x in KEYWORDS):
        score += 2

    if any(x in name for x in EXCLUDE):
        score -= 10

    return score

# =========================
# COOLDOWN CHECK
# =========================
def allowed(pid):
    now = time.time()

    if pid not in seen:
        seen[pid] = now
        return True

    if now - seen[pid] > COOLDOWN:
        seen[pid] = now
        return True

    return False

# =========================
# SQUISHMART (BEST DATA)
# =========================
def check_squishmart():
    url = "https://www.squishmart.com/products.json?limit=250"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        for p in data.get("products", []):
            title = p["title"]
            name = title.lower()

            pid = f"sm_{p['id']}"

            if not allowed(pid):
                continue

            score = score_item(name)

            if score < 0:
                continue

            image = None
            if p.get("images"):
                image = p["images"][0].get("src")

            link = f"https://www.squishmart.com/products/{p['handle']}"

            tag = "HOT" if score >= 3 else "NEW"

            send(title, link, image, "Squishmart", tag)

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
            name = item.get("name", "")

            pid = f"fb_{item.get('id', name)}"

            if not allowed(pid):
                continue

            score = score_item(name)

            if score < 0:
                continue

            send(
                name,
                item.get("url", "https://www.fivebelow.com"),
                item.get("image"),
                "Five Below",
                "NEW"
            )

    except Exception as e:
        print("Five Below error:", e)

# =========================
# TARGET
# =========================
def check_target():
    url = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"

    try:
        r = requests.get(url, params={
            "keyword": "squish",
            "count": 20,
            "channel": "web"
        }, timeout=10)

        data = r.json()

        products = data.get("data", {}).get("search", {}).get("products", [])

        for p in products:
            item = p.get("item", {})
            title = item.get("product_description", {}).get("title", "")

            pid = f"tg_{p.get('tcin')}"

            if not allowed(pid):
                continue

            score = score_item(title)

            if score < 0:
                continue

            image = item.get("enrichment", {}).get("images", {}).get("primary_image_url")
            link = f"https://www.target.com/p/-/A-{p.get('tcin')}"

            send(title, link, image, "Target", "NEW")

    except Exception as e:
        print("Target error:", e)

# =========================
# WALMART (SIGNAL MODE)
# =========================
def check_walmart():
    try:
        r = requests.get(
            "https://www.walmart.com/search?q=squishmallow",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        if "squish" in r.text.lower():
            pid = "wm_signal"

            if allowed(pid):
                send(
                    "Walmart Squishmallow Search Signal",
                    "https://www.walmart.com/search?q=squishmallow",
                    None,
                    "Walmart",
                    "HOT"
                )

    except Exception as e:
        print("Walmart error:", e)

# =========================
# RUN ENGINE
# =========================
check_squishmart()
check_fivebelow()
check_target()
check_walmart()