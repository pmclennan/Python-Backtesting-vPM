import pandas as pd 
import numpy as np

class signalAffirmerModel:
    def __init__(self, model, indicatorStrategy):
        self.model = model
        self.indicatorStrategyClass = indicatorStrategy
        self.sequenceLength = self.model.input_shape[1]
        self.Name = "signalAffirmerModel"

    def runIndicator(self):
        self.indicatorStrategy = self.indicatorStrategyClass()
        self.indicatorSignal, self.indicatorDf = self.indicatorStrategy.run(self.data) 
        
    def prepareInput(self):

        self.inputData = self.inputData.merge(self.indicatorDf, how = 'inner', on = 'time').drop(columns = 'time').reset_index(drop = True)
        X = self.inputData[len(self.inputData)-self.sequenceLength:]
        rowMax = np.array(X.max(axis = 0))
        self.scaledData = np.array(X / rowMax)
        self.scaledData = np.reshape(self.scaledData, (1, self.scaledData.shape[0], self.scaledData.shape[1]))
                    
    def determineSignal(self):

        prediction = round(self.model.predict(self.scaledData)[0][0])
        action = prediction * self.indicatorSignal

        return action

    def run(self, data):        
        self.data = data
        self.inputData = self.data[['time', 'open', 'high', 'low', 'close']]
        self.runIndicator()
        if self.indicatorSignal != 0:
            self.prepareInput()              
            signal = self.determineSignal()
        else:
            signal = 0
        return signal