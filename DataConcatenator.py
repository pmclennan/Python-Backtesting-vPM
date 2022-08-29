import pandas as pd
import datetime
import os
import numpy as np

def ratesTicksConcatenator(ratesDat, ticksDat, floorFreq, ticksCleanFlag = 1, replacementSpread = 3):
   
    timeCol = ratesDat.columns[0]

    #Replacement Policy:
        #1: Replace extreme (spread > 1000pips) & zeroes with spread average of past 5/forward 5 values
        #2: Replace extreme & missing bid/ask with close +- replacementSpread parameter        

    #Get occurences where there is both ASK & BID Data
   
    #Replace extreme values (spread > 1000pips) - have seen this before 
    extremeIdx = ticksDat.loc[abs(ticksDat['ASK'] - ticksDat['BID']) > 0.1].index.values
    ticksDat.loc[extremeIdx, ['BID', 'ASK']] = np.nan
    
    #Clear out the rest of nans
    ticksDat = ticksDat[-(ticksDat['ASK'].isnull() | ticksDat['BID'].isnull())]

    #Floor
    ticksDat.loc[:, timeCol] = ticksDat[timeCol].dt.floor(freq = floorFreq)

    #Merge
    concatDF = ratesDat.merge(ticksDat, how = 'left', on = timeCol).groupby(timeCol).first().reset_index()

    #Replace values    
    missingIDX = concatDF[concatDF['BID'].isnull() | concatDF['ASK'].isnull()].index.values

    if ticksCleanFlag == 1:
        #Average spread of 5 behind / 5 forward rounded to nearest pip
        #NB if unavailable for forward 5 (near end of Data), shift this range back as appropriate (and vice versa if at the start)
            # IE if 4 indexes from the end, use 7 behind / 3 forward rather than 5 / 5
        for idx in missingIDX:
            if len(concatDF) - idx <= 5:
                shiftFactor = (len(concatDF) - idx) - 6
            elif idx <= 5:                
                shiftFactor = 1 - idx
            else:
                shiftFactor = 0

            idxGroup = list(np.arange(idx-5+shiftFactor, idx)) + list(np.arange(idx+1, idx+6+shiftFactor))
            avgBidSpread = round(np.mean(abs(concatDF['BID'].iloc[idxGroup] - concatDF['CLOSE'].iloc[idxGroup])), 5)
            avgAskSpread = round(np.mean(abs(concatDF['ASK'].iloc[idxGroup] - concatDF['CLOSE'].iloc[idxGroup])), 5)
            concatDF['BID'].iloc[idx] = concatDF['CLOSE'].iloc[idx] - avgBidSpread
            concatDF['ASK'].iloc[idx] = concatDF['CLOSE'].iloc[idx] + avgAskSpread

    elif ticksCleanFlag == 2:
        #Flat spread
        for idx in missingIDX:
            concatDF['BID'].iloc[idx] = concatDF['CLOSE'].iloc[idx] - (replacementSpread/10000)
            concatDF['ASK'].iloc[idx] = concatDF['CLOSE'].iloc[idx] + (replacementSpread/10000)

    #Flag replaced values
    replacedBidAskList = [''] * len(concatDF)
    for idx in missingIDX:
        replacedBidAskList[idx] = 'Replaced'

    concatDF['ReplacedBidAsk'] = replacedBidAskList

    concatDF = concatDF[[timeCol, 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'BID', 'ASK', 'ReplacedBidAsk']]

    return concatDF

datFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\Python-Backtesting-vPM\\Datasets\\ConcatWB"

ratesFileName = "EURUSD_M5_202108270000_202208262355.csv"
ticksFileName = "EURUSD_202108270000_202208262356.csv"

ratesDir = os.path.join(datFolder, ratesFileName)
ticksDir = os.path.join(datFolder, ticksFileName)

ratesDat = pd.read_csv(ratesDir, sep = "\t", parse_dates = [[0, 1]])
ticksDat = pd.read_csv(ticksDir, sep = "\t", parse_dates = [[0, 1]])

for oldCol in ratesDat.columns:
    ratesDat.rename(columns = {oldCol: oldCol.replace('<', '').replace('>', '').replace('_', '')}, inplace = True)

for oldCol in ticksDat.columns:
    ticksDat.rename(columns = {oldCol: oldCol.replace('<', '').replace('>', '').replace('_', '')}, inplace = True)

test1 = ratesTicksConcatenator(ratesDat, ticksDat, '5T')

print("test1")