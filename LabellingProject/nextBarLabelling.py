import pandas as pd
import os
import sys
sys.path.append(os.getcwd())
from UtilsPM.DataReaders import MT5SymbolsDataReader
from ChartingWork.candle_plotting_functions import plotCandles, plotCandlesWithPoint, plotCandlesWithPointIndicators
import pytz
import ta
import numpy as np

#For buy, if the next bar high > prev bar high, and next bar low > prev bar low, label 1
#For sell, if the next bar low < prev bar low, and next bar high < prev bar high, label -1
def nextBarLabelling(data, tradeType):

    data['Label'] = [0] * len(data)

    if tradeType == "buy" or tradeType == 1:
        for i in range(0, len(data)-1):
            if (data['high'].iloc[i+1] > data['high'].iloc[i]) and (data['low'].iloc[i+1] > data['low'].iloc[i]):
                data['Label'].iloc[i] = 1
            if i % (round(0.01 * len(data), 0)) == 0:
                print("Progress: {}% ".format(round(100 * (i/len(data)))), end = "\r", flush = True)   

    elif tradeType == "sell" or tradeType == -1:
        for i in range(0, len(data)-1):
            if (data['low'].iloc[i+1] < data['low'].iloc[i]) and (data['high'].iloc[i+1] < data['high'].iloc[i]):
                data['Label'].iloc[i] = 1
            if i % (round(0.01 * len(data), 0)) == 0:
                print("Progress: {}% ".format(round(100 * (i/len(data)))), end = "\r", flush = True)   

    return data

data_filename = "EURUSD.a_M5_201709040000_202210030000.csv"
data_folder = os.path.join(os.getcwd() , 'Datasets', 'Symbols Method')
data_dir = os.path.join(data_folder, data_filename)
data = MT5SymbolsDataReader(data_dir)
data = data.iloc[-2000:].reset_index(drop = True)

labelledDat = nextBarLabelling(data, 1)

labelledDat['BBHigh'] = ta.volatility.BollingerBands(labelledDat['close']).bollinger_hband()
labelledDat['BBMid'] = ta.volatility.BollingerBands(labelledDat['close']).bollinger_mavg()
labelledDat['BBLow'] = ta.volatility.BollingerBands(labelledDat['close']).bollinger_lband()

labelledDat['MACDLine'] = ta.trend.MACD(close=labelledDat['close']).macd()
labelledDat['MACDSignal'] = ta.trend.MACD(close=labelledDat['close']).macd_signal()

nanIdxs = np.any(labelledDat.isna(), axis = 1)
labelledDat = labelledDat[~nanIdxs].reset_index(drop = True)

#Subset - 20 bars before 20 after
subsets = []
subsetRange = 50
for i in range(subsetRange, len(labelledDat)-subsetRange):
    if labelledDat['Label'].iloc[i] != 0:
        subset = labelledDat.iloc[i-subsetRange:i+subsetRange].reset_index(drop = True)
        subset['Point'] = [0] * len(subset)
        subset.loc[labelledDat['time'].iloc[i] == subset['time'], 'Point'] = 1
        subsets.append(subset)
    if i % (round(0.01 * len(data), 0)) == 0:
        print("Progress: {}% ".format(round(100 * (i/len(data)))), end = "\r", flush = True)           

#Suss plots
subset = 2
pointX1 = subsets[subset].loc[subsets[1]['Point'] == 1].index.values[0]
pointX2 = pointX1 + 1
pointY1, pointY2 = subsets[subset].iloc[pointX1], subsets[subset].iloc[pointX2]

Points = pd.DataFrame((pointY1, pointY2))

#So the input for indicators as a nested dictionary
#{Name: {Columns: [Columns], Axis: [Axis]}, HorLine [yValues]}
#Name used as main key, columns for lookup in df and legend, axis for overlaying with OHLC or separate bottom chart
#Horizontal Line added if a reference horizontal line is requested (eg points for stochastic oscilator/cci/macd etc)

indicators = {'Bollinger Bands': {'Columns': ['BBHigh', 'BBMid', 'BBLow'], 'Axis': 0}, \
    'MACD': {'Columns': ['MACDLine', 'MACDSignal'], 'Axis': 1, 'Horizontal Line': [0]}}

plotCandlesWithPointIndicators(subsets[subset], Points, indicators, xtick_iter=12)

print("DebugPoint")