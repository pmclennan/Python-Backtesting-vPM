import pandas as pd
import ta
import numpy as np
pd.set_option('mode.chained_assignment', None)

class DC_CCI_SMA:
    def __init__(self, CCI_window = 20, DC_periods = 20, SMA_window = 7, crossover_lookback = 5):

        self.Name ="DC_CCI_SMA"

        self.CCI_window = CCI_window
        self.DC_periods = DC_periods
        self.SMA_window = SMA_window
        self.crossover_lookback = crossover_lookback
        self.indicatorDf = None

    def addData(self, data):
        self.df = data
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

        self.df['CCI'] = [0] * len(self.df)
        self.df['D_UC'] = [0] * len(self.df)
        self.df['D_LC'] = [0] * len(self.df)
        self.df['D_MC'] = [0] * len(self.df)
        self.df['SMA'] = [0] * len(self.df)        

    def add_CCI(self):
        self.df['CCI'] = ta.trend.CCIIndicator(self.df['high'], self.df['low'], self.df['close'], window = self.CCI_window).cci()

    def add_DC(self):
        for i in range(self.DC_periods, len(self.df)):
            self.df['D_UC'].iloc[i] = max(self.df['high'].iloc[i-self.DC_periods:i])
            self.df['D_LC'].iloc[i] = min(self.df['low'].iloc[i-self.DC_periods:i])
            self.df['D_MC'].iloc[i] = (self.df['D_UC'].iloc[i] + self.df['D_LC'].iloc[i])/2

    def add_SMA(self):
        self.df['SMA'] = ta.trend.SMAIndicator(self.df['close'], window = self.SMA_window).sma_indicator()

    def determine_signal(self):
        
        action = 0

        if len(np.where(self.df['SMA'].iloc[-self.crossover_lookback:] <= self.df['D_MC'].iloc[-self.crossover_lookback:])[0]) != 0 \
            and len(np.where(self.df['SMA'].iloc[-self.crossover_lookback:] >= self.df['D_MC'].iloc[-self.crossover_lookback:])[0]) != 0:

            if self.df['CCI'].iloc[-1] > 100 and self.df['high'].iloc[-1] >= self.df['D_UC'].iloc[-1] \
                and max(np.where(self.df['SMA'].iloc[-self.crossover_lookback:] <= self.df['D_MC'].iloc[-self.crossover_lookback:])[0])\
                    < min(np.where(self.df['SMA'].iloc[-self.crossover_lookback:] >= self.df['D_MC'].iloc[-self.crossover_lookback:])[0]):
                action = 1

            elif self.df['CCI'].iloc[-1] < -100 and self.df['low'].iloc[-1] <= self.df['D_LC'].iloc[-1] \
                and max(np.where(self.df['SMA'].iloc[-self.crossover_lookback:] >= self.df['D_MC'].iloc[-self.crossover_lookback:])[0])\
                    < min(np.where(self.df['SMA'].iloc[-self.crossover_lookback:] <= self.df['D_MC'].iloc[-self.crossover_lookback:])[0]):
                action = -1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'CCI', 'D_UC', 'D_LC', 'D_MC', 'SMA']]

    def run(self, data):
        self.addData(data)
        self.add_CCI()
        self.add_DC()
        self.add_SMA()
        self.addIndicatorDf()
        
        return self.determine_signal(), self.indicatorDf