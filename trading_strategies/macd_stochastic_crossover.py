# -*- coding: utf-8 -*-
"""
@author: vita
This strategy uses the MACD crossovers and Stochastic crossovers. The stochastic crossover should occur just before the MACD crossover.
https://www.dailyfx.com/forex/education/trading_tips/daily_trading_lesson/2020/02/11/macd-vs-stochastic.html
"""
import pandas as pd
import ta
import numpy as np

class MACDStochasticCrossover:
    def __init__(self):
        
        self.Name = "MACD_SCO"
        self.indicatorDf = None

    def addData(self, data):
        self.df = data        
        
        self.close = self.df['close']
        self.high = self.df['high']
        self.low = self.df['low']

        self.df['macd_line'] = [0] * len(data)
        self.df['macd_signal'] = [0] * len(data)
        self.df['stoch_line'] = [0] * len(data)
        self.df['stoch_signal'] = [0] * len(data)
    
    # calculates the macd line
    def add_macd_line(self):
        self.df['macd_line'] = ta.trend.MACD(close=self.close).macd()

    # calculate the macd signal (a 9 period ema of the macd line)
    def add_macd_signal(self):
        self.df['macd_signal'] = ta.trend.MACD(close=self.close).macd_signal()

    # caluclates stochastic line (%k)
    def add_stochastic_line(self):
        stoch = ta.momentum.StochasticOscillator(high=self.high, low=self.low, close=self.close)
        self.df['stoch_line'] = stoch.stoch()

    # calculate stochastic signal line (%d)
    def add_stochastic_signal_line(self):
        stoch_signal = ta.momentum.StochasticOscillator(high=self.high, low=self.low, close=self.close)
        self.df['stoch_signal'] = stoch_signal.stoch_signal()

    def determine_signal(self):
        m_line = self.df['macd_line']
        m_signal = self.df['macd_signal']
        k_line = self.df['stoch_line']
        d_signal = self.df['stoch_signal']

        action = 0

        # SELL CRITERIA: stoch %k and %d lines crossover that are >80 shortly before MACD signal and line crossover that are >0
        if (k_line.iloc[-3] > 80 and d_signal.iloc[-3] > 80 and k_line.iloc[-2] > 80 and d_signal.iloc[
            -2] > 80) and \
                ((k_line.iloc[-3] < d_signal.iloc[-3] and k_line.iloc[-2] > d_signal.iloc[-2])) and \
                (m_line.iloc[-2] > 0 and m_signal.iloc[-2] > 0 and m_line.iloc[-1] > 0 and m_signal.iloc[
                    -1] > 0) and \
                (m_line.iloc[-2] > m_signal.iloc[-2] and m_line.iloc[-1] < m_signal.iloc[-1]):

            action = -1

        # BUY CRITERIA: stoch %k and %d lines crossover that are <20 shortly before MACD signal and line crossover that are <0
        elif (k_line.iloc[-3] < 20 and d_signal.iloc[-3] < 20 and k_line.iloc[-2] < 20 and d_signal.iloc[
            -2] < 20) and \
                ((k_line.iloc[-3] > d_signal.iloc[-3] and k_line.iloc[-2] < d_signal.iloc[-2])) and \
                (m_line.iloc[-2] < 0 and m_signal.iloc[-2] < 0 and m_line.iloc[-1] < 0 and m_signal.iloc[
                    -1] < 0) and \
                (m_line.iloc[-2] < m_signal.iloc[-2] and m_line.iloc[-1] > m_signal.iloc[-1]):

            action = 1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'macd_line', 'macd_signal', 'stoch_line', 'stoch_signal']]

    def run(self, data):
        self.addData(data)
        self.add_macd_line()
        self.add_macd_signal()
        self.add_stochastic_line()
        self.add_stochastic_signal_line()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf