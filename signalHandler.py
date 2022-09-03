from locale import currency
import pandas as pd
import numpy as np
import datetime

class signalHandler:

    def __init__(self,stop_loss, take_profit, guaranteed_sl, broker_cost, data, currency, start_date, end_date):
        self.original_stop_loss = stop_loss
        self.original_take_profit = take_profit
        self.broker_cost = broker_cost
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.guaranteed_sl = guaranteed_sl

        self.prev_traded_position = 0
        self.prev_traded_price = None

        self.total_profit = 0
        data['signal'] = ''
        data['action'] = ''
        data['position'] = ''
        data['P/L'] = ''
        data['Total profit'] = ''
        data['Executed price'] = ''
        data['Take Profit'] = ''
        data['Stop Loss'] = ''
        n = len(data)
        self.signal_list = [""]*n
        self.action = [""]*n
        self.position = [""]*n
        self.arr_PL = [""]*n 
        self.arr_total_profit = [""]*n 
        self.executed_price = [""]*n
        self.stop_loss_px = [""]*n
        self.take_profit_px = [""]*n
        self.current_action = ""
        self.data = data
        self.indicatorDf = pd.DataFrame()
        
        self.trades_total = 0
        self.trades_won = 0
        self.trades_lost = 0
        self.trades_tied = 0
        self.currency = currency
        self.start_date = start_date
        self.end_date = end_date
        self.summary_df = pd.DataFrame(columns = self.data.columns)

    ############### Helpers ###############
    # Floors or ceils PL 
    def bandPL(self,PL):
        if self.guaranteed_sl:
            if PL > self.take_profit:
                PL = self.take_profit
            elif PL < self.stop_loss:
                PL = self.stop_loss
        else:
            PL = PL
        PL -= self.broker_cost
        return PL

    # Only called when a trade happens
    def closeTrade(self,PL):
        
        #Count in total trades
        self.trades_total += 1

        # Reseting Current position,action AND toal profit
        if self.prev_traded_position == -1:
            self.current_action = "close short"
        elif self.prev_traded_position == 1:
            self.current_action = "close long"        
        
        self.total_profit += PL

        self.prev_traded_position = 0
        self.prev_traded_price = None

        self.stop_loss = self.original_stop_loss
        self.take_profit = self.original_take_profit

        #Count if trade is succesful or not
        if PL > 0:
            self.trades_won += 1
        elif PL < 0:
            self.trades_lost += 1
        elif PL == 0:
            self.trades_tied += 1
        
    # Called every iteration to ADD stats into an array.
    # These arrays will be later copied into a DATAFRAME
    def saveStats(self, PL, index):
                
        if self.prev_traded_position == 1:
            self.action[index] = self.current_action
        
        elif self.prev_traded_position == -1:
            self.action[index] = self.current_action
        
        elif self.prev_traded_position == 0:
            self.action[index] = self.current_action
        
        self.arr_PL[index] = PL
        self.arr_total_profit[index] = self.total_profit
        self.position[index] = self.prev_traded_position

    # Transfers all the data into the DATAFRAME
    # The constructor is initialised with
    def getHistory(self):        
        self.data['signal'] = self.signal_list
        self.data['action'] = self.action
        self.data['position'] = self.position
        self.data['P/L'] = self.arr_PL
        self.data['Total profit'] = self.arr_total_profit
        self.data['Executed price'] = self.executed_price
        self.data['Stop Loss'] = self.stop_loss_px
        self.data['Take Profit'] = self.take_profit_px

        #Indicator DF
        insertIdx = self.data.columns.get_loc('signal')
        insertDF = self.indicatorDf.drop(columns = 'time')
        for i in range(len(insertDF.columns)):
            self.data.insert(loc = i + insertIdx, column = insertDF.columns.values[i], value = insertDF.iloc[:, i])

        return self.data

    # Summary of backtest results - called once completed
    def getSummary(self):
        self.summary_df['Start'] = [self.start_date.strftime("%Y-%m-%d %H:%S")]
        self.summary_df['End'] = self.end_date.strftime("%Y-%m-%d %H:%S")
        self.summary_df['Currency Pair'] = [self.currency]
        self.summary_df['Total Trades'] = [self.trades_total]
        self.summary_df['Total P/L'] = [self.arr_total_profit[-1]]
        self.summary_df['Total P/L (pips)'] = [self.arr_total_profit[-1] * 10000]
        self.summary_df['Trades Won (n)'] = [self.trades_won]
        self.summary_df['Trades Won (%)'] = [(self.trades_won/self.trades_total) * 100 if self.trades_total > 0 else 0]
        self.summary_df['Trades Lost (n)'] = [self.trades_lost]
        self.summary_df['Trades Lost (%)'] = [(self.trades_lost/self.trades_total) * 100 if self.trades_total > 0 else 0]
        self.summary_df['Trades Tied (n)'] = [self.trades_tied]
        self.summary_df['Trades Tied (%)'] = [(self.trades_tied/self.trades_total) * 100 if self.trades_total > 0 else 0]
        return self.summary_df
    
    # Used to store signal for final summary df
    def storeSignalAndIndicators(self, signal, indicatorDf, index):
        if self.indicatorDf.empty:
            self.indicatorDf = indicatorDf
        else:
            self.indicatorDf = self.indicatorDf.append(indicatorDf.iloc[-1], ignore_index=True)
        self.signal_list[index] = signal
        
    def store_executed_price(self, bid_price, ask_price, index):
        if self.current_action == "buy" or self.current_action == "close short":
            self.executed_price[index] = ask_price
        elif self.current_action == "short" or self.current_action == "close long":
            self.executed_price[index] = bid_price

    ############### Actions ###############
    def buy(self, bid_price, ask_price, index):
        
        PL = 0 # <----- Default for if currently holding 
        if self.prev_traded_position == 0:
            self.current_action = "buy"
            self.prev_traded_position = 1
            self.prev_traded_price = ask_price #Executed at ask for a buy
            self.stop_loss_px[index] = self.prev_traded_price + self.stop_loss
            self.take_profit_px[index] = self.prev_traded_price + self.take_profit
            self.saveStats(PL,index)

        elif self.prev_traded_position == 1:
            # Reciving a stroger buy signal
            self.checkStopConditions(bid_price, ask_price, index)
            #Recalibrate SL/TP if still short after checking stop - Check Matloob
            if self.current_action == "buy":
                self.take_profit += self.original_take_profit
                self.stop_loss += self.original_take_profit
                self.stop_loss_px[index] = self.prev_traded_price + self.stop_loss
                self.take_profit_px[index] = self.prev_traded_price + self.take_profit

        elif self.prev_traded_position == -1:
            self.current_action = "close short"
            PL = (self.prev_traded_position*(ask_price - self.prev_traded_price)) #Executed at ask for a buy 
            PL = self.bandPL(PL)
            self.closeTrade(PL)
            self.saveStats(PL,index)

        else: 
            print("Should not be here")
           
        return self.total_profit

    def sell(self, bid_price, ask_price, index):
        
        PL = 0 # <----- Default for if currently holding
        if self.prev_traded_position == 0:
            self.current_action = "short"
            self.prev_traded_position = -1
            self.prev_traded_price = bid_price #Executed at bid for a sell
            self.stop_loss_px[index] = self.prev_traded_price - self.stop_loss
            self.take_profit_px[index] = self.prev_traded_price - self.take_profit
            self.saveStats(PL,index)

        elif self.prev_traded_position == -1:
            # Reciving a stroger sell signal, 
            self.checkStopConditions(bid_price, ask_price ,index)
            #Likewise for buy, update sl/tp
            # if self.current_action == "short":
            #     self.take_profit += self.original_take_profit
            #     self.stop_loss += self.original_take_profit
            #     self.stop_loss_px[index] = self.prev_traded_price + self.stop_loss
            #     self.take_profit_px[index] = self.prev_traded_price + self.take_profit
        
        elif self.prev_traded_position == 1:
            self.current_action = "close long"
            PL = (self.prev_traded_position*(bid_price - self.prev_traded_price)) #Executed at bid for a sell + flat spread
            PL = self.bandPL(PL)
            self.closeTrade(PL)
            self.saveStats(PL,index)
        else: 
            print("Should not be here")

        return self.total_profit
    
    # Called from MAIN code when the HOLD signal is received
    # ALSO called by the BUY AND SELL functions when
    # the broker sequentially receives the same signal.
    def checkStopConditions(self, bid_price, ask_price, index):
        PL = 0
        self.current_action = "hold"
        
        if self.prev_traded_position == -1:

            PL = (self.prev_traded_position*(ask_price - self.prev_traded_price)) #MtM PL when short based off ask price (as if we were to buy to close the short)
            
            if PL > self.take_profit:
                PL = self.bandPL(PL) 
                self.closeTrade(PL)
            elif PL < self.stop_loss:
                PL = self.bandPL(PL)
                self.closeTrade(PL)

        elif self.prev_traded_position == 1:

            PL = (self.prev_traded_position*(bid_price - self.prev_traded_price)) #MtM PL when long based off bid price (as if we were to sell to close the long)
            
            if PL > self.take_profit:
                PL = self.bandPL(PL) 
                self.closeTrade(PL)
            elif PL < self.stop_loss:
                PL = self.bandPL(PL)
                self.closeTrade(PL)         

        self.saveStats(PL,index)
        return self.total_profit