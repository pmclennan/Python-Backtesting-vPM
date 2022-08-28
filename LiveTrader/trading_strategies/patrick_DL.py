import pandas as pd 
import numpy as np
import ta
#import trading_strategies.visualise as v
import keras.models
#from keras.layers import LSTM
#from sklearn.preprocessing import MinMaxScaler

class Patrick_Model:
    def __init__(self, data, model_loc):
        self.df = data
        self.DL_model = keras.models.load_model(model_loc)
            
    def determine_signal(self,dframe, model):

        #Initialise action as 0 (holding)
        #Set variable for close price

        action = 0 
        close = dframe['close'] 

        #Shape input for LSTM - last 10 observed close values - and evaluate predictions

        input = np.reshape(np.array(close.iloc[-11:-1]), (1, 10, 1))
        prediction = model.predict(input)

        #Buy signal = 1 -> next step prediction is higher than current (last observed) close

        if prediction > close.iloc[-1]:
            action = 1

        #Sell signal = -1 -> next step prediction is lower than current (last observed) close

        if prediction < close.iloc[-1]:
            action = -1
        
        print(prediction)
        return action

    def patrick_LSTM(self):
        return self.determine_signal(self.df, self.DL_model)