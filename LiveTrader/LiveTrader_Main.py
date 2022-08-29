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

##Initial Params
#Demo acc
login = 50950826
password = 'pwqC1Mx3'
server = 'ICMarkets-Demo'

symbol = 'EURUSD.a'
interval = mt5.TIMEFRAME_M5
takeProfitAmt = 0.0005
stopLossAmt = 0.0005
lookbackPeriod = 100 #How many bars are pulled each refresh
lotsToTrade = 0.01 #Volume to trade
intervalToMinutes = {mt5.TIMEFRAME_M15: 15, mt5.TIMEFRAME_M5: 5, mt5.TIMEFRAME_M1: 1,mt5.TIMEFRAME_H1: 60} #Useful for working with number of bars & time

#MT5 Initialization
mt5.initialize()
mt5_auth = mt5.login(login = login, password = password, server = server)
mt5.login(login = login, password = password, server = server)
print("Auth Status:", mt5_auth)
print("Log:", mt5.last_error())
print("Account/Connection Info:", mt5.account_info()._asdict())

#Final Initialization
intervalMinutes = intervalToMinutes[interval] #Convert for working with time
tRates = 0 #Initialized as zero by intention
tTicks = 0 #Initialized as zero by intention
lastBarTime = datetime.datetime(2000, 1, 1)
lastBarTimeUTC = datetime.datetime(2000, 1, 1, tzinfo = pytz.utc) #Initialized as now by intention

#Initialize broker
broker = signalHandlerLive(takeProfitAmt, stopLossAmt)

#Infinite loop
while True:

    ##Trigger a new bar process
    #Check if time since last pull OR time since last bar exceeds the frequency
    if (time.time() - tRates) or (datetime.datetime.now(tz = pytz.utc) - lastBarTimeUTC) >= intervalMinutes * 60:

        ##First, align with MT5
        positions = mt5.positions_get(symbol = symbol)
        if len(positions) == 0:
            #Handles if a sl/tp has been hit IN MT5
            prevTradedPosition = 0
            prevTradedPrice = None
            takeProfitPrice = None
            stopLossPrice = None
            positionId = None
            sizeOn = None

        elif len(positions) == 1:
            #Simply refreshes/confirms position info
            position = positions[0]
            positionDict = position._asdict()
            
            prevTradedPosition = 1 if positionDict['type'] == 0 else -1
            prevTradedPrice = positionDict['price_open']
            takeProfitPrice = positionDict['tp']
            stopLossPrice = positionDict['sl']
            positionId = result.order
            sizeOn = positionDict['volume']  

        #Update broker object
        broker.updatePostExecution(prevTradedPosition, prevTradedPrice, takeProfitPrice, stopLossPrice, positionId, sizeOn)

        #Reset pullSuccessFlag as we are now looking to pull latest bar
        pullSuccessFlag = 0     

        ##Data Pull
        #Keep trying to pull set of bars. Proceed if pull is not empty & last bar is new
        print("Pulling Rates")
        while not pullSuccessFlag:
            #Format time for pulling - make sure it covers required number of bars
            startTime, endTime = ratesTimeRange(datetime.datetime.now(tz = pytz.utc), intervalMinutes, lookbackPeriod)
            ratesDat = pd.DataFrame(mt5.copy_rates_range(symbol, interval, startTime, endTime))
            if not ratesDat.empty:
                ratesDat['time'] = pd.to_datetime(ratesDat['time'], unit = 's')
                if ratesDat['time'].iloc[-1] > lastBarTime:
                    #Successful Pull - update flag and proceed
                    pullSuccessFlag = 1
            
        ##Time storage
        #Store last bar time - localize for time comparison purposes
        lastBarTime = ratesDat['time'].iloc[-1]
        lastBarTimeUTC = lastBarTime.tz_localize(tz = pytz.utc)
        #Also store general time
        tRates = time.time()

        ##Strategy decision
        strategy = parabolic_SAR.pSAR(ratesDat)
        strategyResult = strategy.run_pSAR()
        
        ##Update in signal handler
        lastTickDat = mt5.symbol_info_tick(symbol)
        broker.refresh(lastTickDat.bid, lastTickDat.ask) #Just update new prices, not checking sl/tp as interferes with next decision.
        signalResults = broker.handleSignal(strategyResult)
                
        ##Format and send to MT5
        #Use volume from open position, otherwise predefined trading volume (should be equal, but just in case)
        if signalResults['Action'][0:5] == 'CLOSE':            
            volToTrade = signalResults['Volume']
        else:
            volToTrade = lotsToTrade

        #Format and send
        formatter = orderFormatter(symbol, volToTrade, signalResults['Action'], signalResults['Price'], signalResults['TP'], signalResults['SL'], signalResults['positionId'])
        request = formatter.formatRequest()
        result = formatter.sendRequest()

        #Check order info if a request is sent
        if request != 'No Request':

            ##Update once order has been sent & align with MT5
            if formatter.lastRetcode == mt5.TRADE_RETCODE_DONE:
                #Check if trade done and len(positions) == 1, then update appropriate data from there.
                positions = mt5.positions_get(symbol = symbol)
                if len(positions) == 1:
                    position = positions[0]
                    positionDict = position._asdict()
                    
                    prevTradedPosition = 1 if positionDict['type'] == 0 else -1
                    prevTradedPrice = positionDict['price_open']
                    takeProfitPrice = positionDict['tp']
                    stopLossPrice = positionDict['sl']
                    positionId = positionDict['ticket']
                    sizeOn = positionDict['volume']            

                #Or if a trade has been closed
                elif len(positions) == 0:
                    prevTradedPosition = 0
                    prevTradedPrice = None
                    takeProfitPrice = None
                    stopLossPrice = None
                    positionId = None
                    sizeOn = None

                broker.updatePostExecution(prevTradedPosition, prevTradedPrice, takeProfitPrice, stopLossPrice, positionId, sizeOn)

            else:
                print("Order Failed with code {} \n".format(formatter.lastRetcode))            