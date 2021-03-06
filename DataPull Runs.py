import pytz
import datetime
from MT5DataPuller import MT5DataPuller
import pandas as pd
import MetaTrader5 as mt5
import os

def PullData(currency, start_date, end_date, interval, freq_dict, batch_size = 0):
    
    start_date = start_date - datetime.timedelta(minutes = 14) #To make the range 'inclusive', i.e. from midnight of the start date.
    end_date = end_date + datetime.timedelta(days = 1, minutes = 14) #To make the range 'inclusive', i.e. til midnight of the end 
    interval_str = freq_dict[interval]
    
    data_obj = MT5DataPuller(currency, interval, start_date, end_date)
    data = data_obj.pull(batch_size)
    print("Data pulled - now exporting to csv")

    #Infer start/end date based on actual data pulled    
    start_date_str = data['time'].iloc[1].date()
    end_date_str = data['time'].iloc[-2].date()

    #Set up file name & export
    parent_dir = os.path.join(os.getcwd(), "Datasets")

    if mt5.account_info().server == 'ICMarkets-MT5-2':
        filename = ("{}_{}__{}_to_{}-P.csv".format(currency, interval_str, start_date_str, end_date_str))
    else:
        filename = ("{}_{}__{}_to_{}.csv".format(currency, interval_str, start_date_str, end_date_str))

    dataset_filename_path = os.path.join(parent_dir, filename).replace('\\', '/')

    data.to_csv(dataset_filename_path, index = False)

#Examples
freq_dict = {mt5.TIMEFRAME_M15: "M15", mt5.TIMEFRAME_M5: "M05", mt5.TIMEFRAME_D1: "D1", mt5.TIMEFRAME_H1: "H1"}
tz = pytz.utc
start_date = datetime.datetime(2021, 7, 1, tzinfo = tz) 
end_date = datetime.datetime(2022, 7, 18, tzinfo = tz) 

#interval = mt5.TIMEFRAME_D1
#currency = "USDJPY"

#PullData(currency, start_date, end_date, interval, freq_dict, 10)    

freq_dict = {mt5.TIMEFRAME_M15: "M15", mt5.TIMEFRAME_D1: "D1", mt5.TIMEFRAME_H1: "H1"}

currencies = ['AUDUSD', 'EURUSD', 'GBPUSD']

auth_dir = 'C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\MT5 Auth Details'
auth_filename = 'PM_ICMarkets_MT5_Live_Auth.txt'
auth_file = os.path.join(auth_dir, auth_filename)


with open(auth_file) as f:
    lines = f.readlines()

login = int(lines[0].split(": ")[1].split("\n")[0])
password = lines[1].split(": ")[1]

mt5.initialize()
mt5_auth = mt5.login(login = login, password = password, server = 'ICMarkets-MT5-2')
#mt5_auth = mt5.login(login = 50862405, password = 'T9hfhsA2', server = 'ICMarkets-Demo')
print("Auth Status:", mt5_auth)
print("Log:", mt5.last_error())
print("Account/Connection Info:", mt5.account_info()._asdict())

for currency in currencies:
    for key in freq_dict:
        print("Pulling", freq_dict[key], "Data for", currency, ".")
        PullData(currency, start_date, end_date, key, freq_dict, 10)