from unittest import skip
import pandas as pd
import os

#Reads the signal labelled files and concatenates then saves output    

def signal_combiner(data_prefix, data_dir, export_dir, export_name):

    all_files = os.listdir(data_dir)
    files = []
    for f in all_files:
        if data_prefix in f:
            files.append(f)

    for i in range(len(files)):
        file_dir = os.path.join(data_dir, files[i])
        limit = file_dir.split("-TP")[0][-2:]
        data = pd.read_csv(file_dir)
        data = data[data.columns[1:]]
        
        if i == 0:
            master_df = data
            master_df.rename(columns = {'label': 'label_' + limit, 'exit_index': 'exit_index_' + limit}, inplace = True)
        else:
            master_df[['label_' + limit, 'exit_index_' + limit]] = data[['label', 'exit_index']]

    master_df.to_csv(export_dir + export_name + '.csv')

    return master_df

export_dir = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Labelling project\\Multi Label\\"
export_suffix = '_Signals_Combined'
data_dir = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Labelling project\\Multi Label\\Data"
data_prefix = "EURUSD_M30"
export_name = data_prefix + export_suffix

signal_combiner(data_prefix, data_dir, export_dir, export_name)