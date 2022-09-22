import pandas as pd
import datetime
import MetaTrader5 as mt5
import pytz
import dateutil.tz as tz
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

currency = 'EURUSD'
frequency = mt5.TIMEFRAME_M1
##tz = pytz.timezone('Australia/Sydney')
tz = pytz.utc

login = 7075929
password = 'ULP3jJgr'

start = datetime.datetime(year = 2021, month = 1, day = 4, tzinfo = tz)
#end = datetime.datetime(year = 2022, month = 9, day = 9, tzinfo = tz)
end = datetime.datetime.now(tz = tz)

mt5.initialize()
mt5_auth = mt5.login(login = login, password = password, server = 'ICMarkets-MT5-2')
mt5.login(login = login, password = password, server = 'ICMarkets-MT5-2')
print("Auth Status:", mt5_auth)
print("Log:", mt5.last_error())
print("Account/Connection Info:", mt5.account_info()._asdict())

data = mt5.copy_rates_range(currency, frequency, start, end)
data = pd.DataFrame(data)
data['time'] = pd.to_datetime(data['time'], unit = 's', utc = True)
data.index = data['time']
data.drop(columns = ['time'], inplace = True)
#data.index = data.index.tz_convert('Australia/Sydney')
data.reset_index(inplace = True)

InpDepth = 12
InpDeviation = 5
InpBackstep = 3

ZigZagBuffer = []
HighMapBuffer = []
LowMapBuffer = []
ExtRecalc = 3
Extremum = 0 #Searching for first extremum
Peak = 1 #Searching for next ZigZag peak
Bottom = -1 #Searching for next ZigZag bottom

#Implied variables...
PointSize = 0.00001

#Unsure
#https://www.mql5.com/en/docs/event_handlers/oncalculate
rates_total = len(data) #I think this is actually ticks..
#prev calculated = bars already accounted for = rates_total if backtesting?

#Loop the below for each bar?
#if prev_calculated == 0:
#    ZigZagBuffer = 0
#    HighMapBuffer = 0
#    LowMapBuffer = 0
#    start = InpDepth

#Functions - looks like we need to get these to set global variables...? use of min, actually i think these are just for while condition
def Lowest(array, depth, start):
    if start < 0:
        return 0
    minval = array[start] #Had to use minval over min
    index = start
    
    #Start searching
    i = start - 1
    while (i > start - depth) and (i >= 0):
        if array[i] < minval:
            index = i
            minval = array[i]
        i -= 1
    
    #Return index of lowest bar
    return index     

def Highest(array, depth, start):
    if start < 0:
        return 0
    
    maxval = array[start] #Also have to use maxval here
    index = start
    
    i = start - 1
    while (i > start - depth) and (i >= 0):
        if array[i] > maxval:
            index = i
            maxval = array[i]
        i -= 1
        
    return index                

#ZigZag was already calculated before
prev_calculated = 0

ZigZagBuffer = [0] * len(data)
HighMapBuffer = [0] * len(data)
LowMapBuffer = [0] * len(data)
start = InpDepth
low = data['low']
high = data['high']

for i in range(len(data)):

    i = 0
    start = 0
    extreme_counter = 0
    extreme_search = Extremum
    shift = 0
    back = 0
    last_high_pos = 0
    last_low_pos = 0
    val = 0
    rest = 0
    curlow = 0
    curhigh = 0
    last_high = 0
    last_low = 0    

    if prev_calculated > 0:
        i = rates_total - 1
        #Search for third extremum from last uncompleted bar
        while (extreme_counter < ExtRecalc) and (i > rates_total - 100):
            res = ZigZagBuffer[i]
            if res != 0:
                extreme_counter += 1
            i -= 1
        i += 1
        start = i
        
        #What type of extremum we search for
        if LowMapBuffer[i] != 0:
            curlow = LowMapBuffer[i]
            extreme_search = Peak
        else:
            curhigh = HighMapBuffer[i]
            extreme_search = Bottom
            
        #Clear Indicator Values
        i = start+1
        while i < rates_total: #MT5 also includes IsStopped()
            ZigZagBuffer[i] = 0
            LowMapBuffer[i] = 0
            HighMapBuffer[i] = 0
            i += 1
            
    #Searching for high and low extremes
    shift = start
    while shift < rates_total: #MT5 also includes IsStopped()
        
        #Low
        val = low[Lowest(low, InpDepth, shift)]
        if val == last_low:
            val = 0
        else:
            last_low = val
            if (low[shift] - val) > InpDeviation * PointSize:
                val = 0
            else:
                back = 1
                while back <= InpBackstep:
                    res = LowMapBuffer[shift - back]
                    if (res != 0) and (res > val):
                        LowMapBuffer[shift-back] = 0
                    back += 1

        if low[shift] == val:
            LowMapBuffer[shift] = val
        else:
            LowMapBuffer[shift] = 0

        #High
        val = high[Highest(high, InpDepth, shift)]
        if val == last_high:
            val = 0
        else:
            last_high = val
            if (val - high[shift]) > InpDeviation * PointSize:
                val = 0
            else:
                back = 1
                while back <= InpBackstep:
                    res = HighMapBuffer[shift - back]
                    if (res != 0) and (res < val):
                        HighMapBuffer[shift - back] = 0
                    back += 1
        
        if high[shift] == val:
            HighMapBuffer[shift] = val
        else:
            HighMapBuffer[shift] = 0
        
        shift += 1
    
    #Set Last Values
    if extreme_search == 0: #Undefined values
        last_low = 0
        last_high = 0
    else:
        last_low = curlow
        last_high = curhigh
        
    #Final Selection
    shift = start
    while shift < rates_total:
        res = 0
        if extreme_search == Extremum:
            if last_low == 0 and last_high == 0:
                if HighMapBuffer[shift] != 0:
                    last_high = high[shift]
                    last_high_pos = shift
                    extreme_search = Bottom
                    ZigZagBuffer[shift] = last_high
                    res = 1
                    
                if LowMapBuffer[shift] != 0:
                    last_low = low[shift]
                    last_low_pos = shift
                    extreme_search = Peak
                    ZigZagBuffer[shift] = last_low
                    res = 1
                    
            #break #??
            
        elif extreme_search == Peak:
            if (LowMapBuffer[shift] != 0) and (LowMapBuffer[shift] < last_low) and (HighMapBuffer[shift] == 0):
                ZigZagBuffer[last_low_pos] = 0
                last_low_pos = shift
                last_low = LowMapBuffer[shift]
                ZigZagBuffer[shift] = last_low
                res = 1
                
            if (HighMapBuffer[shift] != 0) and (LowMapBuffer[shift] == 0):
                last_high = HighMapBuffer[shift]
                last_high_pos = shift
                ZigZagBuffer[shift] = last_high
                extreme_search = Bottom
                res = 1
                
            #break #??
            
        elif extreme_search == Bottom:
            if (HighMapBuffer[shift] != 0) and (HighMapBuffer[shift] > last_high) and (LowMapBuffer[shift] == 0):
                ZigZagBuffer[last_high_pos] = 0
                last_high_pos = shift
                last_high = HighMapBuffer[shift]
                ZigZagBuffer[shift] = last_high
            if (LowMapBuffer[shift] != 0 and HighMapBuffer[shift] == 0):
                last_low = LowMapBuffer[shift]
                last_low_pos = shift
                ZigZagBuffer[shift] = last_low
                extreme_search = Peak
            
            #break

        shift += 1
            
    prev_calculated = rates_total

    print("Debug Point")

print("Debug Point")