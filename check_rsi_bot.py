# required python3 modules: telegram, python-binance, python-telegram-bot
# binance secret api key, api key, telegram bot token and telegram chat id are required.
# credentials.txt file has these 4 value.
import telegram
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import datetime
import time
import re
import os
import threading

credentials = []
with open ("/home/baler/Desktop/algo_bot/credentials.txt", "r") as file:
	while True:
		line = file.readline()
		if not line:
			break
		result = [x.strip() for x in line.split('=')]
		if len(result) == 2:
			credentials.append(result[1])

api_key = credentials[0]
api_secret = credentials[1]
client = Client(api_key, api_secret)
candle_4h = Client.KLINE_INTERVAL_4HOUR
candle_1d = Client.KLINE_INTERVAL_1DAY
limit = 400

bot = telegram.Bot(token=credentials[2])
chatID = credentials[3]

#check depencies of coins that BTC or USDT
def isFinishWithBtcOrUsdt(s):
	x = len(s)
	if s[x-1] == 'C' and s[x-2] == 'T' and s[x-3] == 'B':
		return True
	elif s[x-1] == 'T' and s[x-2] == 'D' and s[x-3] == 'S' and s[x-4] == 'U':
		return True
	#elif s[x-1] == 'H' and s[x-2] == 'T' and s[x-3] == 'E':
	#	return True
	else:
		return False

#get coins which depend on BTC or Tether
def getTradeList():
	binanceList = client.get_all_tickers()
	tradeList = []
	for x in range(len(binanceList)):
		if isFinishWithBtcOrUsdt(binanceList[x]['symbol']):
			tradeList.append(str(binanceList[x]['symbol']))

	return tradeList

def calculateRsi(coinName, candles):
	firstAvGain=0
	firstAvLoss=0
	for x in range(len(candles)-1):
		if float(candles[x][4]) < float(candles[x+1][4]):
			firstAvGain += float(candles[x+1][4]) - float(candles[x][4])
		elif float(candles[x][4]) > float(candles[x+1][4]):
			firstAvLoss += float(candles[x][4]) - float(candles[x+1][4])

	firstAvGain = firstAvGain/14
	firstAvLoss = firstAvLoss/14
	if float(candles[13][4])-float(candles[12][4]) >= 0:
		avGain = (firstAvGain*13 + float(candles[13][4])-float(candles[12][4]))/14	
		avLoss = (firstAvLoss*13)/14
	else:
		avGain = (firstAvGain*13)/14	
		avLoss = (firstAvLoss*13 - float(candles[13][4])+float(candles[12][4]))/14
	rs = avGain / avLoss
	rsi = 100 - (100 / (1 + rs))
	return rsi

def main():
	threading.Timer(14400, main).start()

	tradeList = getTradeList()
	print(tradeList)
	if "SUBBTC" in tradeList:
		tradeList.remove("SUBBTC")

	for i in range(len(tradeList)):
		candles4h = client.get_klines(symbol=tradeList[i], interval=candle_4h, limit=15)
		candles1d = client.get_klines(symbol=tradeList[i], interval=candle_1d, limit=15)

		print(tradeList[i])

		print(calculateRsi(tradeList[i], candles4h))
		print(calculateRsi(tradeList[i], candles1d))




if __name__ == '__main__':
    #main()
    main()