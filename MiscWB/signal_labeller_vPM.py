import pandas as pd
import os 

def signal_labellervPM(data, takeprofit, fee):
  
    data['signal'] = [0] * len(data)

    for i in range(0, len(data)-2):
        
        #Check Long
        if data['ask'].iloc[i] - data['bid'].iloc[i+1] - fee >= takeprofit:
            data['signal'].iloc[i] = 1
        
        #Check Short
        elif data['ask'].iloc[i+1] - data['bid'].iloc[i] - fee >= takeprofit:
            data['signal'].iloc[i] = -1

    return data

#Patrick
data_filename = "EURUSD_M01__2021-06-30_to_2022-07-19-P.csv"
#data_filename = "EURUSD_H1__2021-07-01_to_2022-07-18-P.csv"
data_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Datasets\\Live Account"
data_dir = os.path.join(data_folder, data_filename)
data = pd.read_csv(data_dir)

export_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Labelling project\\vPM"
pip = 0.0001
fee = 2

for i in range(20, 65, 5):
    takeprofit = i * pip
    print("Running for {} pip TP".format(i))
    run = signal_labellervPM(data, takeprofit, fee * pip)
    #export_filename = (data_filename.split("\\")[1].split(".csv")[0]) + ("-{}-TP.csv".format(i))
    export_filename = data_filename.split(".csv")[0] + ("-{}-TP.csv".format(i))
    export_dir = os.path.join(export_folder, export_filename)
    run.to_csv(export_dir)
    print("Exported")    