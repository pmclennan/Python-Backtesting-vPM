import os
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None
import time
from collections import deque
from signalHandler import signalHandler
from visualise import visualise
from trading_strategy import trading_strategy
from MT5DataPuller import MT5DataPuller
import MetaTrader5 as mt5
import datetime
import pytz
import os
from WeeklySummary import get_weekly_summary
from TradeSummary import get_trade_summary

#NB - need to import relevant strategies 
from trading_strategies import macd_stochastic_crossover
from trading_strategies import macd_crossover
from trading_strategies import three_rsp
from trading_strategies import parabolic_SAR
from trading_strategies import DonchianChannel_CCI
#from trading_strategies import DonchianChannel_CCI_SMA

## Initial setup

tz = pytz.utc #UTC Timezone
start_date = datetime.datetime(2021, 1, 1, tzinfo = tz) #Start Date - adjust as necessary
end_date = datetime.datetime(2022, 7, 18, tzinfo = tz) #End Date - adjust as necessary
data_filename = "AUDUSD_M15__2021-07-01_to_2022-07-19-P.csv" #Data File - adjust per the relevant file
currency = data_filename.split("_")[0] #Infer Currency from Data File
frequency_str = data_filename.split("_")[1] #Infer Frequency from Data File

#Set up Data Read - Datasets should be located in directory/Datasets (per the DataPull export)
data_dir = os.path.join(os.getcwd(), "Datasets", "Live Account")
data_file = os.path.join(data_dir, data_filename).replace('\\', '/')

#Read data and handle dates
full_data = pd.read_csv(data_file, parse_dates = ['time'])
full_data['time'] = full_data['time'].dt.tz_localize(tz = tz)

############# Hyperparameters #############
input_row_size = 60         # <----- Minimum number of inputs required by YOUR trading strategy
one_pip = 0.0001            # <----- Indicating the value of 1 pip, i.e. usually 0.0001 for all major fx except for JPY pairs (0.01)
stop_loss = -25*one_pip     # <----- (THIS WILL CHANGE!!, if the code recieves opposite signal than previously executed order then the position will be closed. 
take_profit = 50*one_pip    # <----- For example. If we holding a buy position and sell signal received (labeled as buyy_sell in signalHandler.py) then the position will be closed. 
guaranteed_sl = False       # Whether guaranteed stop loss/take profit is in place -> effects signalHandler.bandpl 
broker_cost = 2*one_pip     # Total cost flat for entering/exiting trade (ie captured once). Consider using higher value if guaranteed_sl is true - in reality guaranteed SL/TP are expensive
inputs = deque(maxlen=input_row_size)

#PSAR MAPPING
#stop_loss = -2000
#take_profit = 1000

############# BACKTESTING #############

## IMPORTANT - given the use of 'input rows', need to extend data at the front so the backtest starts accordingly. 
start_idx = full_data.index[full_data['time'] >= start_date][0]
start_idx_adj = (start_idx - input_row_size + 1) if (start_idx - input_row_size + 1) > 0 else 0
end_idx =  (full_data.index[full_data['time'] <= end_date][-1]) if (full_data['time'].iloc[-1] >= end_date) else full_data.index[-1]
data = full_data[start_idx_adj:end_idx]

#Instantiate Broker
broker = signalHandler(stop_loss, take_profit, guaranteed_sl, broker_cost, data, currency, start_date, end_date)

#Some Initialization
start_time = time.time() 
index = 0
signal = 0

#If no available bid/ask (need both), flag.
if 'ask' not in data or 'bid' not in data:
    print("Data does not contain both Bid & Ask - execution will be based on Close price instead.")

#Set up Iteration and print commencing statement
print("Commencing Backtest...")
for _,row in data.iterrows():

    # Loading the inputs array till the 
    # minimum number of inputs are reached
    inputs.append(row)
    
    if len(inputs) == input_row_size:

        strategy = DonchianChannel_CCI.DC_CCI(pd.DataFrame(inputs), CCI_window = 20, DC_periods = 20) #Change loaded strategy
        signal = strategy.run_DC_CCI() #And call respective strategy run function
        broker.store_signal(signal, index)

        # Current Price
        current_price = row['close']

        #Check if bid/ask available and just use current/close if not
        if 'ask' not in data or 'bid' not in data:
            bid_price = current_price
            ask_price = current_price
        else:        
            bid_price = row['bid']
            ask_price = row['ask']
        
        # Checks signal and executes
        if signal == 1:
            broker.buy(bid_price, ask_price, index)
        elif signal == -1:
            broker.sell(bid_price, ask_price, index)
        elif signal == 0:
            # Checking if stop loss or take profit is hit
            broker.checkStopConditions(bid_price, ask_price, index)
        else:
            print("Unknown Signal")
            break
        broker.store_executed_price(bid_price, ask_price, index)
     
    index += 1
    
    #Show progress
    if index % (round(0.01 * len(data), 0)) == 0:
        print("Backtest Progress:", round(100 * (index/len(data))), "%", end = "\r", flush = True)

#Save time and print
end_time = time.time()
print("\nTime consumed: {}s".format(round(end_time-start_time,2)))

#Set up for export folders
parent_dir = os.path.join(os.getcwd(), "backtests")
child_dir = datetime.datetime.now().strftime("%d%m%y-%H%M%S") + ("_{}_{}__{}_to_{}".format(currency, frequency_str, start_date.date(), end_date.date()))
subfolder = os.path.join(parent_dir, child_dir)
os.mkdir(subfolder)

save_time = datetime.datetime.now().strftime("%d%m%y-%H%M%S")

#History data save
history_data = broker.getHistory() # <----- Gets Data into a DATAFRAME 
history_data['position'] = history_data['position'].replace("", np.nan) #Remove empty period at the start (no position established yet)
history_data = history_data.dropna().reset_index(drop = True) #Drop this period
history_filename_str = "bt_history" + save_time + ("_{}_{}__{}_to_{}".format(currency, frequency_str, start_date.date(), end_date.date())) + ".csv" 
history_filename_path = os.path.join(subfolder, history_filename_str).replace('\\', '/')

#Summary data save
summary_data = broker.getSummary()
summary_data.insert(loc = 3, column = 'Frequency', value = frequency_str)
summary_filename_str = "bt_summary" + save_time + ("_{}_{}__{}_to_{}".format(currency, frequency_str, start_date.date(), end_date.date())) + ".csv" 
summary_filename_path = os.path.join(subfolder, summary_filename_str).replace('\\', '/')

#Weekly summary/breakdown data save
weekly_summary_data = get_weekly_summary(history_data, frequency_str)
weekly_summary_filename_str = "bt_weekly_summary" + save_time + ("_{}_{}__{}_to_{}".format(currency, frequency_str, start_date.date(), end_date.date())) + ".csv" 
weekly_summary_filename_path = os.path.join(subfolder, weekly_summary_filename_str).replace('\\', '/')

#Trade Summary
trade_summary_data = get_trade_summary(history_data)
trade_summary_filename_str = "bt_trade_summary" + save_time + ("_{}_{}__{}_to_{}".format(currency, frequency_str, start_date.date(), end_date.date())) + ".csv" 
trade_summary_filename_path = os.path.join(subfolder, trade_summary_filename_str).replace('\\', '/')

#Image file export preparation
image_filename_str = "bt_plot" + save_time + ("_{}_{}__{}_to_{}".format(currency, frequency_str, start_date.date(), end_date.date())) + ".png"
image_filename_path = os.path.join(subfolder, image_filename_str).replace('\\', '/')

# final_data has FIVE new coloumns
#   'signal'        : The computed signal at that timestep.
#   'action'        : The action the code implemented at that timestep.
#   'position'      : The position of the strategy at that timestep.
#   'P/L'           : The profit or loss at the time step, 0 when holding.
#   'Total profit'  : The total profit up to that timestep. 

visualiser = visualise(history_data)

##Exporting all - saves at very end (to ensure no bugs missed/partial saves)
history_data.to_csv(history_filename_path, index = False)
summary_data.to_csv(summary_filename_path, index = False)
weekly_summary_data.to_csv(weekly_summary_filename_path, index = False)
trade_summary_data.to_csv(trade_summary_filename_path, index = False)
visualiser.plotFig(image_filename_path, show_plot = False) #Save plot and not neccesarily show.

print("Backtest Process finalised: \n", summary_data)

############# Show Plot #############
#visualiser.plotFig(None, show_plot = True)