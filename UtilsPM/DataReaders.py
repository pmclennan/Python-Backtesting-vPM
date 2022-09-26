import pandas as pd
import pytz

def MT5SymbolsDataReader(dataDir, utc = True):

    data = pd.read_csv(dataDir, sep = '\t', parse_dates = [['<DATE>', '<TIME>']])

    for oldCol in data.columns:
        data.rename(columns = {oldCol: oldCol.replace('<', '').replace('>', '').replace('_', '').lower()}, inplace = True)
        
    data.rename(columns = {data.columns[0]: 'time'}, inplace = True)
    data = data[['time', 'open', 'high', 'low', 'close']]
    
    if utc:
        data['time'] = data['time'].dt.tz_localize(tz = pytz.utc)

    return data