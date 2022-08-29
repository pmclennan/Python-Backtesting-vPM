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

login = 50950826
password = 'pwqC1Mx3'
server = 'ICMarkets-Demo'

mt5.initialize()
mt5_auth = mt5.login(login = login, password = password, server = server)
mt5.login(login = login, password = password, server = server)
print("Auth Status:", mt5_auth)
print("Log:", mt5.last_error())
print("Account/Connection Info:", mt5.account_info()._asdict())

symbol = 'EURUSD.a'
take_profit = 0.002
stop_loss = 0.002

lot = 0.1
point = mt5.symbol_info(symbol).point
price = mt5.symbol_info_tick(symbol).ask
deviation = 20
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": price - stop_loss,
    "tp": price + take_profit,
    "deviation": deviation,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC
}

result = mt5.order_send(request)

print(result.retcode)