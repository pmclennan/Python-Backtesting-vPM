import pandas as pd
import datetime
import os
import numpy as np

def ratesTicksConcatenator(ratesDat, ticksDat, floorFreq, ticksCleanFlag = 1, replacementSpread = 3):
   
    #First, find the starting times of both files and use the latest.
    timeCol = ratesDat.columns[0]

    firstRatesTime = ratesDat.iloc[0, 0]
    firstTicksTime = ticksDat.iloc[0, 0]

    if firstRatesTime > firstTicksTime:
        ticksDat = ticksDat[ticksDat[timeCol] >= firstRatesTime].reset_index(drop = True)
    else:
        ratesDat = ratesDat[ratesDat[timeCol] >= firstTicksTime].reset_index(drop = True)

    #Similar for last time in each

    lastRatesTime = ratesDat.iloc[-1, 0]
    lastTicksTime = ticksDat.iloc[-1, 0]

    if lastRatesTime > lastTicksTime:
        ratesDat = ratesDat[ratesDat[timeCol] <= lastTicksTime].reset_index(drop = True)
    else:
        ticksDat = ticksDat[ticksDat[timeCol] <= lastRatesTime].reset_index(drop = True)
        
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
    ticksDat.loc[:, timeCol] = ticksDat.loc[:,timeCol].dt.floor(freq = floorFreq)

    #Merge
    concatDF = ratesDat.merge(ticksDat, how = 'left', on = timeCol).groupby(timeCol).first().reset_index()

    #Replace values    
    missingIDX = concatDF[concatDF['BID'].isnull() | concatDF['ASK'].isnull()].index.values

    if ticksCleanFlag == 1:
        #Average spread of 5 behind / 5 forward rounded to nearest pip
        #NB if unavailable for forward 5 (near end of Data), shift this range back as appropriate (and vice versa if at the start)
            # EG if 4 indexes from the end, use 7 behind / 3 forward rather than 5 / 5
        for idx in missingIDX:
            if len(concatDF) - idx <= 5:
                shiftFactor = (len(concatDF) - idx) - 6
            elif idx <= 5:                
                shiftFactor = 1 - idx
            else:
                shiftFactor = 0

            #idxGroup = list(np.arange(idx-5+shiftFactor, idx)) + list(np.arange(idx+1, idx+6+shiftFactor))
            #Update to only capture rolling window where bid/ask is already present from MT5.
            idxGroup = list(concatDF[~concatDF['BID'].isnull() & ~concatDF['ASK'].isnull()].iloc[idx-5+shiftFactor:idx].index.values) \
                + list(concatDF[~concatDF['BID'].isnull() & ~concatDF['ASK'].isnull()].iloc[idx:idx+6+shiftFactor-1].index.values)

            avgBidSpread = round(np.mean(concatDF.loc[idxGroup,'CLOSE'] - concatDF.loc[idxGroup, 'BID']), 5)
            avgAskSpread = round(np.mean(concatDF.loc[idxGroup, 'ASK'] - concatDF.loc[idxGroup, 'CLOSE']), 5)            
            concatDF.loc[idx, 'BID'] = concatDF.loc[idx, 'CLOSE'] - avgBidSpread
            concatDF.loc[idx, 'ASK'] = concatDF.loc[idx, 'CLOSE'] + avgAskSpread

    elif ticksCleanFlag == 2:
        #Flat spread
        for idx in missingIDX:
            concatDF.loc[idx, 'BID'] = concatDF.loc[idx, 'CLOSE'] - (replacementSpread/10000)
            concatDF.loc[idx, 'ASK'] = concatDF.loc[idx, 'CLOSE'] + (replacementSpread/10000)

    #Flag replaced values
    replacedBidAskList = [''] * len(concatDF)
    for idx in missingIDX:
        replacedBidAskList[idx] = 'Replaced'

    concatDF['ReplacedBidAsk'] = replacedBidAskList

    concatDF = concatDF[[timeCol, 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'BID', 'ASK', 'ReplacedBidAsk']]
    #concatDF = concatDF[[timeCol, 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'BID', 'ASK']]

    return concatDF

ratesDatFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets"
ticksDatFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets\\TicksDat"

ticksFileName = "EURUSD.a_BidAskTicks_202110141713_202209022356.csv"
ratesFileName = "EURUSD.a_M1_202110130000_202209022356.csv"

ratesDir = os.path.join(ratesDatFolder, ratesFileName)
ticksDir = os.path.join(ticksDatFolder, ticksFileName)

ratesDat = pd.read_csv(ratesDir, sep = "\t", parse_dates = [[0, 1]])
ticksDat = pd.read_csv(ticksDir, sep = "\t", parse_dates = [[0, 1]])

for oldCol in ratesDat.columns:
    ratesDat.rename(columns = {oldCol: oldCol.replace('<', '').replace('>', '').replace('_', '')}, inplace = True)

for oldCol in ticksDat.columns:
    ticksDat.rename(columns = {oldCol: oldCol.replace('<', '').replace('>', '').replace('_', '')}, inplace = True)

EURUSDM1_dat = ratesTicksConcatenator(ratesDat, ticksDat, '1T')

exportFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\CombinedDatasets"

startDate = EURUSDM1_dat.iloc[0, 0]
endDate = EURUSDM1_dat.iloc[-1, 0]

exportName = "EURUSD_M1_{}_{}.csv".format(startDate.strftime("%d%m%Y"), endDate.strftime("%d%m%Y")) 
exportDir = os.path.join(exportFolder, exportName)

EURUSDM1_dat.to_csv(exportDir, index = False)