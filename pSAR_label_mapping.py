import pandas as pd
from trading_strategies import parabolic_SAR
import os
import ta
import pytz

def psar_breakout_labelling(bt_data, orig_data):
    #Map 1 as profitable, 0 as unprofitable.

    df = bt_data[['time', 'high', 'low', 'close', 'signal', 'action', 'P/L']]

    pSAR = ta.trend.PSARIndicator(high = orig_data['high'], low = orig_data['low'], close = orig_data['close'], step = 0.02, max_step = 0.2).psar()
    pSAR_df = pd.DataFrame({"time": orig_data['time'], "pSAR": pSAR})

    df = df.merge(pSAR_df, on = 'time')
    df = df[['time', 'high', 'low', 'close', 'pSAR', 'signal', 'action', 'P/L']]
    df['Profitable Signal'] = [''] * len(df)

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

orig_dir = os.getcwd()
bt_folder = "290622-224947_EURUSD-2017-01-02_to_2022-06-05"
bt_file_dir = os.path.join(orig_dir, "backtests", bt_folder)
bt_filename = "bt_history" + bt_folder + ".csv"
bt_dat_dir = os.path.join(bt_file_dir, bt_filename)

bt_dat = pd.read_csv(bt_dat_dir, parse_dates = ['time'])

orig_dat_folder = os.path.join(orig_dir, "Datasets", "Successful Pulls")
orig_dat_filename = "EURUSD_H1__2017-01-02_to_2022-06-06.csv"
orig_dat_dir = os.path.join(orig_dat_folder, orig_dat_filename)

orig_dat = pd.read_csv(orig_dat_dir, parse_dates = ['time'])
orig_dat['time'] = orig_dat['time'].dt.tz_localize(tz = pytz.utc)

run = psar_breakout_labelling(bt_dat, orig_dat)

save_folder = r'C:\\Users\\Patrick\Documents\\UNI - USYD\\2022 - Capstone\\Strategy Research\\My working\\Breakout strategy\\pSAR Mapping'
save_filename = 'pSAR Mapping' + bt_folder + '.csv'
save_dir = os.path.join(save_folder, save_filename)

run.to_csv(save_dir, index = False)

print("test1")