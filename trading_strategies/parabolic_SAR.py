import pandas as pd
import ta

class pSAR:
    def __init__(self):

        self.Name = 'pSAR'
        self.indicatorDf = None

    def addData(self, data):
        
        self.df = data
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']
        
        self.df['pSAR'] = [0] * len(self.df)
    
    def add_pSAR(self):
        self.df["pSAR"] = ta.trend.PSARIndicator(high = self.high, low = self.low, close = self.close, step = 0.02, max_step = 0.2).psar()
        self.pSAR = self.df['pSAR']

    def determine_signal(self):

        action = 0

        #Sell Criteria - current pSAR above close, previous pSAR below close
        if self.pSAR.iloc[-1] > self.close.iloc[-1] and self.pSAR.iloc[-2] < self.close.iloc[-2]:
            action = -1

        #Buy Criteria - current pSAR below close, previous pSAR above close
        elif self.pSAR.iloc[-1] < self.close.iloc[-1] and self.pSAR.iloc[-2] > self.close.iloc[-2]:
            action = 1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'pSAR']]

    def run(self, data):
        self.addData(data)
        self.add_pSAR()
        self.addIndicatorDf()
        
        return self.determine_signal(), self.indicatorDf