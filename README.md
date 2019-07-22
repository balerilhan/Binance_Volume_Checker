# Binance_Volume_Checker

# required python3 modules: telegram, python-binance, python-telegram-bot

# binance secret api key, api key, telegram bot token and telegram chat id are required.

# This script is used to check volume of coins in Binance. These coins' units are BTC and USDT.
# Volumes are checked according to last 12 candles that are 15 min and 30 min candles.
# If a significant increase is detected a coin, telegram bot send a message to chat.
