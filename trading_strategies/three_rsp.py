import pandas as pd
import ta
from .IndicatorFunctions.StochasticOscilatorPM import StochasticOscilator

class ThreeRSP:
    def __init__(self):

        self.indicatorDf = None
        self.Name = "ThreeRSP"
        
    def addData(self, data):
        self.df = data
        self.open = self.df["open"]
        self.high = self.df["high"]
        self.low = self.df["low"]
        self.close = self.df["close"]        
    
    def calculate_pSAR(self):
        self.df["pSAR"] = ta.trend.PSARIndicator(high = self.high, low = self.low, close = self.close, step = 0.02, max_step = 0.2).psar()

    def calculate_RSI(self):
        self.df["RSI"] = ta.momentum.RSIIndicator(close = self.close, window = 14).rsi()

    def calculate_SO(self):
        self.df["slow_k"], self.df["slow_d"] = StochasticOscilator(self.df, K = 14, D = 3, slowing = 3)
        
    def determine_signal(self):

        action = 0

        close = self.df["close"]
        psar = self.df["pSAR"]
        rsi = self.df["RSI"]
        slow_k = self.df["slow_k"]
        slow_d = self.df["slow_d"]

        #Buy Criteria
        # Closing Price > pSAR
        # Slow k or Slow d < 30
        # RSI < 40

        if (close.iloc[-1] > psar.iloc[-1]) and (slow_k.iloc[-1] < 30 or slow_d.iloc[-1] < 30) and (rsi.iloc[-1] < 40):
            action = 1

        #Sell Criteria
        # Closing Price < pSAR
        # Slow k or Slow d > 70
        # RSI > 65
        
        elif (close.iloc[-1] < psar.iloc[-1]) and (slow_k.iloc[-1] > 70 or slow_d.iloc[-1] > 70) and (rsi.iloc[-1] > 65):
            action = -1
        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'pSAR', 'RSI', 'slow_k', 'slow_d']]

    def run(self, data):
        self.addData(data)
        self.calculate_pSAR()
        self.calculate_RSI()
        self.calculate_SO()
        self.addIndicatorDf()
        signal = self.determine_signal()

        return signal, self.indicatorDf