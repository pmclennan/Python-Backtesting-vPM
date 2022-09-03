import pandas as pd
import ta

class ThreeRSP:
    def __init__(self, data):
        self.df = data
        self.open = self.df["open"]
        self.high = self.df["high"]
        self.low = self.df["low"]
        self.close = self.df["close"]
        self.indicatorDf = None
        
    def calculate_pSAR(self):
        self.df["pSAR"] = ta.trend.PSARIndicator(high = self.high, low = self.low, close = self.close, step = 0.02, max_step = 0.2).psar()

    def calculate_RSI(self):
        self.df["RSI"] = ta.momentum.RSIIndicator(close = self.close, window = 14).rsi()

    def calculate_SO(self):
        
        #Try 1
        #stoch_obj = ta.momentum.StochasticOscillator(high = self.high, low = self.low, close = self.close, window = 5, smooth_window = 3)
        #self.df["slow_k"], self.df["slow_d"] = stoch_obj.stoch(), stoch_obj.stoch_signal()
        
        #Try 3
        #self.df["slow_k"], self.df["slow_d"] = ta.momentum.STOCH(high = self.high, low = self.low, close = self.close, fastk_period = 5, slowk_period = 3, slowk_matype = 0, slowd_period = 3, slowd_matype = 0)
        
        #Try 3
        #n_high = self.high.rolling(5).max()
        #n_low = self.low.rolling(5).min()
        #self.df["slow_k"] = ((self.close[-1] - n_high.iloc[-1]) * 100) / (n_high.iloc[-1] - n_low.iloc[-1])
        #self.df["slow_d"] = self.df["slow_k"].rolling(3).mean()

        #Try 4
        #n_high = self.high[-5:-1].max()
        #n_low = self.high[-5:-1].min()
        #self.df["slow_k"] = ((self.close[-1] - n_high) * 100) / (n_high - n_low)
        #self.df["slow_d"] = self.df["slow_k"].rolling(3).mean()

        #Try 5
        stoch_obj = ta.momentum.StochasticOscillator(high = self.high, low = self.low, close = self.close, window = 5, smooth_window = 3)
        self.df["slow_k"] = stoch_obj.stoch().rolling(3).mean()
        self.df["slow_d"] = self.df["slow_k"].rolling(3).mean()

    def determine_signal(self, dframe):

        action = 0

        close = dframe["close"]
        psar = dframe["pSAR"]
        rsi = dframe["RSI"]
        slow_k = dframe["slow_k"]
        slow_d = dframe["slow_d"]

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

    def run_3RSP(self):
        self.calculate_pSAR()
        self.calculate_RSI()
        self.calculate_SO()
        self.addIndicatorDf()
        signal = self.determine_signal(self.df)

        return signal, self.indicatorDf