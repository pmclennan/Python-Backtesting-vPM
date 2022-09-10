import pandas as pd
import os
import ta
import pytz

def backtestMapping(historyData, tradeData):
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

data_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\backtests\\forMapping\\DC CCI 030922-150025_EURUSD_M5__2021-10-14_to_2022-08-26"
history_filename = "History.csv"
trade_filename = 'Trade_Summary.csv'
history_dir = os.path.join(data_folder, history_filename)
trade_dir = os.path.join(data_folder, trade_filename)

historyData = pd.read_csv(history_dir)
tradeData = pd.read_csv(trade_dir)

mappingData = backtestMapping(historyData, tradeData)

export_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\BacktestMapping\\Mapped Data"
export_filename = "DC_CCI_EURUSDM5_2021-10-14_to_2022-08-26.csv"
export_dir = os.path.join(export_folder, export_filename)

mappingData.to_csv(export_dir, index = False)