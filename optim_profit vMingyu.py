import pandas as pd

'''
Calculates the profit that can be made if trades are made following the signals
Input:  an output csv file from signal_labeller.py
        takeprofit
Output: an csv with every trade and total profit
'''
'''
##########################
############# Input Parameters #############
file_name = 'EURUSD_M30_202001020600_202012312330_labeled.csv'

############# Read File #############
data = pd.read_csv(file_name, sep=',', skiprows=1, names = ['date', 'time', 'open', 'high', 'low', 'close', 'tickvol','vol','spread', 'label','exit_index'], nrows = 500)
##########################
'''

def optim_profit(data, takeprofit):

    ############# Hyperparameters #############
    pip = 0.0001
    broker_fee = 2*pip

    ############# Variables #############
    total_profit = 0
    trades = []

    trade_type = 0
    trade_enter_index = -1
    trade_exit_index = -1

    ############# Calculating Profit #############
    for i, row in data.iterrows():
        #exiting the trade as the takeprofit was reached
        if trade_exit_index == i:
            #calculate profit as the trade exits
            #perhaps instead of close of index, open of index + 1? to more simulate ai acting on the trade AFTER the takeprofit was reached
            profit = trade_type*(data.loc[trade_exit_index, 'close'] - trade_type * data.loc[trade_exit_index, 'spread']*pip) - trade_type*(data.loc[trade_enter_index, 'close'] + trade_type * data.loc[trade_enter_index, 'spread']*pip) - broker_fee
            total_profit += profit
            trades.append([trade_type, trade_enter_index, trade_exit_index, profit, total_profit])

            trade_type = 0
            trade_enter_index = -1
            trade_exit_index = -1
        else:
            #if no current trade exists
            if trade_exit_index == -1:
                trade_type = row['label']
                trade_enter_index = i
                trade_exit_index = row['exit_index']
            #if trade proposed in current row will finish faster than what we currently have
            elif row['exit_index'] < trade_exit_index:
                trade_type = row['label']
                trade_enter_index = i
                trade_exit_index = row['exit_index']

    ############# Output #############
    output = pd.DataFrame(trades, columns = ['trade_type', 'trade_start', 'trade_finish', 'profit', 'rolling_profit'])
    output.to_csv('EURUSD_M5_' + str(takeprofit) + '_profit.csv')
    
    return total_profit

