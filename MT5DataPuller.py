import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import datetime
import pytz

class MT5DataPuller:
    def __init__(self, currency, interval, start_date, end_date):
        self.currency = currency
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        
        self.rates_data_df = None
        self.ticks_data_df = None
        self.ticks_data_minutely_single_df = None
        self.agg_data_df = None

        #Connection Check
        mt5.initialize()
        self.connection_status = mt5.initialize()
        
        #Confirmation of connection
        if self.connection_status == True:
            self.server = mt5.account_info().server
            print("Connected to MT5 under server {}".format(self.server))
        else:
            print("Connection Issue")
        
#Main datapull function
    def pull(self, batch_size = 0):

        ## Check Connection
        if self.connection_status == False:
            print("Connection Issue - Data Pull will fail")
            return None

        if batch_size == 0:
            n_full_batches = 1
            ## Trying in one pull if no batch_size defined

            print("Pulling Rates Data...")
            rates_data = mt5.copy_rates_range(self.currency, self.interval, self.start_date, self.end_date)
            print("Pulling Ticks Data...")
            ticks_data = mt5.copy_ticks_range(self.currency, self.start_date, self.end_date, mt5.COPY_TICKS_ALL)
            #ticks_data = mt5.copy_ticks_range(self.currency, self.start_date, self.end_date, mt5.COPY_TICKS_INFO)

            #Put data into DF
            rates_data_df = pd.DataFrame(rates_data)    
            ticks_data_df = pd.DataFrame(ticks_data)

            #Error handling - usually because pull range is too long!
            if ticks_data is None or ticks_data.size == 0 or rates_data is None or rates_data.size == 0:
                batch_size = 5 #Set to batch size of 5 to resolve for pull range being too long
                print("Issue with single pull")
            else:
                print("Pulled in one batch")
        
        #Pull in batches to concatenate
        if batch_size > 0:
            n_full_batches = (self.end_date - self.start_date).days // batch_size ##Round division with final batch being smaller

            if n_full_batches < 1: #Error handling if odd batch size is computed
                print("batch size exceeds pull length - reverting batch size to 1")
                n_full_batches = 1

                print("Pulling Rates Data...")
                rates_data = mt5.copy_rates_range(self.currency, self.interval, self.start_date, self.end_date)
                print("Pulling Ticks Data...")
                ticks_data = mt5.copy_ticks_range(self.currency, self.start_date, self.end_date, mt5.COPY_TICKS_ALL)
                #ticks_data = mt5.copy_ticks_range(self.currency, self.start_date, self.end_date, mt5.COPY_TICKS_INFO)
        
                rates_data_df = pd.DataFrame(rates_data)    
                ticks_data_df = pd.DataFrame(ticks_data)

                if ticks_data is None or ticks_data.size == 0 or rates_data is None or rates_data.size == 0: #If batches still don't work
                    print("Issue with data pull")

            else:
                #Set up lists for different date ranges to use as batches
                if self.interval == mt5.TIMEFRAME_D1:
                    start_dl = [self.start_date + datetime.timedelta(days = i * batch_size) for i in range(0, n_full_batches+1)]
                    end_dl = [self.start_date + datetime.timedelta(days = i * batch_size) for i in range(1, n_full_batches+1)]
                    end_dl.append(self.end_date)
                else:
                    start_dl = [self.start_date + datetime.timedelta(days = i * batch_size) for i in range(0, n_full_batches+1)]
                    end_dl = [self.start_date + datetime.timedelta(days = i * batch_size, minutes = 15) for i in range(1, n_full_batches+1)]
                    end_dl.append(self.end_date + datetime.timedelta(minutes = 15))
                
                rates_pulls_list = []
                tick_pulls_list = []

                print("Pulling in {} batches with average size of {} days".format(n_full_batches+1, batch_size)) ## Summary statement
            
                for i in range(0, n_full_batches+1):
                    #Pull in batches based off start date/end date lists defined above
                    print("\rPulling Batch: {}/{}".format(i+1, n_full_batches+1), end = "\r", flush = True) ## Progress statement

                    batch_rates_pull = mt5.copy_rates_range(self.currency, self.interval,start_dl[i], end_dl[i])
                    batch_rates_pull_df = pd.DataFrame(batch_rates_pull)
                    batch_rates_pull_df['time'] = pd.to_datetime(batch_rates_pull_df['time'], unit = 's')
                    rates_pulls_list.append(batch_rates_pull_df)

                    batch_ticks_pull = mt5.copy_ticks_range(self.currency, start_dl[i], end_dl[i], mt5.COPY_TICKS_ALL)
                    #batch_ticks_pull = mt5.copy_ticks_range(self.currency, start_dl[i], end_dl[i], mt5.COPY_TICKS_INFO)
                    batch_ticks_pull_df = pd.DataFrame(batch_ticks_pull)
                    batch_ticks_pull_df['time'] = pd.to_datetime(batch_ticks_pull_df['time'], unit = 's')
                    tick_pulls_list.append(batch_ticks_pull_df)

                    if batch_rates_pull is None or batch_rates_pull.size == 0:
                        print("\nIssue with rates pull at batch: ", i)
                    if batch_ticks_pull is None or batch_ticks_pull.size == 0:
                        print("\nIssue with ticks pull at batch: ", i)
                    
                #Concatenate these batch pulls
                rates_data_df = pd.concat(rates_pulls_list, ignore_index = True)
                ticks_data_df = pd.concat(tick_pulls_list, ignore_index = True)
        
            print("\n", n_full_batches+1, "batches pulled.")
        
        #Set time columns as datetime object
        if n_full_batches == 1:
            rates_data_df['time'] = pd.to_datetime(rates_data_df['time'], unit = 's')
            ticks_data_df['time'] = pd.to_datetime(ticks_data_df['time'], unit = 's')   
        
        #Subset relevant columns (as to note interfere with removing zeros)
        ticks_data_df = ticks_data_df[['time', 'bid', 'ask']]
        rates_data_df = rates_data_df[['time', 'open', 'high', 'low', 'close']]

        #Remove Zeros
        ticks_data_df = ticks_data_df.replace(0, np.nan).dropna().reset_index(drop = True)
        rates_data_df = rates_data_df.replace(0, np.nan).dropna().reset_index(drop = True)

        ticks_data_cleaned_df = ticks_data_df.copy()
        #Floor 10mins if around midnight... noticed missing data around midnight so still works as a decent proxy. 
        #Also won't make a difference for obvs where  there IS data around midnight.
        print("Flooring ticks time data")
        
        ticks_data_cleaned_df['time'].loc[ticks_data_cleaned_df['time'].dt.time <= datetime.time(0, 10, 0)] = ticks_data_cleaned_df['time'].loc[ticks_data_cleaned_df['time'].dt.time <= datetime.time(0, 10, 0)].dt.floor(freq = '10T')
        ticks_data_cleaned_df['time'] = ticks_data_cleaned_df['time'].dt.floor(freq = '5T')

        print("Aligning Ticks data with Rates Data")

        agg_data_df = rates_data_df.merge(ticks_data_cleaned_df, how = 'inner', on = 'time').groupby('time').first().reset_index()
        
        #Update as attributes of the main object
        self.rates_data_df = rates_data_df
        self.ticks_data_df = ticks_data_df
        self.ticks_data_cleaned_df = ticks_data_cleaned_df
        self.agg_data_df = agg_data_df

        print("Pull Complete")
        return agg_data_df

    #Modification methods
    def modify_currency(self, new_currency):
        self.currency = new_currency

    def modify_interval(self, new_interval):
        self.interval = new_interval

    def modify_start_date(self, new_start_date):
        self.start_date = new_start_date

    def modify_end_date(self, new_end_date):
        self.end_date = new_end_date

    #Summary of inputs/status
    def input_summary(self):
        summary_string = ("Connection Status: {} \n Server: {} \n Currency: {} \n Interval: {} \n Start Date: {} \n End Date: {}"
        .format(self.connection_status, self.server, self.currency, self.interval, self.start_date, self.end_date))
        print(summary_string)
        return summary_string