import pandas as pd
import datetime 
from MT5DataPuller import MT5DataPuller
import pytz
import MetaTrader5 as mt5
import os

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

#tz = pytz.utc
#currency = "AUDUSD"
#interval = mt5.TIMEFRAME_M15
#start_date = datetime.datetime(2022, 1, 1, tzinfo = tz)
#end_date = datetime.datetime(2022, 5, 1, tzinfo = tz)
frequency = pd.Timedelta(1, 'm')

#data_obj = MT5DataPuller(currency, interval, start_date, end_date)
#data_obj.input_summary()
#dataset = data_obj.pull()

dataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Symbols Method"
dataFile = "EURUSD.a_M1_201709040000_202109031210.csv"
dataDir = os.path.join(dataFolder, dataFile)
dataset = pd.read_csv(dataDir, sep = "\t", parse_dates = [["<DATE>", "<TIME>"]])
dataset.rename(columns = {"<DATE>_<TIME>": "time"}, inplace = True)

#dataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\CombinedDatasets"
#dataFile = "EURUSD_M1_14102021_02092022.csv"
#dataDir = os.path.join(dataFolder, dataFile)
#dataset = pd.read_csv(dataDir, parse_dates = ["DATETIME"])
#dataset.rename(columns = {"DATETIME": "time"}, inplace = True)

exportFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Missing Data Analysis"
exportFileName = dataFile.split(".csv")[0] + "_MissingDataAnalysis.csv"
exportDir = os.path.join(exportFolder, exportFileName)

intervalCheckDF = interval_checker_observations(dataset, frequency, False)
intervalCheckDF.to_csv(exportDir, index = False)