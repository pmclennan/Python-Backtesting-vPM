import MetaTrader5 as mt5
import datetime
import pandas as pd
import numpy as np
import pytz

#My packages
from ZigZag_mapping import ZigZagPoints
from ABCD_mapping import ABCD_mapping
from candle_plotting_functions import * 

#----------------------------------------------------------------------------------------
#MT5 Datapulling, just for convinience to keep this code to get latest data for ref to autochartist 
#as opposed to repulling to csv from MT5 each time
currency = 'EURUSD'
frequency = mt5.TIMEFRAME_M15
tz = pytz.utc
start = datetime.datetime(year = 2022, month = 8, day = 17, tzinfo = tz)
end = datetime.datetime.now(tz = tz)

login = 7075929
password = 'ULP3jJgr'
mt5.initialize()
mt5_auth = mt5.login(login = login, password = password, server = 'ICMarkets-MT5-2')
mt5.login(login = login, password = password, server = 'ICMarkets-MT5-2')

data = mt5.copy_rates_range(currency, frequency, start, end)
data = pd.DataFrame(data)
data['time'] = pd.to_datetime(data['time'], unit = 's', utc = True)
data.index = data['time']
data.drop(columns = ['time'], inplace = True)
data.reset_index(inplace = True)
#----------------------------------------------------------------------------------------

## Some examples

#ZigZag Mapping
dat_zigzag = data.copy().reset_index(drop = True)
depth = 12
deviation = 5
backstep = 3
pipsize = 1/10000
ZigZags1 = ZigZagPoints(data, depth, deviation, backstep, pipsize)
#print(ZigZags1[ZigZags1['ZigZag Type'] != ''])
#plotCandlesWithZigZag(ZigZags1, 80, 180, 4, False, True, None)

#ABCD Mapping
ZigZagsABCD1 = ZigZags1.copy()
ABCD1 = ABCD_mapping(ZigZagsABCD1, 1.61, 0.5, 1)
print(ABCD1.query("ABCD1 != '' or ABCD2 != '' or ABCD3 != '' or ABCD4 != ''"))
plotCandlesWithZigZagABCD(ABCD1, 900, 1100, 16, False, True, None)