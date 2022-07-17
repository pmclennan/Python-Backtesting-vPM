import pandas as pd
import ta

class DC_CCI:
    def __init__(self, data, CCI_window, DC_periods):

        self.df = data
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

        self.CCI_window = CCI_window
        self.DC_periods = DC_periods

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

        if self.df['CCI'].iloc[-1] > 150 and self.df['high'].iloc[-1] >= self.df['D_UC'].iloc[-1]:
            action = 1

        elif self.df['CCI'].iloc[-1] < -150 and self.df['low'].iloc[-1] <= self.df['D_LC'].iloc[-1]:
            action = -1

        return action

    def run_DC_CCI(self):
        self.add_CCI()
        self.add_DC()
        
        return self.determine_signal()