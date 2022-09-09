import pandas as pd 
import numpy as np
import ta
from sklearn.preprocessing import MinMaxScaler

class indicatorModel:
    def __init__(self, data, model, scaler):
        self.data = data
        self.model = model
        self.scaler = scaler
        self.sequence_length = self.model.input_shape[1]
        self.scaled_data = None
        self.input = None

    def clean_columns(self):
        self.data = self.data[['open', 'high', 'low', 'close', 'bid', 'ask']]

    def add_indicator(self):
        self.data['pSAR'] = ta.trend.PSARIndicator(high = self.data['high'], low = self.data['low'], close = self.data['close'], step = 0.02, max_step = 0.2).psar()

    def scale_input(self):
        
        scaler = self.scaler
        X = pd.DataFrame(scaler.transform(self.data), columns = self.data.columns)

        self.scaled_data = X

    def sequence_input(self):
        X = []
        for i in range(0, len(self.data) - self.sequence_length):
            end = i + self.sequence_length
            X.append(self.data.iloc[i:end])

        X = np.array(X)
        X = np.reshape(X[-1], (1, X[-1].shape[0], X[-1].shape[1]))

        self.input_sequence = X  
                    
    def determine_signal(self):

        action = 0

        prediction = self.model.predict(self.input_sequence)

        action = np.argmax(prediction, axis = 1) - 1

        return action[0]

    def run_indicatorDL(self):
        self.clean_columns()
        self.add_indicator()       
        self.scale_input()
        self.sequence_input() 
        return self.determine_signal()