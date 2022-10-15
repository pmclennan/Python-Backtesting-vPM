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
from trading_strategies.NoLimitModel import NoLimitModelZigZag
from trading_strategies.NoLimitModelZZpSARMACD import NoLimitModelZZpSARMACD

tz = pytz.utc
startDate = datetime.datetime(2021, 10, 10, tzinfo = tz) #Start Date - adjust as necessary
endDate = datetime.datetime(2022, 2, 10, tzinfo = tz) #End Date - adjust as necessary
dataFolder = os.path.join(os.getcwd(), 'Datasets', 'CombinedDatasets')
dataFilename = "EURUSD.a_M5_14102021_02092022.csv"
dataDir = os.path.join(dataFolder, dataFilename)
timeCols = 'DATETIME'
delimitter = None

one_pip = 0.0001
guaranteed_sl = False
broker_cost = 2*one_pip

exportFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Backtests"

##Example of loading a DL strategy that requires an indicator strategy
model_folder = os.path.join(os.getcwd(), "DLModels", "NoLimitHitModels")
model_filename = "GRU_ZZInd_NLH 13-10-2022 22-44-02.h5"
model_loc = os.path.join(model_folder, model_filename)
model = keras.models.load_model(model_loc)

exportFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Backtests"

##IMPORTANT
#If you are feeding the data as a directory and wishing the backtesting system to format/prep for report based on filename, please use .readAndPrepData()
#If feeding data directly (ie reading above), please use inputDataAndInfo

dataFolder = os.path.join(os.getcwd(), 'Datasets', 'CombinedDatasets')
dataFilename = "EURUSD.a_M5_14102021_02092022.csv"
dataDir = os.path.join(dataFolder, dataFilename)
backtestStartDate = datetime.datetime(2021, 10, 13, tzinfo = pytz.utc)
end_date = datetime.datetime(2022, 9, 3, tzinfo = pytz.utc)
delimitter = None
timeCols = 'DATETIME'

ZigZagDatFolder = os.path.join(os.getcwd(), 'Datasets', 'ZigZagPrelim')
ZigZagDatFilename = "ZigZagMT5_20211014_20220903_EURUSD.a_M5.csv"
ZigZagDatDir = os.path.join(ZigZagDatFolder, ZigZagDatFilename)
ZigZagDat = pd.read_csv(ZigZagDatDir, sep = '\t', encoding = 'UTF-16', parse_dates = ['time'])
renameDict = {'ZigZag(12,5,3) buffer 0': 'ZigZagValue', 'ZigZag(12,5,3) buffer 1': 'MaxBuffer', 'ZigZag(12,5,3) buffer 2': 'MinBuffer'}
ZigZagDat.rename(columns = renameDict, inplace = True)
ZigZagDat['time'] = ZigZagDat['time'].dt.tz_localize(tz = pytz.utc)

strategy = NoLimitModelZZpSARMACD(model, ZigZagDat)

stop_loss = -10 * one_pip
take_profit = 20 * one_pip
Backtest = BacktestRunner(startDate, endDate, 160, strategy, exportFolder)
Backtest.readAndPrepData(dataDir, delimitter, timeCols)
Backtest.loadBroker(stop_loss, take_profit, guaranteed_sl, broker_cost)
Backtest.runBacktest(2)
Backtest.runReports()
print("Total PnL: {}".format(round(Backtest.broker.total_profit, 6)))

print("DebugPoint")