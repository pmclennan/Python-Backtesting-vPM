import MetaTrader5 as mt5
import datetime

class orderFormatter:
    
    def __init__(self, inputSymbol, inputVolume, inputAction, inputPrice, inputTp, inputSl, positionId, \
         inputDeviation = 20, inputComment = "", inputTypeTime = mt5.ORDER_TIME_GTC, inputTypeFilling = mt5.ORDER_FILLING_IOC):
        
        self.inputSymbol = inputSymbol
        self.inputVolume = inputVolume
        self.inputAction = inputAction
        self.inputPrice = inputPrice
        self.inputTp = inputTp
        self.inputSl = inputSl
        self.positionId = positionId
        self.inputDeviation = inputDeviation
        self.inputComment = "Python " + self.inputAction + " Order"
        self.inputTypeTime = inputTypeTime
        self.inputTypeFilling = inputTypeFilling

        self.action = None
        self.request = None
        self.lastRetcode = None

    def formatRequest(self):       

        ##TODO - check logic on if open trades

        if self.inputAction[0:4] == "HOLD":
            request = "No Request"

        elif self.inputAction[0:5] == "CLOSE":
            self.action = mt5.TRADE_ACTION_DEAL
            if self.inputAction == "CLOSE LONG":
                self.orderDirection = mt5.ORDER_TYPE_SELL
            elif self.inputAction == "CLOSE SHORT":
                self.orderDirection = mt5.ORDER_TYPE_BUY

            request={
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.inputSymbol,
                "volume": self.inputVolume,
                "type": self.orderDirection,
                "position": self.positionId,
                "price": self.inputPrice,
                "deviation": self.inputDeviation,
                "comment": self.inputComment,
                "type_time": self.inputTypeTime,
                "type_filling": self.inputTypeFilling
            }

        elif self.inputAction == "BUY" or self.inputAction == "SELL":
            self.tp = self.inputTp
            self.sl = self.inputSl
            if self.inputAction == "BUY":
                self.orderDirection = mt5.ORDER_TYPE_BUY
            elif self.inputAction == "SELL":
                self.orderDirection = mt5.ORDER_TYPE_SELL
        
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.inputSymbol,
                "volume": self.inputVolume,
                "type": self.orderDirection,
                "price": self.inputPrice,
                "sl": self.sl,
                "tp": self.tp,
                "deviation": self.inputDeviation,
                "comment": self.inputComment,
                "type_time": self.inputTypeTime,
                "type_filling": self.inputTypeFilling
                }
        
        else:
            print("Unable to format request")
        
        self.request = request

        return self.request

    def sendRequest(self, request = None):
        if request == None:
            request = self.request
        
        if request == "No Request":
            self.lastResult = 'No Request Sent'
            
        else:
            self.lastResult = mt5.order_send(request)
            self.lastRetcode = self.lastResult.retcode
        
        return self.lastResult