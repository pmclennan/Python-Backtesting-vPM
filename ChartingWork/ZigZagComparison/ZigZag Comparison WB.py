import os
import matplotlib.pyplot as plt
import pandas as pd
import pytz

dataFolder = os.path.join(os.getcwd(), 'ChartingWork', 'ZigZagComparison')

MT5DatFileName = 'ZigZagvMT.csv'
MT5DatDir = os.path.join(dataFolder, MT5DatFileName)

MyDatFileName = 'ZigZagvME.csv'
MyDatDir = os.path.join(dataFolder, MyDatFileName)

MT5Dat = pd.read_csv(MT5DatDir, sep = '\t', parse_dates = ['Date'])
MyDat = pd.read_csv(MyDatDir, parse_dates = ['time'])

MT5Dat.rename(columns = {'Buffer#0': 'ZigZag', 'Date': 'Time'}, inplace = True)
MT5Dat['Time'] = MT5Dat['Time'].dt.tz_localize(tz = pytz.utc)

MyDat.drop(columns = ['tick_volume', 'spread', 'real_volume'], inplace = True)

for column in MyDat.columns:
    newName = column[0].upper() + column[1:]
    MyDat.rename(columns = {column: newName}, inplace = True)

if MT5Dat.loc[0, 'Time'] > MyDat.loc[0, 'Time']:
    MyDat = MyDat.loc[MyDat['Time'] >= MT5Dat.loc[0, 'Time'], :].reset_index(drop = True)
elif MyDat.loc[0, 'Time'] > MT5Dat.loc[0, 'Time']:
    MT5Dat = MT5Dat.loc[MT5Dat['Time'] >= MyDat.loc[0, 'Time'], :].reset_index(drop = True)


MT5Dat = MT5Dat.iloc[:-1]
MyDat = MyDat.iloc[:-1]

print("BreakPoint")