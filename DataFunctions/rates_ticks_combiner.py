import pandas as pd
import os 
import datetime

def rates_ticks_combiner(rates_dat, ticks_dat, floor_freq):

    ticks_dat['time'] = ticks_dat['time'].dt.floor(freq = floor_freq)

    combined_df = rates_dat.merge(ticks_dat, how = 'inner', on = 'time').groupby('time').first().reset_index()
    
    return combined_df

dat_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Symbols Method"
export_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Symbols Method"

rates_filename = "EURUSD_M15_201701020000_202208010000.csv"
ticks_filename = "EURUSD_202106291040_202208011137.csv"

rates_dir = os.path.join(dat_folder, rates_filename)
ticks_dir = os.path.join(dat_folder, ticks_filename)

rates_dat = pd.read_csv(rates_dir, sep = '\t')
ticks_dat = pd.read_csv(ticks_dir, sep = '\t')

for old_colname in rates_dat.columns.values:
    new_colname = old_colname.lower().replace('<', '').replace('>', '')
    rates_dat.rename(columns = {old_colname: new_colname}, inplace = True)

rates_dat['time'] = pd.to_datetime(rates_dat['date'] + ' ' + rates_dat['time'])
rates_dat.drop(['date'], axis = 1, inplace = True)

for old_colname in ticks_dat.columns.values:
    new_colname = old_colname.lower().replace('<', '').replace('>', '')
    ticks_dat.rename(columns = {old_colname: new_colname}, inplace = True)    

ticks_dat['time'] = pd.to_datetime(ticks_dat['date'] + ' ' + ticks_dat['time'])
ticks_dat.drop(columns = ['date', 'last', 'volume', 'flags'], axis = 1, inplace = True)

floor_freq_dict = {'M15': '15T', 'M5': '5T', 'M1': '1T'}

interval = rates_filename.split("_")[1]
currency = rates_filename.split("_")[0]

floor_freq = floor_freq_dict[interval]

combined_dat = rates_ticks_combiner(rates_dat, ticks_dat, floor_freq)

start_time = combined_dat['time'].iloc[0].date()
end_time = combined_dat['time'].iloc[-1].date()

export_filename = currency + "_" + interval + "__" + start_time.strftime('%Y%m%d') + "_" + end_time.strftime('%Y%m%d') + "_" + "combined" + ".csv"
export_dir = os.path.join(export_folder, export_filename)

combined_dat.to_csv(export_dir, index = False)