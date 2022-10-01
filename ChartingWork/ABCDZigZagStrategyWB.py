import pandas as pd
import sys
import os
import time
import datetime
import pytz

sys.path.append(os.getcwd())
from trading_strategies.ZigZagWriter import ZigZagWriter
from ABCDStrategyWB import ABCDStrategy
from BacktestRunner import BacktestRunner

class ZigZagABCD:
    def __init__(self, ABCDThreshMean = 1.61, ABCDThreshVar = 0.05):
        self.ZigZagObject = ZigZagWriter()
        self.ABCDThreshMean = ABCDThreshMean
        self.ABCDThreshVar = ABCDThreshVar

    def ZigZagPrep(self, prelimData, startDate):
        self.ZigZagObject.readPrelimData(prelimData, startDate)

    def run(self, data):
        ZigZagDat = self.ZigZagObject.run(data, 1)
        ABCDStrat = ABCDStrategy(ZigZagDat, self.ABCDThreshMean, self.ABCDThreshVar)
        signal = ABCDStrat.run()

        return signal

dataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Symbols Method"
dataFilename = "EURUSD.a_M1_201709040000_202109031210.csv"
dataDir = os.path.join(dataFolder, dataFilename)
start_date = datetime.datetime(2021, 6, 1, tzinfo = pytz.utc)
end_date = datetime.datetime(2021, 9, 1, tzinfo = pytz.utc)

prelimDataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets\\ZigZag Comparison"
prelimDataFilename = "MT5ZigZagEURUSD.a_M1.csv"
prelimDataDir = os.path.join(prelimDataFolder, prelimDataFilename)
prelim_data = pd.read_csv(prelimDataDir, sep = '\t', parse_dates = ['time'])
renameDict = {'ZigZag(12,5,3) buffer 0': 'ZigZag Value', 'ZigZag(12,5,3) buffer 1': 'HighMapBuffer', 'ZigZag(12,5,3) buffer 2': 'LowMapBuffer'}
prelim_data.rename(columns = renameDict, inplace = True)
prelim_data['time'] = prelim_data['time'].dt.tz_localize(tz = pytz.utc)
prelim_data = prelim_data.loc[prelim_data['time'] < start_date]

exportFolder = os.path.join(os.getcwd(), "backtests")
one_pip = 0.0001
stop_loss = -25*one_pip
take_profit = 50*one_pip
guaranteed_sl = False
broker_cost = 2*one_pip
strategy = ZigZagABCD()
strategy.ZigZagPrep(prelim_data, start_date)

Backtest = BacktestRunner(start_date, end_date, 1, strategy, exportFolder, 0)
Backtest.readAndPrepData(dataDir, "\t", ['<DATE>', '<TIME>'])
Backtest.loadBroker(stop_loss, take_profit, guaranteed_sl, broker_cost)
Backtest.runBacktest(runType = 3)
Backtest.runReports()