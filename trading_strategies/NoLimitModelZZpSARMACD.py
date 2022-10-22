import pandas as pd 
import numpy as np
import ta

class NoLimitModelZZpSARMACD:
    def __init__(self, model, ZigZagDat):
        self.model = model     
        self.sequence_length = self.model.input_shape[1]
        self.scaled_data = None
        self.input = None
        self.ZigZagDat = ZigZagDat
        self.Name = "NoLimitZigZag"
        self.input_sequence = None

    def add_data(self, data):
        self.data = data.reset_index(drop = True)

    def clean_columns(self):        
        self.data = self.data[['time', 'open', 'high', 'low', 'close']]
        self.InputData = self.data[['open', 'high', 'low', 'close']]

    def add_indicator(self):
        TempZigZag = self.ZigZagDat.loc[(self.ZigZagDat['time'] >= self.data['time'].iloc[0]) & (self.ZigZagDat['time'] <= self.data['time'].iloc[-1])].reset_index(drop = True)
        TempZigZag['MinMax'] = [0] * len(TempZigZag)
        TempZigZag.loc[TempZigZag['MaxBuffer'] != 0, 'MinMax'] = 1
        TempZigZag.loc[TempZigZag['MinBuffer'] != 0, 'MinMax'] = -1
        self.InputData['MinMax'] = TempZigZag['MinMax']
        self.InputData['OC'] = self.InputData['open'] - self.InputData['close']
        self.InputData['HL'] = self.InputData['high'] - self.InputData['low']
        self.InputData['pSAR'] = ta.trend.PSARIndicator(high = self.InputData['high'], low = self.InputData['low'], close = self.InputData['close'], step = 0.02, max_step = 0.2).psar()
        self.InputData['closepSar'] = self.InputData['close'] - self.InputData['pSAR']
        self.InputData['MACDLine'] = ta.trend.MACD(close=self.InputData['close']).macd()
        self.InputData['MACDSignal'] = ta.trend.MACD(close=self.InputData['close']).macd_signal()
        self.InputData['MACDDiff'] = self.InputData['MACDLine'] - self.InputData['MACDSignal']

    def scale_input(self):
        
        rowMax = self.input_sequence.max(axis = 1)
        rowMin = self.input_sequence.max(axis = 1)
        self.input_sequence_scaled = (self.input_sequence - rowMin[:, np.newaxis]) / (rowMax[:, np.newaxis] - rowMin[:, np.newaxis])
        self.input_sequence_scaled = np.reshape(self.input_sequence_scaled, (1, self.input_sequence_scaled[-1].shape[0], self.input_sequence_scaled[-1].shape[1]))

    def sequence_input(self):
        X = []
        X.append(self.InputData.iloc[len(self.data)-self.sequence_length:])
        X = np.array(X)
        #X = np.reshape(X[-1], (1, X[-1].shape[0], X[-1].shape[1]))

        self.input_sequence = X
                    
    def determine_signal(self):

        action = 0

        prediction = self.model.predict(self.input_sequence_scaled)

        action = np.argmax(prediction, axis = 1) - 1

        return action[0]

    def run(self, data):
        self.add_data(data)
        self.clean_columns()
        self.add_indicator()       
        self.sequence_input() 
        self.scale_input()        
        return self.determine_signal()