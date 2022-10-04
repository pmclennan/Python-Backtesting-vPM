import pandas as pd
import numpy as np
import pytz
import datetime
import os

def StochasticOscilator(fullData, K = 14, D = 3, slowing = 3):

    retStochVals = [np.nan] * len(fullData)
    retStochSigVals = [np.nan] * len(fullData)

    for subset in range(2 * K, len(fullData)+1):
        data = fullData.iloc[subset - 2 * K:subset].reset_index(drop = True)

        #Buffers
        LowValList = [0] * K
        HighValList = [0] * K
        CloseValList = [0] * K
        for i in range(K):
            LowValList[i] = min(data['low'].iloc[i+1:K+i+1])
            HighValList[i] = max(data['high'].iloc[i+1:K+i+1])
            CloseValList[i] = data['close'].iloc[-K+i]

        stochVals = [0] * D
        for i in reversed(range(D)): #D
            sum_high = 0 
            sum_low = 0
            for j in reversed(range(1, slowing+1)): #Slow
                sum_low += (CloseValList[-j-i] - LowValList[-j-i])
                sum_high += (HighValList[-j-i] - LowValList[-j-i])
            if sum_high == 0:
                stochVals[-i-1] = 100
            else:
                stochVals[-i-1] = (sum_low/sum_high) * 100  

        stochSigVals = sum(stochVals)/len(stochVals)

        retStochVals[subset-1] = stochVals[-1]
        retStochSigVals[subset-1] = stochSigVals

    return retStochVals, retStochSigVals