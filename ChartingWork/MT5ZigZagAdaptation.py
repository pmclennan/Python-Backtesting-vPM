import pandas as pd
import datetime
import MetaTrader5 as mt5
import pytz
import os

'''
ZigZag Indicator calculation process following the method that the MetaTrader 5 indicator uses.
For more context, please review the MQL5 code behind the ZigZag indicator.

An important point to note is that MT5 seems to look back to the start of the previous year to beging calculating the ZigZags.
So this functionality does that first, then starts the process of calculating each bar in the input range individually - shown in .run().

This has been set up as a class to keep a 'global' i index which MT5 seems to keep as well as other indexing variables (shift, back etc)
that are carried across different parts of the process.
'''

class ZigZagIndicator:
    def __init__(self, InpDepth = 12, InpDeviation = 5, InpBackstep = 3):
        
        self.i = 0
        self.prev_calculated = 0
        self.prelimData = pd.DataFrame()
        self.testData = pd.DataFrame()
        self.testDataFinal = pd.DataFrame()
        self.fulLData = pd.DataFrame()
        self.currData = pd.DataFrame()
        self.rates_total = 0

        self.PointSize = 0.00001
        
        self.InpDepth = InpDepth
        self.InpDeviation = InpDeviation
        self.InpBackstep = InpBackstep

        self.Extremum = 0
        self.Peak = 1
        self.Bottom = -1
        self.ExtRecalc = 3
        self.extreme_counter = 0
        
        self.shift = None
        self.back = None
        self.last_high_pos = None
        self.last_low_pos = None
        self.val = None
        self.res = None
        self.extreme_search = None
        self.curlow = None
        self.curhigh = None
        self.last_high = None
        self.last_low = None

        self.high = None
        self.low = None

        self.login = None
        self.password = None
        self.password = None
        
    def setMT5Auth(self, login, password, server):
        self.login = login
        self.password = password
        self.server = server
        
        mt5.initialize()
        auth = mt5.login(login = self.login, password = self.password, server = self.server)
        print('\n-----MT5 Connection Status------')
        print("Auth Status:", auth)
        print("Log:", mt5.last_error())
        print("Account/Connection Info:", mt5.account_info()._asdict())

    def pullData(self, currency, frequency, startDate, endDate):
        #Seems that MT5 uses start of previous year to base the ZigZag
       
        if endDate.hour == 0 and endDate.minute == 0:
            endDate = endDate - datetime.timedelta(minutes = 1)
        prelimStartDateYear = startDate.year - 1
        prelimStartDate = datetime.datetime(year = prelimStartDateYear, month = 1, day = 1, tzinfo = pytz.utc)
        prelimEndDate = startDate - datetime.timedelta(minutes =  1)

        self.prelimData = mt5.copy_rates_range(currency, frequency, prelimStartDate, prelimEndDate)
        self.prelimData = pd.DataFrame(self.prelimData)
        self.prelimData['time'] = pd.to_datetime(self.prelimData['time'], unit = 's', utc = True)

        self.testData = mt5.copy_rates_range(currency, frequency, startDate, endDate)
        self.testData = pd.DataFrame(self.testData)
        self.testData['time'] = pd.to_datetime(self.testData['time'], unit = 's', utc = True)

        self.fullData = mt5.copy_rates_range(currency, frequency, prelimStartDate, endDate)
        self.fullData = pd.DataFrame(self.fullData)
        self.fullData['time'] = pd.to_datetime(self.fullData['time'], unit = 's', utc = True)

        self.currData = self.prelimData
        
    def appendDataByOne(self):
        appendIdx = len(self.currData) - len(self.prelimData)
        self.currData = self.currData.append(self.testData.loc[appendIdx, :], ignore_index = True)
        self.ZigZagBuffer.append(0)
        self.HighMapBuffer.append(0)
        self.LowMapBuffer.append(0)

    def initialization(self):
        
        self.rates_total = len(self.currData)
        self.high = self.currData['high']
        self.low = self.currData['low']      

        self.i = 0
        self.start = 0
        self.extreme_counter = 0
        self.extreme_search = self.Extremum
        self.shift = 0
        self.back = 0
        self.last_high_pos = 0
        self.last_low_pos = 0
        self.val = 0
        self.res = 0
        self.curlow = 0
        self.curhigh = 0
        self.last_high = 0
        self.last_low = 0
                
        if self.prev_calculated == 0:
            self.ZigZagBuffer = [0] * len(self.currData)
            self.HighMapBuffer = [0] * len(self.currData)
            self.LowMapBuffer = [0] * len(self.currData)
            self.start = self.InpDepth

    def ZigZagPrevCalc(self):
        #Searching for the third extremum from the last uncompleted bar
        
        if self.prev_calculated > 0:
            self.i = self.rates_total - 1

            while (self.extreme_counter < self.ExtRecalc) and (self.i > self.rates_total - 100):
                self.res = self.ZigZagBuffer[self.i]
                if self.res != 0:
                    self.extreme_counter += 1
                self.i -= 1

            self.i += 1
            self.start = self.i

            #What type of exremum we search for
            if self.LowMapBuffer[self.i] != 0:
                self.curlow = self.LowMapBuffer[self.i]
                self.extreme_search = self.Peak

            else:
                self.curhigh = self.HighMapBuffer[self.i]
                self.extreme_search = self.Bottom

            #Clear Indicator Values
            self.i = self.start + 1
            while self.i < self.rates_total:
                self.ZigZagBuffer[self.i] = 0
                self.LowMapBuffer[self.i] = 0
                self.HighMapBuffer[self.i] = 0

                self.i += 1

    def searchExtremes(self):
        #Searching for high and low extremes

        self.shift = self.start        
        while self.shift < self.rates_total:
            
            #Low
            self.val = self.low[self.Lowest(self.low, self.InpDepth, self.shift)]
            if self.val == self.last_low:
                self.val = 0            
            else:
                self.last_low = self.val
                if (self.low[self.shift] - self.val) > self.InpDeviation * self.PointSize:
                    self.val = 0
                else:
                    self.back = 1
                    while self.back <= self.InpBackstep:
                        self.res = self.LowMapBuffer[self.shift - self.back]
                        if (self.res != 0) and (self.res > self.val):
                            self.LowMapBuffer[self.shift - self.back] = 0

                        self.back += 1

            if self.low[self.shift] == self.val:
                self.LowMapBuffer[self.shift] = self.val
            else:
                self.LowMapBuffer[self.shift] = 0

            #High
            self.val = self.high[self.Highest(self.high, self.InpDepth, self.shift)]
            if self.val == self.last_high:
                self.val = 0
            else:
                self.last_high = self.val
                if (self.val - self.high[self.shift]) > self.InpDeviation * self.PointSize:
                    self.val = 0
                else:
                    self.back = 1
                    while self.back <= self.InpBackstep:
                        self.res = self.HighMapBuffer[self.shift - self.back]
                        if (self.res != 0) and (self.res < self.val):
                            self.HighMapBuffer[self.shift - self.back] = 0

                        self.back += 1

            if self.high[self.shift] == self.val:
                self.HighMapBuffer[self.shift] = self.val
            else:
                self.HighMapBuffer[self.shift] = 0

            self.shift += 1

    def setLastValues(self):
        if self.extreme_search == 0:
            self.last_low = 0
            self.last_high = 0
        else:
            self.last_low = self.curlow
            self.last_high = self.curhigh
    
    def finalSelection(self):
        self.shift = self.start
        while self.shift < self.rates_total:
            self.res = 0
            if self.extreme_search == self.Extremum:
                if self.last_low == 0 and self.last_high == 0:
                    if self.HighMapBuffer[self.shift] != 0:
                        self.last_high = self.high[self.shift]
                        self.last_high_pos = self.shift
                        self.extreme_search = self.Bottom
                        self.ZigZagBuffer[self.shift] = self.last_high
                        self.res = 1

                    if self.LowMapBuffer[self.shift] != 0:
                        self.last_low = self.low[self.shift]
                        self.last_low_pos = self.shift
                        self.extreme_search = self.Peak
                        self.ZigZagBuffer[self.shift] = self.last_low
                        self.res = 1

            elif self.extreme_search == self.Peak:
                if (self.LowMapBuffer[self.shift] != 0) and (self.LowMapBuffer[self.shift] < self.last_low) and (self.HighMapBuffer[self.shift] == 0):
                    self.ZigZagBuffer[self.last_low_pos] = 0
                    self.last_low_pos = self.shift
                    self.last_low = self.LowMapBuffer[self.shift]
                    self.ZigZagBuffer[self.shift] = self.last_low
                    self.res = 1
                    
                if (self.HighMapBuffer[self.shift] != 0) and (self.LowMapBuffer[self.shift] == 0):
                    self.last_high = self.HighMapBuffer[self.shift]
                    self.last_high_pos = self.shift
                    self.ZigZagBuffer[self.shift] = self.last_high
                    self.extreme_search = self.Bottom
                    self.res = 1
                                   
            elif self.extreme_search == self.Bottom:
                if (self.HighMapBuffer[self.shift] != 0) and (self.HighMapBuffer[self.shift] > self.last_high) and (self.LowMapBuffer[self.shift] == 0):
                    self.ZigZagBuffer[self.last_high_pos] = 0
                    self.last_high_pos = self.shift
                    self.last_high = self.HighMapBuffer[self.shift]
                    self.ZigZagBuffer[self.shift] = self.last_high
                if (self.LowMapBuffer[self.shift] != 0 and self.HighMapBuffer[self.shift] == 0):
                    self.last_low = self.LowMapBuffer[self.shift]
                    self.last_low_pos = self.shift
                    self.ZigZagBuffer[self.shift] = self.last_low
                    self.extreme_search = self.Peak
                
            self.shift += 1

        self.prev_calculated = self.rates_total

    def Lowest(self, array, depth, start):
        
        if start < 0:
            return 0

        minval = array[start]
        index = start

        #Start Searching
        i = start - 1
        while (i > start - depth) and (i >= 0):
            if array[i] < minval:
                index = i
                minval = array[i]
                
            i -= 1

        #Return index of lowest bar
        return index

    def Highest(self, array, depth, start):
        if start < 0:
            return 0

        maxval = array[start]
        index = start

        #Start searching
        i = start - 1
        while (i > start - depth) and (i >= 0):
            if array[i] > maxval:
                index = i
                maxval = array[i]

            i -= 1

        #Return index of highest bar
        return index


    def finaliseResults(self, fullFlag):

        self.currData['ZigZag Value'] = self.ZigZagBuffer

        self.currData['ZigZag Type'] = [''] * len(self.currData)
        self.currData['HighMapBuffer'] = self.HighMapBuffer
        self.currData['LowMapBuffer'] = self.LowMapBuffer

        self.currData.loc[self.currData['ZigZag Value'] == self.currData['high'], 'ZigZag Type'] = 'peak'
        self.currData.loc[self.currData['ZigZag Value'] == self.currData['low'], 'ZigZag Type'] = 'valley'

        self.testDataFinal = self.currData.loc[(self.currData['time'] >= startDate) & (self.currData['time'] <= endDate)].reset_index(drop = True)
        
        if not fullFlag:
            return self.testDataFinal
        else:
            return self.currData 

    def run(self, currency, timeframe, startDate, endDate, fullFlag = 0):

        self.pullData(currency, timeframe, startDate, endDate)

        for i in range(len(self.testData)+1):
            if i > 0:
                self.appendDataByOne()
            self.initialization()
            self.ZigZagPrevCalc()
            self.searchExtremes()
            self.setLastValues()
            self.finalSelection()

        result = self.finaliseResults(fullFlag)

        return result

startDate = datetime.datetime(2018, 1, 1, tzinfo = pytz.utc)
endDate = datetime.datetime(2022, 9, 24, tzinfo = pytz.utc)



o = ZigZagIndicator()
o.setMT5Auth(7075929, 'ULP3jJgr', 'ICMarkets-MT5-2')
ZigZagDat = o.run('EURUSD.a', mt5.TIMEFRAME_M1, startDate, endDate, 1)

exportFolder = os.path.join(os.getcwd(), 'ChartingWork')
exportFileName = "EURUSDM1_ZigZag_" + str(startDate.date()) + "_" + str(endDate.date()) + ".csv"
exportDir = os.path.join(exportFolder, exportFileName)
ZigZagDat.to_csv(exportDir, index = False)

print("DebugPoint")