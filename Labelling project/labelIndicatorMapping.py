import pandas as pd
import ta
import os
import datetime
import numpy as np
pd.options.mode.chained_assignment = None

def mapLabelsWithIndicators(labelDat, maxBars):

    #Clear out tail end
    dropIDX = labelDat[np.isnan(labelDat['exit_index'])].index.values[0]
    labelDat = labelDat[:dropIDX]
    labelDat['exit_bars'] = labelDat['exit_index'] - labelDat.index.values

    idxZeros = labelDat[labelDat['exit_bars'] > maxBars].index.values

    #For simplicity, reassign every 2 labelling just as 1.
    labelDat.loc[labelDat['label'] == 2, 'label'] = 1

    labelDat.loc[idxZeros, 'label'] = 0

    labelDat.drop(columns = ['exit_index', 'exit_bars'], inplace = True)

    ##Add Indicators
    
    #CCI
    CCI_window = 20
    labelDat['CCI'] = ta.trend.CCIIndicator(labelDat['high'], labelDat['low'], labelDat['close'], window = CCI_window).cci()

    #SMA
    SMA_window = 7
    labelDat['SMA'] = ta.trend.SMAIndicator(labelDat['close'], window = SMA_window).sma_indicator()
        
    #DC
    DC_periods = 20

    labelDat['D_UC'] = [0] * len(labelDat)
    labelDat['D_LC'] = [0] * len(labelDat)
    labelDat['D_MC'] = [0] * len(labelDat)

    for i in range(DC_periods, len(labelDat)):
        labelDat['D_UC'].iloc[i] = max(labelDat['high'].iloc[i - DC_periods:i])
        labelDat['D_LC'].iloc[i] = min(labelDat['low'].iloc[i - DC_periods:i])
        labelDat['D_MC'].iloc[i] = (labelDat['D_UC'].iloc[i] + labelDat['D_LC'].iloc[i])/2

    #pSAR
    labelDat['pSAR'] = ta.trend.PSARIndicator(high = labelDat['high'], low = labelDat['low'], close = labelDat['close'], step = 0.02, max_step = 0.2).psar()
   
    #MACD
    labelDat['macd_line'] = ta.trend.MACD(close = labelDat['close']).macd()
    labelDat['macd_signal'] = ta.trend.MACD(close = labelDat['close']).macd_signal()
    
    #Stochastic Oscilator
    labelDat['stoch_line'] = ta.momentum.StochasticOscillator(high = labelDat['high'], low = labelDat['low'], close = labelDat['close']).stoch()
    labelDat['stoch_signal'] = ta.momentum.StochasticOscillator(high = labelDat['high'], low = labelDat['low'], close = labelDat['close']).stoch_signal()

    #RSI
    labelDat["RSI"] = ta.momentum.RSIIndicator(close = labelDat['close'], window = 14).rsi()

    #Clear out NaNs - remove at front (indicators not generated), replace with zero elsewhere
    idxNan = labelDat[labelDat.isnull().any(axis = 1)].index.values
    idxNanDiff = idxNan[1:] - idxNan[:-1]
    lastDropIDX = int(np.where(idxNanDiff > 1)[0][0]) + 1
    labelDat = labelDat[lastDropIDX:].reset_index(drop = True)
    labelDat.fillna(value = 0, inplace = True)

    return labelDat

labelDat_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets\\EURUSD 4Y1Min labelling"
labelDat_filename = "EURUSD.a_M1__20170904_20210903-20-TP.csv"
labelDat_dir = os.path.join(labelDat_folder, labelDat_filename)

labelDat = pd.read_csv(labelDat_dir, index_col=0)
labelDat['time'] = pd.to_datetime(labelDat['date'] + ' ' + labelDat['time'])
labelDat = labelDat.drop(columns = ['date', 'tickvol', 'vol', 'spread'])

test1 = mapLabelsWithIndicators(labelDat, 180)

exportFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets\\EURUSD 4Y1Min labelling"
exportFilename = "EURUSDM1_20TP_withIndicators.csv"
exportDir = os.path.join(exportFolder, exportFilename)

test1.to_csv(exportDir)

print("Break Point")