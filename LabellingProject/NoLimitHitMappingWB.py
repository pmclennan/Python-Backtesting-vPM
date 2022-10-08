import pandas as pd
import os
import datetime
import sys

sys.path.append(os.getcwd())
from UtilsPM.DataReaders import MT5SymbolsDataReader

def NoLimitHitMapping(data, limit):
    
    data['shortLossHit'] = [""] * len(data)
    data['maxShortPnL'] = [""] * len(data)
    data['shortExitIndex'] = [""] * len(data)

    data['longLossHit'] = [""] * len(data)
    data['maxLongPnL'] = [""] * len(data)
    data['longExitIndex'] = [""] * len(data)


    for i in range(1, len(data)-1):
        openPrice = data.loc[i, 'open']        
        
        #Long
        j = data.where(openPrice - data.loc[i+1:,'low'] >= limit).first_valid_index()
        data.loc[i, 'longLossHit'] = j
        maxPoint = data.loc[data.loc[i+1:j-1, 'high'].idxmax()]          
        data.loc[i,'maxLongPnL'] = maxPoint['high'] - openPrice
        data.loc[i,'longExitIndex'] = maxPoint.name

        #Short
        j = data.where(data.loc[i+1:,'high'] - openPrice >= limit).first_valid_index()
        data.loc[i, 'shortLossHit'] = j
        minPoint = data.loc[data.loc[i+1:j-1, 'low'].idxmin()]          
        data.loc[i,'maxShortPnL'] = minPoint['low'] - openPrice
        data.loc[i,'shortExitIndex'] = minPoint.name

        #Long
        # for j in range(i+1, len(data)):
        #     if openPrice - data.loc[j, 'low'] >= limit:
        #         data.loc[i, 'longLossHit'] = j
        #         maxPoint = data.loc[data.loc[i+1:j-1, 'high'].idxmax()]          
        #         data.loc[i,'maxLongPnL'] = maxPoint['high'] - openPrice
        #         data.loc[i,'longExitIndex'] = maxPoint.name
        #         break
        
        # #Short
        # for j in range(i+1, len(data)):
        #     if data.loc[j, 'high'] - openPrice >= limit:
        #         data.loc[i, 'shortLossHit'] = j
        #         minPoint = data.loc[data.loc[i+1:j-1, 'low'].idxmin()]          
        #         data.loc[i,'maxShortPnL'] = minPoint['low'] - openPrice
        #         data.loc[i,'shortExitIndex'] = minPoint.name
        #         break
            
        if i % (round(0.01 * len(data), 0)) == 0:
                print("Progress: {}% ".format(round(100 * (i/len(data)))), end = "\r", flush = True)            

    return data

data_filename = "EURUSD.a_M1_202009020000_202209022356.csv"
#data_folder = "C:\\Users\\Patrick\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Symbols Method"
data_folder = os.path.join(os.getcwd() , 'Datasets', 'Symbols Method')
data_dir = os.path.join(data_folder, data_filename)
data = MT5SymbolsDataReader(data_dir)

data = data.loc[0:100000]

df = NoLimitHitMapping(data, 20/10000)

print("Something")