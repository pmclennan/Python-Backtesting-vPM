from locale import currency
import pandas as pd
import numpy as np
import datetime

class signalHandlerLive:

    #Use structure as backtest one, but clear out as using for live
    #Ie dont need the reports etc at this stage.

    def __init__(self,stopLossAmt, takeProfitAmt):
        self.stopLossAmt = stopLossAmt
        self.takeProfitAmt = takeProfitAmt
        self.currPL = 0

        self.currAction = "HOLD NO POSITION"
        self.expectedExecutionPrice = None
        self.expectedStopLossPrice = None
        self.expectedTakeProfitPrice = None

        self.prevTradedPosition = 0
        self.prevTradedPrice = None
        self.takeProfitPrice = None
        self.stopLossPrice = None
        self.positionId = None
        self.sizeOn = None

        self.currBidPrice = None
        self.currAskPrice = None

    def updatePostExecution(self, position, executedPrice, takeProfitPrice, stopLossPrice, positionId, sizeOn):
        #Here we update relevant details from MetaTrader 5 about current positions
        self.prevTradedPosition = position
        self.prevTradedPrice = executedPrice
        self.takeProfitPrice = takeProfitPrice
        self.stopLossPrice = stopLossPrice
        self.positionId = positionId
        self.sizeOn = sizeOn

    def refresh(self, bidPrice, askPrice):
        #Refresh bid/ask - used to outputting expected/targeted execution price
        self.currBidPrice = bidPrice
        self.currAskPrice = askPrice

    def refreshAndCheck(self, bidPrice, askPrice):
        #Not in use - see cmments under checkStpCondition
        self.refresh(bidPrice, askPrice)
        self.checkStopConditions(self.currBidPrice, self.currAskPrice)

    def handleSignal(self, signal):
        #Handles the simple (1, 0, -1) strategy result and calls other functions to do the rest of the work
        #That is, pick price target, set sl/tp etc
        #And returns a dictionary ready to be formatted for MT5

        if signal == 1:
            self.buy()            
        elif signal == -1:
            self.sell()
        elif signal == 0:            
            self.hold()

        signalInfo = {"Action": self.currAction, "Price": self.expectedExecutionPrice, \
            "TP": self.expectedTakeProfitPrice, "SL": self.expectedStopLossPrice, \
                "positionId": self.positionId, 'Volume': self.sizeOn}

        return signalInfo
        
    def buy(self):
        #Self explanatory - sets properties for buy order
        
        if self.prevTradedPosition == 0:
            self.currAction = "BUY"
            self.expectedExecutionPrice = self.currAskPrice
            self.expectedTakeProfitPrice = round(self.expectedExecutionPrice + self.takeProfitAmt, 5)
            self.expectedStopLossPrice = round(self.expectedExecutionPrice - self.stopLossAmt, 5)

        elif self.prevTradedPosition == -1:
            self.currAction = "CLOSE SHORT"    
            self.expectedExecutionPrice = self.currBidPrice

        elif self.prevTradedPosition == 1:
            self.hold()

        else: 
            print("Should not be here")
           
        return self.currAction

    def sell(self):
        #Similar to buy()

        if self.prevTradedPosition == 0:
            self.currAction = "SELL"
            self.expectedExecutionPrice = self.currAskPrice
            self.expectedTakeProfitPrice = round(self.expectedExecutionPrice - self.takeProfitAmt, 5)
            self.expectedStopLossPrice = round(self.expectedExecutionPrice + self.stopLossAmt, 5)

        elif self.prevTradedPosition == 1:
            self.currAction = "CLOSE LONG"  
            self.expectedExecutionPrice = self.currAskPrice        

        elif self.prevTradedPosition == -1:
            self.hold()

        #Refresh done just before processing signal
        #So sl/tp conditions already accounted for

        else: 
            print("Should not be here")
           
        return self.currAction

    def hold(self):
        #Similar to the above but useful as clears out expected prices

        if self.prevTradedPosition == -1:
            self.currAction = "HOLD SHORT"
        elif self.prevTradedPosition == 1:
            self.currAction = "HOLD LONG"
        elif self.prevTradedPosition == 0:
            self.currAction = "HOLD NO POSITION"

        self.expectedExecutionPrice = None
        self.expectedStopLossPrice = None
        self.expectedTakeProfitPrice = None

    def checkStopConditions(self):
        ##NEED TO CONFIRM IF THIS IS ACTUALLY REQUIRED
        ##Seems as if we can get away with auto sl/tp trigger in MT5

        if self.prevTradedPosition == 1:
            self.currPL = self.prevTradedPrice - self.currBidPrice

        if self.prevTradedPosition == -1:
            self.currPL = self.currAskPrice - self.prevTradedPrice
        
        if self.currPL <= self.stopLossAmt or self.currPL >= self.takeProfitAmt:
            self.closeTrade()

    def closeTrade(self):
        #Also not in use... as above
        
        if self.prevTradedPosition == 1:
            self.handleSignal(-1)
        
        elif self.prevTradedPosition == -1:
            self.handleSignal(1)