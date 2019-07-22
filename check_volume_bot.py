# required python3 modules: telegram, python-binance, python-telegram-bot
# binance secret api key, api key, telegram bot token and telegram chat id are required.
# This script is used to check volume of coins in Binance. These coins' units are BTC and USDT.
# Volumes are checked according to last 12 candles that are 15 min and 30 min candles.
# If a significant increase is detected a coin, telegram bot send a message to chat.

import telegram
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import datetime
import time
import re
import os
import threading

api_key = 'BINANCE_API_KEY'
api_secret = 'BINANCE_SECRET_KEY'
client = Client(api_key, api_secret)
candle_4hours = Client.KLINE_INTERVAL_4HOUR
candle_30min = Client.KLINE_INTERVAL_30MINUTE
candle_15min = Client.KLINE_INTERVAL_15MINUTE

bot = telegram.Bot(token='TELEGRAM_BOT_TOKEN')
chatID = 'TELEGRAM_CHAT_ID'

# check depencies of coins that BTC or USDT
def isFinishWithBtcOrUsdt(s):
	x = len(s)
	if s[x-1] == 'C' and s[x-2] == 'T' and s[x-3] == 'B':
		return True
	elif s[x-1] == 'T' and s[x-2] == 'D' and s[x-3] == 'S' and s[x-4] == 'U':
		return True
	else:
		return False

# get coins which depend on BTC or Tether
def getTradeList():
	binanceList = client.get_all_tickers()
	tradeList = []
	for x in range(len(binanceList)):
		if isFinishWithBtcOrUsdt(binanceList[x]['symbol']):
			tradeList.append(str(binanceList[x]['symbol']))

	return tradeList

def main():
	tradeList = getTradeList()
	#print(tradeList)
	if "SUBBTC" in tradeList:
		tradeList.remove("SUBBTC")

	for i in range(len(tradeList)):
		candles15m = client.get_klines(symbol=tradeList[i], interval=candle_15min, limit=13)
		candles30m = client.get_klines(symbol=tradeList[i], interval=candle_30min, limit=13)

		avg_15m_btc = 0
		avg_30m_btc = 0
		maxVol_15m = 0
		maxVol_30m = 0
		volume = {'vol_4h':[], 'vol_4h_btc':[], 'vol_30min':[], 'vol_30min_btc':[], 'avg':[]}

		for x in range(len(candles15m)-1):
			avg_15m_btc += float(candles15m[x][7])
			if float(candles15m[x][7]) > maxVol_15m:
				maxVol_15m = float(candles15m[x][7])

		for x in range(len(candles30m)-1):
			avg_30m_btc += float(candles30m[x][7])
			if float(candles30m[x][7]) > maxVol_30m:
				maxVol_30m = float(candles30m[x][7])

		avg_15m_btc /= 12
		avg_30m_btc /= 12
		
		last_vol_15m = float(candles15m[12][7])
		last_vol_30m = float(candles30m[12][7])
		prev_vol_15m = float(candles15m[11][7])
		prev_vol_30m = float(candles30m[11][7])

		unit = "BTC"
		vol_limit = 1
		if 'USDT' in tradeList[i]:
			unit = "USDT"
			vol_limit = 10000
		if last_vol_15m > vol_limit and last_vol_15m >= 4*avg_15m_btc and last_vol_15m >= 3*prev_vol_15m and last_vol_15m > maxVol_15m:
			printStr = 'Volume of ' + tradeList[i] + ' is increasing in 15mins candles. Volume = ' + str(last_vol_15m) + " " + unit
			bot.send_message(chat_id=chatID, text=printStr)
		elif last_vol_30m > vol_limit*2 and last_vol_30m >= 4*avg_30m_btc and last_vol_30m >= 3*prev_vol_30m and last_vol_30m > maxVol_30m:
			printStr = 'Volume of ' + tradeList[i] + ' is increasing in 30mins candles. Volume = ' + str(last_vol_30m) + " " + unit
			bot.send_message(chat_id=chatID, text=printStr)

if __name__ == '__main__':
    main()