import MetaTrader5 as mt5
import datetime
import pytz
import math
from ratesTimeRange import ratesTimeRange
import pandas as pd 
from trading_strategies import parabolic_SAR
import time
from signalHandlerLive import signalHandlerLive
from orderFormatterLive import orderFormatter

#Outline

#Connect to MT5
#Pull Data
#Signal Handler
#Check Current Positions
#Signal Writer
#Sent to MT5

#MT5 Live acc
#login = 7075929
#password = 'ULP3jJgr'
#server = 'ICMarkets-MT5-2'

##Initial Params
#Demo acc
login = 50950826
password = 'pwqC1Mx3'
server = 'ICMarkets-Demo'

symbol = 'EURUSD'
interval = mt5.TIMEFRAME_M5
takeProfitAmt = 0.0005
stopLossAmt = 0.0005
lookbackPeriod = 100
intervalToMinutes = {mt5.TIMEFRAME_M15: 15, mt5.TIMEFRAME_M5: 5, mt5.TIMEFRAME_M1: 1,mt5.TIMEFRAME_H1: 60}

mt5.initialize()
mt5_auth = mt5.login(login = login, password = password, server = server)
mt5.login(login = login, password = password, server = server)
print("Auth Status:", mt5_auth)
print("Log:", mt5.last_error())
print("Account/Connection Info:", mt5.account_info()._asdict())

#Final Initialization

intervalMinutes = intervalToMinutes[interval]
tRates = 0
tTicks = 0

broker = signalHandlerLive(takeProfitAmt, stopLossAmt)

while True:

    #Check stoploss/takeprofit every 10 sec
    if (time.time() - tTicks) >= 10:
        lastTickDat = mt5.symbol_info_tick(symbol)
        if broker.prevTradedPosition is not None and broker.prevTradedPrice is not None and broker.takeProfitPrice is not None and broker.stopLossPrice is not None:
            broker.refreshAndCheck(lastTickDat.bid, lastTickDat.ask)

    #Trigger a new bar
    if (time.time() - tRates) >= intervalMinutes * 60:
        #Trigger every bar

        startTime, endTime = ratesTimeRange(datetime.datetime.now(tz = pytz.utc), intervalMinutes, lookbackPeriod)
        #Prep time

        #Pull new set of bars
        ratesDat = pd.DataFrame(mt5.copy_rates_range(symbol, interval, startTime, endTime))
        ratesDat['time'] = pd.to_datetime(ratesDat['time'], unit = 's')
        lastBarTime = ratesDat['time'].iloc[-1]
        tRates = time.time()

        #Refresh & Check
        lastTickDat = mt5.symbol_info_tick(symbol)
        if broker.prevTradedPosition is not None and broker.prevTradedPrice is not None and broker.takeProfitPrice is not None and broker.stopLossPrice is not None:
            broker.refreshAndCheck(lastTickDat.bid, lastTickDat.ask)        

        #Strategy decision
        strategy = parabolic_SAR.pSAR(ratesDat)
        strategyResult = strategy.run_pSAR()
        
        #Update in signal handler
        lastTickDat = mt5.symbol_info_tick(symbol)
        broker.refresh(lastTickDat.bid, lastTickDat.ask) #Just update new prices
        signalResults = broker.handleSignal(strategyResult)
        
        ##Work in getting previous positions - for closing trades
        #Format and send to MT5
        formatter = orderFormatter(symbol, 0.01, signalResults['Action'], signalResults['Price'], signalResults['TP'], signalResults['SL'])
        request = formatter.formatRequest()
        formatter.sendRequest()

        #Update post order has been sent
        positions = mt5.positions_get(symbol = symbol)

        print("test1")