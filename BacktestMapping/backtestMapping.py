import pandas as pd
import os
import ta
import pytz

def backtestMapping(historyData, tradeData):
    #Map 1 as profitable long, -1 as profitable short, 0 as no trade.
    #So if a long trade is unprofitable, map it as a profitable short and vice versa.

    mappingData = historyData.drop(columns = ['signal', 'action', 'position', 'P/L', 'Total profit', 'Executed price', 'Take Profit', 'Stop Loss'])

    mappingList = [0] * len(historyData)

    for i in range(len(tradeData)-1):
        insertIdx = historyData[historyData['time'] == tradeData.loc[i, 'Trade Open Time']].index.values[0]
        
        if tradeData.loc[i, 'Trade Type'] == 'buy':            
            if tradeData.loc[i, 'Trade P/L'] > 0:
                mappingList[insertIdx] = 1
            elif tradeData.loc[i, 'Trade P/L'] < 0:
                mappingList[insertIdx] = -1
        
        elif tradeData.loc[i, 'Trade Type'] == 'short':
            if tradeData.loc[i, 'Trade P/L'] > 0:
                mappingList[insertIdx] = -1
            elif tradeData.loc[i, 'Trade P/L'] < 0:
                mappingList[insertIdx] = 1

    mappingData['SignalMapping'] = mappingList

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