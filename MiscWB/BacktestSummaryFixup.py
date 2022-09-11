import pandas as pd
import os
import sys

sys.path.append(os.getcwd())

from WeeklySummary import get_weekly_summary
from BacktestSummary import get_backtest_summary
from TradeSummary import get_trade_summary

#Realise we had floating point error in trades and they weren't being flagged as "Tied" in the summary correctly.

def cleanHistoryRounding(historyDat):

    #Round rolling trade PnL
    historyDat.loc[:, 'P/L'] = round(historyDat.loc[:, 'P/L'], 5)

    #Recalc rolling gross PnL
    #Get indices 
    openIDXs = historyDat.loc[(historyDat['action'] == 'buy') | (historyDat['action'] == 'short')].index.values
    closeIDXs = historyDat.loc[(historyDat['action'] == 'close long') | (historyDat['action'] == 'close short')].index.values

    if len(openIDXs) > len(closeIDXs):
        lastOpenIdx = openIDXs[-1]
        openIDXs = openIDXs[:-1]

    idxPairs = [[a, b] for a, b in zip(openIDXs, closeIDXs)]
    idxPairs.append([lastOpenIdx, len(historyDat)+1])

    for idxPair in idxPairs:
        prevGrossPnL = historyDat.loc[idxPair[0]-1, 'Total profit']
        tradePnL = historyDat.loc[idxPair[0], 'P/L']
        newGrossPnL = tradePnL + prevGrossPnL
        historyDat.loc[idxPair[0]:idxPair[1]-1, 'Total profit'] = round(newGrossPnL, 5)

    return historyDat

#Directory
parentFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets\\4 Year Tests"
childFolder = "ThreeRSP 070922-124934_EURUSD.a_M1__2017-09-04_to_2021-09-01"
folderName = os.path.join(parentFolder, childFolder)

#Read
historyFilename = "History.csv"
historyDir = os.path.join(folderName, historyFilename)
historyDat = pd.read_csv(historyDir, parse_dates=['time'])

newHistoryDat = cleanHistoryRounding(historyDat)
#newBacktestSummary = get_backtest_summary(newHistoryDat, 'EURUSD', 'M1')
#newWeeklySummary = get_weekly_summary(newHistoryDat, 'M1')
newTradeSummary = get_trade_summary(newHistoryDat)

print("Break Point")