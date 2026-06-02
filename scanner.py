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

filtered = []

for coin in coins:

    symbol = coin["symbol"].lower()

    if symbol in stablecoins:
        continue

    market_cap = coin.get("market_cap", 0)
    volume = coin.get("total_volume", 0)
    change = coin.get("price_change_percentage_24h", 0)

    if (
        market_cap >= 50000000 and
        market_cap <= 5000000000 and
        volume >= 10000000 and
        change > 3
    ):
        filtered.append(coin)

filtered = sorted(
    filtered,
    key=lambda x: x["price_change_percentage_24h"],
    reverse=True
)

message = "🚀 SPOT SCANNER V2\n\n"

for i, coin in enumerate(filtered[:10], start=1):

    message += (
        f"{i}. {coin['symbol'].upper()}\n"
        f"💰 ${coin['current_price']}\n"
        f"📈 {coin['price_change_percentage_24h']:.2f}%\n"
        f"🏦 MCAP ${(coin['market_cap']/1000000):.0f}M\n\n"
    )

if len(filtered) == 0:
    message = "📭 Tiada coin memenuhi syarat hari ini."

telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

requests.post(
    telegram_url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print("Scanner V2 selesai")
