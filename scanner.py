import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

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

        # Momentum (40 markah)
        score += min(change * 2, 40)

        # Volume ratio (30 markah)
        score += min(volume_ratio * 100, 30)

        # Market cap (20 markah)
        if market_cap < 500000000:
            score += 20
        elif market_cap < 1000000000:
            score += 15
        else:
            score += 10

        # Bonus volume besar (10 markah)
        if volume > 50000000:
            score += 10

        candidates.append({
            "symbol": coin["symbol"].upper(),
            "price": coin["current_price"],
            "change": change,
            "market_cap": market_cap,
            "score": round(score)
        })

candidates = sorted(
    candidates,
    key=lambda x: x["score"],
    reverse=True
)

message = "🔥 TOP SPOT PICKS V3\n\n"

medals = ["🥇", "🥈", "🥉"]

for i, coin in enumerate(candidates[:10]):

    medal = medals[i] if i < 3 else "⭐"

    message += (
        f"{medal} {coin['symbol']}\n"
        f"Score: {coin['score']}/100\n"
        f"Price: ${coin['price']}\n"
        f"24H: {coin['change']:.2f}%\n\n"
    )

if len(candidates) == 0:
    message = "📭 Tiada coin memenuhi syarat."

telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

requests.post(
    telegram_url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print("V3 scanner selesai")
