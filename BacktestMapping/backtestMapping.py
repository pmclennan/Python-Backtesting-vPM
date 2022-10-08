import pandas as pd
import os
import ta
import pytz

def backtestMapping3(historyData, tradeData):
    #Map 1 as profitable long, -1 as profitable short, 0 as no trade.
    #So if a long trade is unprofitable, map it as a profitable short and vice versa.

    mappingData = historyData.drop(columns = ['signal', 'action', 'position', 'P/L', 'Total profit', 'Executed price', 'Take Profit', 'Stop Loss'])

    tradeData['SignalMapping'] = [0] * len(tradeData)
    
    #Profitable Longs as 1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'buy') & (tradeData['Trade P/L'] > 0)] = 1
    #Non-profitable longs as -1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'buy') & (tradeData['Trade P/L'] < 0)] = -1
    #Profitable shorts as -1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'short') & (tradeData['Trade P/L'] > 0)] = -1
    #Non profitable shorts as 1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'short') & (tradeData['Trade P/L'] < 0)] = 1

    tradeData.rename(columns = {'Trade Open Time': 'time'}, inplace = True)

    mappingData = mappingData.merge(tradeData[['time', 'SignalMapping']], how = 'left', on = 'time')    
    mappingData['SignalMapping'].fillna(0, inplace = True)

    return mappingData

def backtestMappingTrueFalse(historyData, tradeData):
    #Here we are just mapping 1 for a correctly (profitable) predicted trade, and 0 if unprofitable. 

    mappingData = historyData.drop(columns = ['signal', 'action', 'position', 'P/L', 'Total profit', 'Executed price', 'Take Profit', 'Stop Loss'])

    tradeData['CorrectSignal'] = [0] * len(tradeData)
    tradeData['CorrectSignal'].loc[tradeData['Trade P/L'] > 0] = 1    

    tradeData.rename(columns = {'Trade Open Time': 'time'}, inplace = True)

    mappingData = mappingData.merge(tradeData[['time', 'CorrectSignal']], how = 'left', on = 'time')    

    return mappingData

def backtestMappingBoth(historyData, tradeData):

    mappingData = historyData.drop(columns = ['signal', 'action', 'position', 'P/L', 'Total profit', 'Executed price', 'Take Profit', 'Stop Loss'])
    
    tradeData['CorrectSignal'] = [0] * len(tradeData)
    tradeData['CorrectSignal'].loc[tradeData['Trade P/L'] > 0] = 1

    tradeData['SignalMapping'] = [0] * len(tradeData)
    #Profitable Longs as 1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'buy') & (tradeData['Trade P/L'] > 0)] = 1
    #Non-profitable longs as -1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'buy') & (tradeData['Trade P/L'] < 0)] = -1
    #Profitable shorts as -1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'short') & (tradeData['Trade P/L'] > 0)] = -1
    #Non profitable shorts as 1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'short') & (tradeData['Trade P/L'] < 0)] = 1

    tradeData.rename(columns = {'Trade Open Time': 'time'}, inplace = True)

    mappingData = mappingData.merge(tradeData[['time', 'Trade P/L', 'CorrectSignal', 'SignalMapping']], how = 'left', on = 'time')   
    mappingData['SignalMapping'].fillna(0, inplace = True)

    return mappingData

data_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\backtests\\pSAR_031022-140822_EURUSD.a_M5__2019-01-02_to_2020-12-31_20Limit"
history_filename = "History.csv"
trade_filename = 'Trade_Summary.csv'
history_dir = os.path.join(data_folder, history_filename)
trade_dir = os.path.join(data_folder, trade_filename)

historyData = pd.read_csv(history_dir)
tradeData = pd.read_csv(trade_dir)

mappingData = backtestMappingBoth(historyData, tradeData)

export_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\BacktestMapping\\Mapped Data"
export_filename = data_folder.split("\\")[-1] + "_Mapped.csv"
export_dir = os.path.join(export_folder, export_filename)

mappingData.to_csv(export_dir, index = False)
print("Exported")