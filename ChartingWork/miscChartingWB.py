import pandas as pd
import os

dataFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Large Datasets"
#dataFilename = "EURUSDZigZagM1_2017v2.csv"
#dataFilename = "EURUSDZigZagM1_2017.csv"
dataFilename = "EURUSDZigZagM1_2017v3.csv"
dataDir = os.path.join(dataFolder, dataFilename)

#data = pd.read_csv(dataDir, encoding = "utf-16be")
data = pd.read_csv(dataDir, sep = "\t")

print("Break Point")