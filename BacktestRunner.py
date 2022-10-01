from logging import exception
from unittest import case
import pandas as pd
import pytz 
import os
import datetime
import sys
import time
from collections import deque

from signalHandler import signalHandler
from WeeklySummary import get_weekly_summary
from TradeSummary import get_trade_summary
from visualise import visualise

from trading_strategies import macd_stochastic_crossover, macd_crossover, three_rsp
from trading_strategies import parabolic_SAR, DonchianChannel_CCI, DonchianChannel_CCI_SMA

class BacktestRunner:

    def __init__(self, startDate, endDate, inputRowSize, strategyType, exportParentFolder, storeIndicators = 1):

        #Data Preparation attributes
        self.startDate = startDate
        self.endDate = endDate
        self.inputRowSize = inputRowSize
        self.data = None
        self.inputs = deque(maxlen=inputRowSize)

        #Report formatting        
        self.currency = None
        self.frequencyStr = None
        self.exportParentFolder = exportParentFolder

        #Backtesting functionality
        self.broker = signalHandler
        self.strategyType = strategyType
        self.storeIndicators = storeIndicators

    def readAndPrepData(self, dataDir, delimitter, timeCols):

        #Set up export filename details
        if "/" in dataDir:
            dataFilename = dataDir.split("/")[-1]
        elif "\\" in dataDir:
            dataFilename = dataDir.split("\\")[-1]
        self.currency = dataFilename.split("_")[0]
        self.frequencyStr = dataFilename.split("_")[1]

        #Read data
        fullData = pd.read_csv(dataDir, sep = delimitter, parse_dates = [timeCols])

        #Rename/standardize columns as well as localizing time
        for oldCol in fullData.columns:
            fullData.rename(columns = {oldCol: oldCol.replace('<', '').replace('>', '').replace('_', '').lower()}, inplace = True)
        
        fullData.rename(columns = {fullData.columns[0]: 'time'}, inplace = True)
        fullData['time'] = fullData['time'].dt.tz_localize(tz = pytz.utc)

        if 'bid' in fullData and 'ask' in fullData:
            fullData = fullData[['time', 'open', 'high', 'low', 'close', 'bid', 'ask']]    
        else:
            print("Data does not contain both Bid & Ask - execution will be based on Close price instead.")
            fullData = fullData[['time', 'open', 'high', 'low', 'close']]
        
        #Flag any errors with date inputs
        if self.startDate >= fullData['time'].iloc[-1] or self.startDate > self.endDate:
            print("Input start date: {} | Input end date: {}".format(self.startDate, self.endDate))
            print("Data start date : {} | Data end date:  {}".format(fullData['time'].iloc[0], fullData['time'].iloc[-1]))
            raise Exception ("Input time does not work with data dates - please review input dates or dataset")
        
        #Trim the data to the required window
        startIdx = fullData.index[fullData['time'] >= self.startDate][0]
        startIdxAdj = max((startIdx - self.inputRowSize + 1), 0)
        endIdx =  min((fullData.index[fullData['time'] <= self.endDate][-1] + 1), fullData.index[-1])
        self.data = fullData[startIdxAdj:endIdx].reset_index(drop = True)

        #Adjust the start/end date accordingly to line up with the actual data used - just for file naming purposes
        self.startDate = self.data['time'].iloc[self.inputRowSize]
        self.endDate = self.data['time'].iloc[-1]        

    def loadBroker(self, stopLoss, takeProfit, guaranteedSl, brokerCost):
        self.broker = self.broker(stopLoss, takeProfit, guaranteedSl, brokerCost, self.data, self.currency, self.startDate, self.endDate, self.storeIndicators)
    
    def runBacktest(self, runType = 1):
        '''
        Types:
        1 - standard indicator strategy. Instantiate with Data.
        2 - Deep Learning - requires model/scaler input
        3 - ZigZag - requires preliminary data upon instantiation before input into backtest. New data is loaded in "Run"
        '''

        startTime = time.time()
        index = 0
        signal = 0

        #Set up Iteration and print commencing statement
        print("Commencing Backtest")
        for _,row in self.data.iterrows():

            # Loading the inputs array till the 
            # minimum number of inputs are reached
            self.inputs.append(row)
            if len(self.inputs) == self.inputRowSize:

                if runType == 1:
                    #Vanilla indicator strategies
                    strategy = self.strategyType(pd.DataFrame(self.inputs))
                    signal, indicatorDf = strategy.run()
                    self.broker.storeSignalAndIndicators(signal, indicatorDf, index)          

                elif runType == 2:
                    print("TODO: Add DL Functionality")
                
                elif runType == 3:
                    if index >= 1261:
                        print("DebugPoint")
                    signal = self.strategyType.run(pd.DataFrame(self.inputs))
                    self.broker.storeSignalAndIndicators(signal, None, index)          

                currentPrice = row['close']

                if 'ask' not in self.data or 'bid' not in self.data:
                    bidPrice = currentPrice
                    askPrice = currentPrice

                else:
                    bidPrice = row['bid']
                    askPrice = row['ask']

                if signal == 1:
                    self.broker.buy(bidPrice, askPrice, index)
                elif signal == -1:
                    self.broker.sell(bidPrice, askPrice, index)
                elif signal == 0:
                    self.broker.checkStopConditions(bidPrice, askPrice, index)
                else:
                    print("Unknown Signal!")
                    break

                self.broker.store_executed_price(bidPrice, askPrice, index)

            index += 1

            #Show progress
            if index % (round(0.01 * len(self.data), 0)) == 0:
                print("Backtest Progress:", round(100 * (index/len(self.data))), "%", end = "\r", flush = True)

        endTime = time.time()
        print("\nTimeConsumed: {}".format(datetime.timedelta(seconds = endTime - startTime)))

    def runReports(self, savePlot = False, showPlot = False):
        
        #Folder setup
        childDir = datetime.datetime.now().strftime("%d%m%y-%H%M%S") + ("_{}_{}__{}_to_{}".format(
            self.currency, self.frequencyStr, self.startDate.date(), self.endDate.date()))
        subfolder = os.path.join(self.exportParentFolder, childDir)
        os.mkdir(subfolder)

        #History
        historyData = self.broker.getHistory()
        historyData = historyData.loc[self.inputRowSize-1:, :].reset_index(drop = True)
        historyFilename = "History.csv"
        historyDir = os.path.join(subfolder, historyFilename).replace('\\', '/')

        #Summary
        summaryData = self.broker.getSummary()
        summaryData.insert(loc = 3, column = 'Frequency', value = self.frequencyStr)
        summaryFilename = "Summary.csv"
        summaryDir = os.path.join(subfolder, summaryFilename).replace('\\', '/')

        #Weekly summary
        weeklySummaryData = get_weekly_summary(historyData, self.frequencyStr)
        weeklySummaryFilename = "Weekly_Summary.csv"
        weeklySummaryDir = os.path.join(subfolder, weeklySummaryFilename).replace('\\', '/')

        #Trade summary
        tradeSummaryData = get_trade_summary(historyData)
        tradeSummaryFilename = "Trade_Summary.csv"
        tradeSummaryDir = os.path.join(subfolder, tradeSummaryFilename).replace('\\', '/')

        #Exporting csvs
        historyData.to_csv(historyDir, index = False)
        summaryData.to_csv(summaryDir, index = False)
        weeklySummaryData.to_csv(weeklySummaryDir, index = False)
        tradeSummaryData.to_csv(tradeSummaryDir, index = False)
        
        #Plot
        if savePlot or showPlot:
            visualiser = visualise(historyData)        
            if savePlot:
                plotFilename = "Plot.png"
                plotDir = os.path.join(subfolder, plotFilename).replace('\\', '/')
                visualiser.plotFig(plotDir = plotDir, show_plot = showPlot) #Save plot and not neccesarily show.
            else:
                visualiser.plotFig(plotDir = None, show_plot = showPlot)

        print("Exports finalised\n", summaryData)