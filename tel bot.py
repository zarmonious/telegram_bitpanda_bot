import requests
import telegram
from telegram.ext import Updater, CommandHandler

BITPANDA_API_KEY = "xxxxxx"
TELEGRAM_BOT_TOKEN = "xxxxxx"
CHAT_ID = "xxxxxx"

import requests

BITPANDA_API_URL = "https://api.bitpanda.com/v1/asset-wallets"
BITPANDA_TICKER_URL = "https://api.bitpanda.com/v1/ticker"

def get_best_eur_price():
    response = requests.get(BITPANDA_TICKER_URL)
    
    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            return None

        best_price = data.get("BEST", {}).get("EUR")
        if best_price:
            return float(best_price)

        return None
    return None

def get_portfolio():
    headers = {
        "X-Api-Key": BITPANDA_API_KEY,
        "Accept": "application/json"
    }
    response = requests.get(BITPANDA_API_URL, headers=headers)

    #print("Status code:", response.status_code)
    #print("Response body:", response.text)

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            return "Failed to parse API response."

        wallets = (
            data.get("data", {})
            .get("attributes", {})
            .get("cryptocoin", {})
            .get("attributes", {})
            .get("wallets", [])
        )

        if not wallets:
            return "No wallets found in API response."

        holdings = "Your Portfolio:\n"
        best_wallet_found = False
        amount = 0

        for wallet in wallets:
            attributes = wallet.get("attributes", {})
            name = attributes.get("name", "Unknown")

            if name == "BEST Wallet":
                amount = float(attributes.get("balance", "0")) 
                best_wallet_found = True
                break

        if not best_wallet_found:
            return "BEST wallet not found."

        best_eur_price = get_best_eur_price()
        if best_eur_price is None:
            return "Failed to retrieve BEST price."

        best_value_in_eur = amount * best_eur_price

        holdings += f"{name}: {amount}\n"
        holdings += f"Price per 1 Best: {best_eur_price:.2f} €\nValue in EUR: {best_value_in_eur:.2f} €"

        return holdings
    else:
        return "Failed to retrieve portfolio data."


def send_telegram_message(message):
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

def portfolio(update, context):
    portfolio_info = get_portfolio()
    update.message.reply_text(portfolio_info)

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("portfolio", portfolio))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    send_telegram_message("Bot started. Send /portfolio to get your holdings.")
    main()

