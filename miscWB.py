import os
import datetime
import pandas as pd
import pytz

tz = pytz.utc
start_date = datetime.datetime(2022, 12, 31, tzinfo = tz)
end_date = datetime.datetime(2022, 5, 31, tzinfo = tz)
data_filename = "GBPUSD_M15__2020-01-02_to_2022-06-03.csv"
currency = data_filename.split("_")[0]
frequency_str = data_filename.split("_")[1]
input_len = 60

data_dir = os.path.join(os.getcwd(), "Datasets")
data_file = os.path.join(data_dir, data_filename).replace('\\', '/')

full_data = pd.read_csv(data_file, parse_dates = ['time'])
full_data['time'] = full_data['time'].dt.tz_localize(tz = tz)

start_idx = full_data.index[full_data['time'] >= start_date][0]
start_idx_adj = (start_idx - input_len) if (start_idx - input_len) > 0 else 0
end_idx =  full_data.index[full_data['time'] == end_date][0]

data = full_data[start_idx_adj:end_idx]

print(data.head())
print(start_date)
print(data.tail())
print(end_date)

print("Something")