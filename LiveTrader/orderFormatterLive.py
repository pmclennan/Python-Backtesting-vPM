import MetaTrader5 as mt5
import datetime

class orderFormatter:
    
    def __init__(self, inputSymbol, inputVolume, inputAction, inputPrice, inputTp, inputSl, \
         inputDeviation = 0.0002, inputComment = "", inputTypeTime = mt5.ORDER_TIME_GTC, inputTypeFilling = mt5.ORDER_FILLING_FOK):
        
        self.inputSymbol = inputSymbol
        self.inputVolume = inputVolume
        self.inputAction = inputAction
        self.inputPrice = inputPrice
        self.inputTp = inputTp
        self.inputSl = inputSl
        self.inputDeviation = inputDeviation
        self.inputComment = "Python Order" + inputComment + str(datetime.datetime.now())
        self.inputTypeTime = inputTypeTime
        self.inputTypeFilling = inputTypeFilling

        self.action = None
        self.request = None
        self.requestRetcode = None

    def formatRequest(self):       

        ##TODO - check logic on if open trades

        if self.inputAction[0:4] == "HOLD":
            request = "No Request"

        if self.inputAction == "LONG" or self.inputAction == "SHORT":
            self.tp = self.inputTp
            self.sl = self.inputSl
            if self.inputAction == "LONG":
                self.orderDirection = mt5.ORDER_TYPE_BUY
            elif self.inputAction == "SHORT":
                self.orderDirection = mt5.ORDER_TYPE_SELL
        
            request = {
                "action": self.action,
                "symbol": self.inputSymbol,
                "volume": self.inputVolume,
                "type": self.orderDirection,
                "price": self.price,
                "sl": self.sl,
                "tp": self.tp,
                "deviation": self.deviation,
                "comment": self.comment,
                "type_time": self.type_time,
                "type_filling": self.type_filling
                }
        
        self.request = request

        return self.request

    def sendRequest(self, request = None):
        if request == None:
            request = self.request
        
        if request != "No Request":
            
            result = mt5.order_send(request)
            self.requestRetcode = result.retcode

            if self.requestRetcode != mt5.TRADE_RETCODE_DONE:
                print(self.requestRetcode)