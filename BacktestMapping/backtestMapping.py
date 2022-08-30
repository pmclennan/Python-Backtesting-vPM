import pandas as pd
import os
import ta
import pytz

def backtestMapping(bt_data, orig_data):
    #Map 1 as profitable long, -1 as profitable short, 0 as no trade.
    #So if a long trade is unprofitable, map it as a profitable short and vice versa.

    df = bt_data[['time', 'open', 'high', 'low', 'close', 'signal', 'action', 'P/L']]

    print("Calculating pSAR")
    pSAR = ta.trend.PSARIndicator(high = orig_data['high'], low = orig_data['low'], close = orig_data['close'], step = 0.02, max_step = 0.2).psar()
    pSAR_df = pd.DataFrame({"time": orig_data['time'], "pSAR": pSAR})

    print("Setting up DataFrame")
    df = df.merge(pSAR_df, on = 'time')
    df = df[['time', 'open', 'high', 'low', 'close', 'pSAR', 'signal', 'action', 'P/L']]
    df['Profitable Signal'] = [''] * len(df)

    print("Mapping")
    for i in range(0, len(df)):
        if df['action'].iloc[i] == 'short':
            if not df['P/L'].loc[(df['action'] == 'close short') & (df.index >= i)].empty:
                trade_PL = df['P/L'].loc[(df['action'] == 'close short') & (df.index >= i)].iloc[0]
        elif df['action'].iloc[i] == 'buy':
            if not df['P/L'].loc[(df['action'] == 'close long') & (df.index >= i)].empty:
                trade_PL = df['P/L'].loc[(df['action'] == 'close long') & (df.index >= i)].iloc[0]
        
        if df['action'].iloc[i] == 'short' or df['action'].iloc[i] == 'buy':
            if trade_PL > 0:
                df['Profitable Signal'].iloc[i] = 1
            elif trade_PL <= 0:
                df['Profitable Signal'].iloc[i] = 0
    return df

#Instructions
#Rename bt_foldername to the relevant backtest with pSAR then also rename orig_dat_filename to the csv inside it
#And also change export_folder to where you want the output saved

orig_dir = os.getcwd()
bt_foldername = "100722-131317_EURUSD_H1__2017-01-02_to_2022-06-05"
bt_file_dir = os.path.join(orig_dir, "backtests", bt_foldername)
bt_filename = "bt_history" + bt_foldername + ".csv"
bt_dat_dir = os.path.join(bt_file_dir, bt_filename)

bt_dat = pd.read_csv(bt_dat_dir, parse_dates = ['time'])

orig_dat_folder = os.path.join(orig_dir, "Datasets", "Successful Pulls")

for orig_dat_file in os.listdir(orig_dat_folder):
    if bt_foldername.split("_")[1:3] == orig_dat_file.split("_")[0:2]:
        orig_dat_filename = orig_dat_file

orig_dat_dir = os.path.join(orig_dat_folder, orig_dat_filename)

orig_dat = pd.read_csv(orig_dat_dir, parse_dates = ['time'])
orig_dat['time'] = orig_dat['time'].dt.tz_localize(tz = pytz.utc)

run = psar_breakout_labelling(bt_dat, orig_dat)

export_folder = r'C:\\Users\\Patrick\Documents\\UNI - USYD\\2022 - Capstone\\Strategy Research\\My working\\Breakout strategy\\pSAR Mapping'
export_filename = 'pSAR Mapping' + bt_foldername + '.csv'
export_dir = os.path.join(export_folder, export_filename)

run.to_csv(export_dir, index = False)
