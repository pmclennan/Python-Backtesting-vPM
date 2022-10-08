from logging import exception
from unittest import case
import pandas as pd
import pytz 
import os
import datetime
import sys
import time
from collections import deque

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf 
import keras.models

sys.path.append(os.getcwd())
from signalHandler import signalHandler
from trading_strategies import three_rsp
from WeeklySummary import get_weekly_summary
from TradeSummary import get_trade_summary
from visualise import visualise
from BacktestRunner import BacktestRunner
from trading_strategies.DLSignalAffirmer import signalAffirmerModel
from trading_strategies.three_rsp import ThreeRSP
from trading_strategies.parabolic_SAR import pSAR
from trading_strategies.pSAR_SO import pSAR_SO
from trading_strategies.ZigZagWriter import ZigZagWriter
from trading_strategies.ABCDZigZagStrategy import ZigZagABCD

exportFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Backtests"

#ABCD

dataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\CombinedDatasets"
dataFilename = "EURUSD.a_M5_14102021_02092022.csv"
dataDir = os.path.join(dataFolder, dataFilename)
backtestStartDate = datetime.datetime(2021, 10, 13, tzinfo = pytz.utc)
end_date = datetime.datetime(2021, 10, 28, tzinfo = pytz.utc)
delimitter = None
timeCols = 'DATETIME'

start_date = datetime.datetime(2021, 10, 14, hour = 17, minute = 15, tzinfo = pytz.utc)
prelimDataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\ZigZagPrelim"
prelimDataFilename = "MT5ZigZag_20200101_20211014EURUSD.a_M5.csv"
prelimDataDir = os.path.join(prelimDataFolder, prelimDataFilename)
prelim_data = pd.read_csv(prelimDataDir, sep = '\t', encoding = 'UTF-16', parse_dates = ['time'])
renameDict = {'ZigZag(12,5,3) buffer 0': 'ZigZag Value', 'ZigZag(12,5,3) buffer 1': 'HighMapBuffer', 'ZigZag(12,5,3) buffer 2': 'LowMapBuffer'}
prelim_data.rename(columns = renameDict, inplace = True)
prelim_data['time'] = prelim_data['time'].dt.tz_localize(tz = pytz.utc)
prelim_data = prelim_data.loc[prelim_data['time'] < start_date]

one_pip = 0.0001
stop_loss = -10*one_pip
take_profit = 30*one_pip
guaranteed_sl = False
broker_cost = 2*one_pip
#limit = 20

strategy = ZigZagABCD()
strategy.ZigZagPrep(prelim_data, start_date)

#stop_loss = -limit * one_pip
#take_profit = limit * one_pip
Backtest = BacktestRunner(start_date, end_date, 1, strategy, exportFolder)
Backtest.readAndPrepData(dataDir, delimitter, timeCols)
Backtest.loadBroker(stop_loss, take_profit, guaranteed_sl, broker_cost)
Backtest.runBacktest(3)
Backtest.runReports()
print("Total PnL: {}".format(round(Backtest.broker.total_profit, 6)))

print("DEBUG POINT")