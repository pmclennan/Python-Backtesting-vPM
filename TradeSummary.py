import os
import pandas as pd
import datetime

def get_trade_summary(data):
    data = data[['time', 'close', 'signal', 'action', 'Executed price', 'position', 'Total profit']]
    trades_df = pd.DataFrame(columns = data.columns)
    #Add Executed Trade Price to history 
    trades_summary_df = pd.DataFrame({"Trade Type": [], "Trade Open Time": [], "Trade Open Price": [], \
        "Trade Close Time": [], "Trade Close Price": [], "Trade P/L": []})

    for i in range(0, len(data)):
        if data['action'].iloc[i] != 'hold':
            trades_df = trades_df.append(data.iloc[i], ignore_index = True)
    
    for j in range(0, len(trades_df)-1):
        if (trades_df['action'].iloc[j] == 'buy' and trades_df['action'].iloc[j+1] == 'close long') or \
            (trades_df['action'].iloc[j] == 'short' and trades_df['action'].iloc[j+1] == 'close short'):
            trade_pnl = trades_df['Total profit'].iloc[j+1] - trades_df['Total profit'].iloc[j] 
            trades_summary_df = trades_summary_df.append({"Trade Type": trades_df['action'].iloc[j], \
                "Trade Open Time": trades_df['time'].iloc[j], "Trade Open Price": trades_df['Executed price'].iloc[j], \
                    "Trade Close Time": trades_df['time'].iloc[j+1], "Trade Close Price": trades_df['Executed price'].iloc[j+1], \
                        "Trade P/L": trade_pnl}, ignore_index = True)

    return trades_summary_df

# orig_dir = os.getcwd()
# backtest_folder = "200622-183546_USDCAD-2021-12-31_to_2022-05-31"
# file_dir = os.path.join(orig_dir, "backtests", backtest_folder)
# filename = "backtesting_history" + backtest_folder + ".csv"
# dat_dir = os.path.join(file_dir, filename)

# dat = pd.read_csv(dat_dir)
# test1 = get_trade_summary(dat)
# print("test1")