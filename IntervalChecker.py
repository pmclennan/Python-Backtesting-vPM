import pandas as pd
import datetime 
from MT5DataPuller import MT5DataPuller
import pytz
import MetaTrader5 as mt5

def interval_checker_observations(dataset, frequency, print_output = False):
    
  dataset['time'] = pd.to_datetime(dataset['time'])
  
  dataset['Time Difference'] = dataset['time'].diff(1)
  
  comparison_table = dataset.groupby('Time Difference', as_index = False)['time'].nunique()
  comparison_table = comparison_table.rename(columns = {'time' : '# Occurrences'})
  comparison_table['% Data'] = round(comparison_table['# Occurrences']/len(dataset[1:]) * 100, 6)

  comparison_table = pd.DataFrame(comparison_table.sort_values(by = '# Occurrences', ascending = False)).reset_index(drop = True)
  comparison_table['# Frequency Deviations'] = round(comparison_table['Time Difference']/frequency, 2)

  comparison_table = comparison_table[['Time Difference', '# Frequency Deviations', '# Occurrences', '% Data']]
  comparison_table = comparison_table.sort_values(by = 'Time Difference', ignore_index = True)

  if print_output == True:
    print(comparison_table)
  return (comparison_table)

tz = pytz.utc
currency = "AUDUSD"
interval = mt5.TIMEFRAME_M15
start_date = datetime.datetime(2022, 1, 1, tzinfo = tz)
end_date = datetime.datetime(2022, 5, 1, tzinfo = tz)
frequency = pd.Timedelta(15, 'm')

data_obj = MT5DataPuller(currency, interval, start_date, end_date)
data_obj.input_summary()
dataset = data_obj.pull()

intervalCheckDF = interval_checker_observations(dataset, frequency, True)
print(intervalCheckDF.sort_values(by = "% Data", ascending = False))