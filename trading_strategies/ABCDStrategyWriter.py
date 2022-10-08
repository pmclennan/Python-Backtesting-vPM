import pandas as pd
import sys
import os
import time
import datetime
import pytz

sys.path.append(os.getcwd())
from trading_strategies.ZigZagWriter import ZigZagWriter

class ABCDStrategy:
    def __init__(self, ZigZagData, threshMean = 1.61, threshVar = 0.05):

        self.ZigZagData = ZigZagData        
        self.threshMean = threshMean
        self.threshVar = threshVar

    def checkConditions(self, direction):
        #Note here that we look up to the second last point (hence the iloc[:-1])
        #As we have the condition based on bar next after the C point
                
        APoint = self.ZigZagData.iloc[:-1].loc[self.ZigZagData['ZigZag Value'] != 0].iloc[-3]
        BPoint = self.ZigZagData.iloc[:-1].loc[self.ZigZagData['ZigZag Value'] != 0].iloc[-2]
        CPoint = self.ZigZagData.iloc[:-1].loc[self.ZigZagData['ZigZag Value'] != 0].iloc[-1]

        Apx = APoint['ZigZag Value']
        Bpx = BPoint['ZigZag Value']
        Cpx = CPoint['ZigZag Value']    

        AB_BC_diff = (abs(Bpx - Apx))/(abs(Cpx - Bpx))

        signal = 0

        if (self.threshMean - self.threshVar <= AB_BC_diff <= self.threshMean + self.threshVar):

            if direction == 'Up' and (Apx < Cpx < Bpx) and Cpx < self.ZigZagData.loc[CPoint.name + 1, 'low']:

                signal = 1

            elif direction == 'Down' and (Apx > Cpx > Bpx) and Cpx > self.ZigZagData.loc[CPoint.name + 1, 'high']:
                
                signal = -1
            
        return signal

    def run(self):

        signal = 0

        #Check if the current bar is not a drawn Zig/Zag
        #Given the condition based on Bar after C.
        #This current bar/ZigZag point will get picked up on the next bar process anyway.

        if self.ZigZagData['ZigZag Type'].iloc[-1] != 'valley' or self.ZigZagData['ZigZag Type'].iloc[-1] != 'peak':
            
            #DownTrend
            if self.ZigZagData['ZigZag Type'].iloc[-2] == 'valley':
                signal = self.checkConditions('Up')
            #Uptrend
            elif self.ZigZagData['ZigZag Type'].iloc[-2] == 'peak':
                signal = self.checkConditions('Down')

        return signal