import pandas as pd
import ta
pd.set_option('mode.chained_assignment', None)

class DC_CCI:
    def __init__(self, CCI_window = 20, DC_periods = 20):

        self.Name = "DC_CCI"

        self.CCI_window = CCI_window
        self.DC_periods = DC_periods
        self.indicatorDf = None

    def addData(self, data):
        self.df = data
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

        self.df['CCI'] = [0] * len(self.df)
        self.df['D_UC'] = [0] * len(self.df)
        self.df['D_LC'] = [0] * len(self.df)
    
    def add_CCI(self):
        self.df['CCI'] = ta.trend.CCIIndicator(self.df['high'], self.df['low'], self.df['close'], window = self.CCI_window).cci()

    def add_DC(self):
        for i in range(self.DC_periods, len(self.df)):
            self.df['D_UC'].iloc[i] = max(self.df['high'].iloc[i-self.DC_periods:i])
            self.df['D_LC'].iloc[i] = min(self.df['low'].iloc[i-self.DC_periods:i])

    def determine_signal(self):
        
        action = 0

        if self.df['CCI'].iloc[-1] > 100 and self.df['high'].iloc[-1] >= self.df['D_UC'].iloc[-1]:
            action = 1

        elif self.df['CCI'].iloc[-1] < -100 and self.df['low'].iloc[-1] <= self.df['D_LC'].iloc[-1]:
            action = -1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'CCI', 'D_UC', 'D_LC']]

    def run(self, data):
        self.addData(data)
        self.add_CCI()
        self.add_DC()
        self.addIndicatorDf()
        
        return self.determine_signal(), self.indicatorDf