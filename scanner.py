import os
import json
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ==========================
# Load previous scan
# ==========================

try:
    with open("previous_scan.json", "r") as f:
        previous = json.load(f)
except:
    previous = []

previous_ranks = {}

for i, coin in enumerate(previous):
    previous_ranks[coin["symbol"]] = i + 1

# ==========================
# Get CoinGecko Data
# ==========================

url = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",
    "order": "volume_desc",
    "per_page": 250,
    "page": 1,
    "price_change_percentage": "24h"
}

coins = requests.get(url, params=params).json()

stablecoins = [
    "usdt",
    "usdc",
    "dai",
    "fdusd",
    "tusd",
    "usde",
    "pyusd"
]

candidates = []

for coin in coins:

    symbol = coin["symbol"].lower()

    if symbol in stablecoins:
        continue

    market_cap = coin.get("market_cap", 0)
    volume = coin.get("total_volume", 0)
    change = coin.get("price_change_percentage_24h") or 0

    if (
        market_cap >= 50000000 and
        market_cap <= 5000000000 and
        volume >= 10000000 and
        change > 0
    ):

        volume_ratio = volume / market_cap

        score = 0

        score += min(change * 2, 40)

        score += min(volume_ratio * 100, 30)

        if market_cap < 500000000:
            score += 20
        elif market_cap < 1000000000:
            score += 15
        else:
            score += 10

        if volume > 50000000:
            score += 10

        candidates.append({
            "symbol": coin["symbol"].upper(),
            "price": coin["current_price"],
            "change": change,
            "score": round(score)
        })

candidates = sorted(
    candidates,
    key=lambda x: x["score"],
    reverse=True
)

top10 = candidates[:10]

# ==========================
# Compare rankings
# ==========================

alerts = []

for rank, coin in enumerate(top10, start=1):

    symbol = coin["symbol"]

    if symbol not in previous_ranks:

        alerts.append(
            f"🚨 NEW ENTRY\n"
            f"{symbol}\n"
            f"Rank #{rank}\n"
            f"Score {coin['score']}"
        )

    else:

        old_rank = previous_ranks[symbol]

        if old_rank - rank >= 3:

            alerts.append(
                f"🔥 RANK UP\n"
                f"{symbol}\n"
                f"#{old_rank} → #{rank}\n"
                f"Score {coin['score']}"
            )

# ==========================
# Build Telegram Message
# ==========================

message = "🔥 TOP SPOT PICKS V4\n\n"

for rank, coin in enumerate(top10, start=1):

    message += (
        f"{rank}. {coin['symbol']}\n"
        f"Score: {coin['score']}/100\n"
        f"24H: {coin['change']:.2f}%\n\n"
    )

if alerts:

    message += "\n================\n\n"

    for alert in alerts[:5]:
        message += alert + "\n\n"

# ==========================
# Send Telegram
# ==========================

telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

requests.post(
    telegram_url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

# ==========================
# Save latest scan
# ==========================

with open("previous_scan.json", "w") as f:
    json.dump(top10, f)

print("V4 scan selesai")
