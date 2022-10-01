import pandas as pd
import sys
import os
import time
import datetime
import pytz

sys.path.append(os.getcwd())
from trading_strategies.ZigZagWriter import ZigZagWriter
from UtilsPM.DataReaders import MT5SymbolsDataReader

class ABCDStrategy:
    def __init__(self, ZigZagData, threshMean = 1.61, threshVar = 0.05):

        self.ZigZagData = ZigZagData        
        self.threshMean = threshMean
        self.threshVar = threshVar

    def checkConditions(self, direction):
        #Note here that we look up to the second last point (hence the iloc[:-1])
        #As we have the condition based on bar next after the C point
                
        APoint = self.ZigZagData.iloc[:-1].loc[self.ZigZagData['ZigZag Value'] != 0].iloc[-3]
        BPoint = self.ZigZagData.iloc[:-1].loc[self.ZigZagData['ZigZag Value'] != 0].iloc[-2]
        CPoint = self.ZigZagData.iloc[:-1].loc[self.ZigZagData['ZigZag Value'] != 0].iloc[-1]

        Apx = APoint['ZigZag Value']
        Bpx = BPoint['ZigZag Value']
        Cpx = CPoint['ZigZag Value']    

        AB_BC_diff = (abs(Bpx - Apx))/(abs(Cpx - Bpx))

        if (self.threshMean - self.threshVar <= AB_BC_diff <= self.threshMean + self.threshVar):

            if direction == 'Up' and (Apx < Cpx < Bpx) and Cpx < self.ZigZagData.loc[CPoint.name + 1, 'low']:

                return 1

            elif direction == 'Down' and (Apx > Cpx > Bpx) and Cpx > self.ZigZagData.loc[CPoint.name + 1, 'high']:
                
                return -1
            
        else:
            return 0

    def run(self):

        signal = 0

        #Check if the current bar is not a drawn Zig/Zag
        #Given the condition based on Bar after C.
        #This current bar/ZigZag point will get picked up on the next bar process anyway.

        if self.ZigZagData['ZigZag Type'].iloc[-1] != 'valley' or self.ZigZagData['ZigZag Type'].iloc[-1] != 'peak':
            
            #DownTrend
            if self.ZigZagData['ZigZag Type'].iloc[-2] == 'valley':
                signal = self.checkConditions('Up')
            #Uptrend
            elif self.ZigZagData['ZigZag Type'].iloc[-2] == 'peak':
                signal = self.checkConditions('Down')

        return signal

# dataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Symbols Method"
# dataFilename = "EURUSD.a_M1_201709040000_202109031210.csv"
# dataDir = os.path.join(dataFolder, dataFilename)
# data = MT5SymbolsDataReader(dataDir)

# start_date = datetime.datetime(2021, 6, 1, tzinfo = pytz.utc)
# test_data = data.loc[data['time'] >= start_date].reset_index(drop = True)

# prelimDataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets\\ZigZag Comparison"
# prelimDataFilename = "MT5ZigZagEURUSD.a_M1.csv"
# prelimDataDir = os.path.join(prelimDataFolder, prelimDataFilename)
# prelim_data = pd.read_csv(prelimDataDir, sep = '\t', parse_dates = ['time'])
# renameDict = {'ZigZag(12,5,3) buffer 0': 'ZigZag Value', 'ZigZag(12,5,3) buffer 1': 'HighMapBuffer', 'ZigZag(12,5,3) buffer 2': 'LowMapBuffer'}
# prelim_data.rename(columns = renameDict, inplace = True)
# prelim_data['time'] = prelim_data['time'].dt.tz_localize(tz = pytz.utc)
# prelim_data = prelim_data.loc[prelim_data['time'] < start_date]

# o = ZigZagWriter()
# o.readPrelimData(prelim_data, start_date)
# signalList = []

# t0 = time.time()
# for counter, row in test_data.iterrows():
        
#     ZigZagDat = o.run(row, 1)
#     strategy = ABCDStrategy(ZigZagDat)
#     signal = strategy.run()
#     signalList.append(signal)
#     if signal != 0:
#         print("CheckPoint")


# t1 = time.time()

# print("Time Taken: {}".format(datetime.timedelta(seconds = t1-t0)))
# print("Approx time per bar: {}".format(datetime.timedelta(seconds = t1-t0)/len(test_data)))
# print("DebugPoint")