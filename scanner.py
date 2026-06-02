import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

url = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",
    "order": "volume_desc",
    "per_page": 5,
    "page": 1
}

coins = requests.get(url, params=params).json()

message = "🔥 TOP 5 VOLUME COINS\n\n"

for i, coin in enumerate(coins, start=1):
    message += (
        f"{i}. {coin['symbol'].upper()}\n"
        f"💰 Price: ${coin['current_price']}\n"
        f"📊 Volume: ${coin['total_volume']:,}\n\n"
    )

telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

requests.post(
    telegram_url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print("Top volume coins sent")
