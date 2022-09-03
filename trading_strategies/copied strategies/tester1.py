import pandas as pd

class Test_1:
    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))

    def determine_signal(self,dframe):
        # sell = -1, hold = 0, buy = 1, initialise all as hold first

        action = 0
        close = dframe['close']

        #Buy
        if close.iloc[-1] < 0.7250:
            action = 1

        #Sell
        if close.iloc[-1] > 0.7250:
            action = -1
        
        return action, close.iloc[-1] - 0.7250

    def run_X(self):
        return self.determine_signal(self.df), self.df