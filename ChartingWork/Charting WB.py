import MetaTrader5 as mt5
import datetime
import pandas as pd
import numpy as np
import pytz
import os

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
# dat_zigzag = data.copy().reset_index(drop = True)
# depth = 12
# deviation = 5
# backstep = 3
# pipsize = 1/10000
# ZigZags1 = ZigZagPoints(data, depth, deviation, backstep, pipsize)
# print(ZigZags1[ZigZags1['ZigZag Type'] != ''])
# plotCandlesWithZigZag(ZigZags1, 80, 180, 4, False, True, None)

#ABCD Mapping
#ZigZagsABCD1 = ZigZags1.copy()
#ABCD1 = ABCD_mapping(ZigZagsABCD1, 1.61, 0.05, 1)
#print(ABCD1.query("ABCD1 != '' or ABCD2 != '' or ABCD3 != '' or ABCD4 != ''"))
#plotCandlesWithZigZagABCD(ABCD1, 900, 1100, 16, False, True, None)

#With MT5 ZigZag Data
dataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets"
dataFilename = "EURUSDZigZagM1_2017v3.csv"
dataDir = os.path.join(dataFolder, dataFilename)

#Set up time period
tz = pytz.utc
start = datetime.datetime(year = 2022, month = 9, day = 8, tzinfo = tz)
end = datetime.datetime.now(tz = tz)
data = pd.read_csv(dataDir, sep = "\t", parse_dates = ["Date"])
data['Date'] = data['Date'].dt.tz_localize(tz = tz)
datTest = data.loc[data['Date'] >= start].loc[data['Date'] <= end].reset_index(drop = True)

#Rename cols
for column in datTest.columns:
    datTest.rename(columns = {column: column.lower()}, inplace = True)
datTest.rename(columns = {'buffer#0': "ZigZag Value", 'date': 'time'}, inplace = True)

#Map ZigZags in format for plotting
ZigZagTypes = [""] * len(datTest)
peakIdx = datTest.loc[datTest['ZigZag Value'] == datTest['high']].index.values
valleyIdx = datTest.loc[datTest['ZigZag Value'] == datTest['low']].index.values
for idx in peakIdx:
    ZigZagTypes[idx] = "peak"
for idx in valleyIdx:
    ZigZagTypes[idx] = "valley"
datTest['ZigZag Type'] = ZigZagTypes    
datTest.loc[datTest['ZigZag Value'] == 0, 'ZigZag Value'] = ''
#plotCandlesWithZigZag(datTest, len(datTest)-200, len(datTest))

ABCD2 = ABCD_mapping(datTest, 1.61, 0.05, 1)
print(ABCD2.query("ABCD1 != '' or ABCD2 != '' or ABCD3 != '' or ABCD4 != ''"))
plotCandlesWithZigZagABCD(ABCD2, len(ABCD2)-720, len(ABCD2), 30, False, False, None)

print("Break Point")