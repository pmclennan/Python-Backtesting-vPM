import pandas as pd
import ta
import os

def mapLabelsWithIndicators(labelDat, maxBars):



    return None

labelDat_folder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Python Backtesting System\\github versions\\Live\\Python-Backtesting-vPM\\Labelling project\\withIndicators"
labelDat_filename = "20210809-20220815EURUSD_M1_Signals_Combined.csv"
labelDat_dir = os.path.join(labelDat_folder, labelDat_filename)

labelDat = pd.read_csv(labelDat_dir)
labelDat = labelDat.drop(columns = ['tickvol', 'vol', 'spread'])

print("Break Point")