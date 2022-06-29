## Python based backtesting framework

Altered to add functionality of pulling data from MetaTrader 5 and incorporate bid/ask levels to further mimic
the live market.

Steps for running - main.py:
1. Copy file containing the selected strategy to the main folder. 
	NB: Strategy should just return signal as an integer, ie -1 (sell)/0 (hold)/1 (buy).
2. Ensure all packages are installed correctly (pandas, datetime, ta-lib etc) and 
3. Specify date range & data filename in the Initial setup. NB the data should be in the respective /Datasets folder.
4. Specify "Hyperparameters" such as input row size, pip size (important consideration for JPY), sl/tp and flat broker cost
5. Reassign the strategy under the backtest loop and method for signal (line 73/74 at this stage)
6. Run - all relevant outputs should be saved under a timestamped subfolder in /backtests

To manually observe the backtesting trading data use jupyter notebook visualise.ipynb

Auxiliary files:

a) signalHandler - Class made to handle functionality trading strategy.
	Inputs are fed through as part of the main backtest loop in the main.py file.
	
	Handles closing/opening trades, sl/tp tracking and action, buy/sell actions as well as 
	storing actions in history for final output.

b) visualise - Class made to visualise the trading strategy signals over the price history.

c) MT5DataPuller - Class made to pull data from MetaTrader 5 via the pull function.
	Requires connection to MetaTrader 5 (will flag if not connected).
	Variables for instantiation include currency (string in format of MT5 symbol), interval (mt5 Timeframe
	object), start date & end date (datetime objects.
	
	pull() method takes input batch_size, which dictates the size of each pull from MetaTrader and 
	is used to handle issues of failing to pull data in large sizes. NB: Has been found to be most 
	successful at batch size of 20.

d) DataPull Runs - file containing the PullData function that is used to pull data via the MT5DataPuller and 
export to csv.
	Takes currency, start_date, end_date and interval as specified for MT5 DataPuller as well as interval.
	Also takes freq_dict input as a dictionary mapping mt5 Timeframe objects as keys to strings as values for
	the purpose of naming the exported data file.

e) WeeklySummary - file containing the get_weekly_summary function that breaks down the backtest performance
on a weekly basis.
	Takes input data which is the export history of the backtest.

f) IntervalChecker - file containing the interval_checker_observations function that is used to review any 
missing data.
	Takes dataset (the input data file), frequency (pd.Timedelta object in the denomination of the data frequency) and
	print_output (whether or not to print the resulting dataframe upon execution).

g) miscWB - used for testing purposes. Can be disregarded.

+ Any trading strategy files.
