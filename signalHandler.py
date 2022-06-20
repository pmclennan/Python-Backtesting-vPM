from locale import currency
import pandas as pd
import numpy as np
import datetime

class signalHandler:

    def __init__(self,stop_loss, take_profit, broker_cost, data, currency, start_date, end_date):
        self.original_stop_loss = stop_loss
        self.original_take_profit = take_profit
        self.broker_cost = broker_cost
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.prev_traded_position = 0
        self.prev_traded_price = None

        self.total_profit = 0
        data['signal'] = ''
        data['action'] = ''
        data['position'] = ''
        data['P/L'] = ''
        data['Total profit'] = ''
        n = len(data)
        self.signal_list = [""]*n
        self.action = [""]*n
        self.position = [""]*n
        self.arr_PL = [""]*n 
        self.arr_total_profit = [""]*n 
        self.current_action = ""
        self.data = data
        
        self.trades_total = 0
        self.trades_won = 0
        self.trades_lost = 0
        self.trades_tied = 0
        self.currency = currency
        self.start_date = start_date
        self.end_date = end_date
        self.summary_df = pd.DataFrame()

    ############### Helpers ###############
    # Floors or ceils PL 
    def bandPL(self,PL):
        if PL > self.take_profit:
            PL = self.take_profit
        elif PL < self.stop_loss:
            PL = self.stop_loss
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
        self.data['P/L'] = self.arr_PL
        self.data['Total profit'] = self.arr_total_profit
        self.data['position'] = self.position
        return self.data

    # Summary of backtest results - called once completed
    def getSummary(self):
        self.summary_df['Start'] = [self.start_date.strftime("%Y-%m-%d %H:%S")]
        self.summary_df['End'] = self.end_date.strftime("%Y-%m-%d %H:%S")
        self.summary_df['Currency Pair'] = [self.currency]
        self.summary_df['Total Trades'] = [self.trades_total]
        self.summary_df['Total P/L (pips)'] = [self.arr_total_profit[-1]]
        self.summary_df['Trades Won (n)'] = [self.trades_won]
        self.summary_df['Trades Won (%)'] = [(self.trades_won/self.trades_total) * 100]
        self.summary_df['Trades Lost (n)'] = [self.trades_lost]
        self.summary_df['Trades Lost (%)'] = [(self.trades_lost/self.trades_total) * 100]
        self.summary_df['Trades Tied (n)'] = [self.trades_tied]
        self.summary_df['Trades Tied (%)'] = [(self.trades_tied/self.trades_total) * 100]
        return self.summary_df
    
    # Used to store signal for final summary df
    def store_signal(self, signal, index):
        self.signal_list[index] = signal

    ############### Actions ###############
    def buy(self, bid_price, ask_price, index):
        
        PL = 0 # <----- Default for if currently holding 
        if self.prev_traded_position == 0:
            self.current_action = "buy"
            self.prev_traded_position = 1
            self.prev_traded_price = ask_price #Executed at ask for a buy
            self.saveStats(PL,index)

        elif self.prev_traded_position == 1:
            # Reciving a stroger buy signal, 
            # Changing take profit to reflect that
            # PL = self.prev_traded_position*(current_price - self.prev_traded_price)
            # if PL > 0:
            #     self.take_profit *= 1.02 # <----- EDIT Based on how you wish to scale take_profit
            #     self.stop_loss *= 2
            self.checkStopConditions(bid_price, ask_price, index)

        elif self.prev_traded_position == -1:
            self.current_action = "close short"
            PL = (self.prev_traded_position*(ask_price - self.prev_traded_price)) - self.broker_cost #Executed at ask for a buy + flat spread
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
            self.saveStats(PL,index)

        elif self.prev_traded_position == -1:
            # Reciving a stroger sell signal, 
            # Changing stop loss to reflect that
            # self.stop_loss *= 0.5 # <----- EDIT Based on how you wish to scale stop_loss
            self.checkStopConditions(bid_price, ask_price ,index)
        
        elif self.prev_traded_position == 1:
            self.current_action = "close long"
            PL = (self.prev_traded_position*(bid_price - self.prev_traded_price)) - self.broker_cost #Executed at bid for a sell + flat spread
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