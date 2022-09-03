import pandas as pd
import numpy as np
import keras.models

class Test_2:
    def __init__(self, file_path, model_loc):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.DL_model = keras.models.load_model(model_loc)
            
    def determine_signal(self,dframe, model):
        # sell = -1, hold = 0, buy = 1, initialise all as hold first

        action = 0
        close = dframe['close']

        input = np.reshape(np.array(close.iloc[-11:-1]), (1, 10, 1))
        prediction = model.predict(input)

        #Buy
#        if close.iloc[-1] < 0.7250:
#            action = 1

        #Sell
#        if close.iloc[-1] > 0.7250:
#            action = -1

        #Buy
        if close.iloc[-1] > prediction:
            action = 1

        #Sell
        if close.iloc[-1] < prediction:
            action = -1
        

        #return action, close.iloc[-1] - 0.7250
        return action, prediction

    def run_Y(self):
        return self.determine_signal(self.df, self.DL_model), self.df