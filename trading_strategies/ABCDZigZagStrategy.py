import pandas as pd
import sys
import os
import datetime
import pytz

sys.path.append(os.getcwd())
from trading_strategies.ZigZagWriter import ZigZagWriter
from trading_strategies.ABCDStrategyWriter import ABCDStrategy

class ZigZagABCD:
    def __init__(self, ABCDThreshMean = 1.61, ABCDThreshVar = 0.05):
        self.ZigZagObject = ZigZagWriter()
        self.ABCDThreshMean = ABCDThreshMean
        self.ABCDThreshVar = ABCDThreshVar
        self.Name = "ZigZagABCD"

    def ZigZagPrep(self, prelimData, startDate):
        self.ZigZagObject.readPrelimData(prelimData, startDate)

    def addIndicators(self, data):
        self.indicatorDF = self.ZigZagDat[['time', 'LowMapBuffer', 'HighMapBuffer', 'ZigZag Value', 'ZigZag Type']].iloc[-len(data):].reset_index(drop = True)

    def run(self, data):        
        self.ZigZagDat = self.ZigZagObject.run(data, 1)
        self.addIndicators(data)
        ABCDStrat = ABCDStrategy(self.ZigZagDat, self.ABCDThreshMean, self.ABCDThreshVar)
        signal = ABCDStrat.run()

        return signal, self.indicatorDF