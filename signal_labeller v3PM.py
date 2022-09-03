import pandas as pd
import os

'''
Labels each time period with appropriate trade signal based on the pip profit that we wnat to reach. This algorithm takes spread into consideration.
Currently early exit due to stoploss is not factored in.
Input:  a csv file containing the stock raw data
        takeprofit bound
Output: a csv file with new column that assigns trade signals:
            1 - if the pip upper bound is reached first
            -1 - if the pip lower bound is reached first
            0 - if neither is reached
            2 - if upper and lower bound is reached at the same time
        and the index where the trade will reach the profit defined by the takeprofit
'''

'''
##########################
############# Input Parameters #############
file_name = 'M30_2020\EURUSD_M30_202001020600_202012312330.csv'
takeprofit = 20
############# Read File #############
data = pd.read_csv(file_name, sep=',', skiprows=1, names = ['date', 'time', 'open', 'high', 'low', 'close', 'tickvol','vol','spread'], nrows = 500)
##########################
'''

def signal_labeller(data, takeprofit):

    ############# Hyperparameters #############
    pip = 0.0001
    #spread = 3

    ############# Labeling #############
    #looping over each bar
    data['label'] = 0
    data['exit_index'] = 0
    for i in range(len(data.index)-1):
        cur_price = data['open'].iloc[i+1]
        
        for j in range(i+1, len(data)):
            long_bound_hit = None
            short_bound_hit = None

            if (cur_price + takeprofit*pip <= data['high'].iloc[j]) or (cur_price - takeprofit*pip >= data['low'].iloc[j]):
                
                if (cur_price + takeprofit*pip <= data['high'].iloc[j]) and (cur_price - takeprofit*pip >= data['low'].iloc[j]):
                    long_bound_hit = j
                    short_bound_hit = j

                elif (cur_price + takeprofit*pip <= data['high'].iloc[j]):
                    long_bound_hit = j

                elif (cur_price - takeprofit*pip >= data['low'].iloc[j]):
                    short_bound_hit = j

                break

        if long_bound_hit == None and short_bound_hit == None:
            label = 0
            exit_index = None
        elif long_bound_hit == None:
            label = -1
            exit_index = short_bound_hit
        elif short_bound_hit == None:
            label = 1
            exit_index = long_bound_hit
        elif long_bound_hit == short_bound_hit:
            label = 2
            exit_index = long_bound_hit
        elif long_bound_hit < short_bound_hit:
            label = 1
            exit_index = long_bound_hit
        elif short_bound_hit < long_bound_hit:
            label = -1
            exit_index = short_bound_hit
        else:
            label = 0
            exit_index = -1

        data.loc[i,'label'] = label
        data.loc[i,'exit_index'] = exit_index
        if i % 10 == 0:
            print("Progress:", round(100 * (i/len(data)), 2), "%", end = "\r", flush = True)

    ############# Output #############
    #data.to_csv('EURUSD_M5_' + str(takeprofit) + '_labeled.csv')

    return data

##Patrick
data_filename = "EURUSD.a_M1_202009020000_202209022356.csv"
#data_folder = "C:\\Users\\Patrick\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Symbols Method"
data_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Symbols Method"
data_dir = os.path.join(data_folder, data_filename)
data = pd.read_csv(data_dir, sep='\t', skiprows=1, names = ['date', 'time', 'open', 'high', 'low', 'close', 'tickvol','vol','spread'])
data['date'] = pd.to_datetime(data['date'])

end_date = data['date'].iloc[-1]
start_date = end_date - pd.Timedelta(weeks = 53)

data = data[data['date'] <= end_date][data['date'] >= start_date].reset_index(drop = True)

##Mingyu
#data_filename = 'M30_2020\EURUSD_M30_202001020600_202012312330.csv'
#data_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Mingyus Repo\\RL-FOREX-Trader\\Testing Data"
#data_dir = os.path.join(data_folder, data_filename)
#data = pd.read_csv(data_dir, sep=',', skiprows=1, names = ['date', 'time', 'open', 'high', 'low', 'close', 'tickvol','vol','spread'], nrows = 500)

export_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Labelling project\\Individual Runs\\EURUSD_M1_V5"
export_prefix = data_filename.split("_")[0] + "_" + data_filename.split("_")[1] + "__" + start_date.strftime('%Y%m%d') + '_' + end_date.strftime('%Y%m%d')

for i in range(20, 25, 5):
    print("Running for {} pip TP".format(i))
    run = signal_labeller(data, i)
    export_filename = export_prefix.split(".csv")[0] + ("-{}-TP.csv".format(i))
    export_dir = os.path.join(export_folder, export_filename)
    run.to_csv(export_dir)
    print("\n Exported") 