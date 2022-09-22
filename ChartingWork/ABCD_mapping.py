#Forward Looking
import pandas as pd
import numpy as np

## To DO - check on the threshold (1.61 +- 0.05)... only returned 1 

def ABCD_mapping(dataWithZigZags, thresholdMean = 0, thresholdVar = np.inf, labelSignal = 0):


    #At this stage this requires the data input from the format of ZigZag_mapping/ZigZagPoints
    #NB - this adjusts the input dataframe and does not return anything/a new dataframe
    #Basically here just check mapped ZigZags against the conditions in a forward looking fashion
    
    #Currently have switched the threshold of ABdiff/BCdiff off (1.61+-0.05) as was limiting mapping... 
    #Need to check this but can be switched on by commenting/uncommenting the around lines 41 & 85
    
    #Regarding the multilabel mapping... new ABCD formats can form with the same zigzags as current ABCD forms.
    #This can result in the mapping being like [A, B, A, B, C, D] - that is, a new ABCD is mapped over a current one in progress.
    #Need to check this but for now have split this into 4 columns.

    dataWithZigZags.loc[dataWithZigZags['ZigZag Value'] == 0, ['ZigZag Value', 'ZigZag Type']] = '' #Handle blanks as zeros

    dataWithZigZagsABCD = dataWithZigZags.copy()

    zigzagDF = dataWithZigZagsABCD[dataWithZigZagsABCD['ZigZag Type'] != ''][['time', 'ZigZag Type', 'ZigZag Value']].copy().reset_index(drop = True)
    dataWithZigZagsABCD['ABCD1'] = [""] * len(dataWithZigZagsABCD)
    dataWithZigZagsABCD['ABCD2'] = [""] * len(dataWithZigZagsABCD)
    dataWithZigZagsABCD['ABCD3'] = [""] * len(dataWithZigZagsABCD)
    dataWithZigZagsABCD['ABCD4'] = [""] * len(dataWithZigZagsABCD)

    for i in range(len(dataWithZigZagsABCD)):
        if dataWithZigZagsABCD['ZigZag Type'].iloc[i] != '' and dataWithZigZagsABCD['time'].iloc[i] < zigzagDF['time'].iloc[-3]:
            zz_idxA = zigzagDF[zigzagDF['time'] == dataWithZigZagsABCD['time'].iloc[i]].index.values[0]
            
            Apx = zigzagDF['ZigZag Value'].iloc[zz_idxA]
            Bpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+1]
            Cpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+2]
            Dpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+3]
            
            ABdiff = abs(Bpx - Apx)
            BCdiff = abs(Cpx - Bpx)
            
            idxC = dataWithZigZagsABCD[dataWithZigZagsABCD['time'] == zigzagDF['time'].iloc[zz_idxA+2]].index.values[0]
            Cnexthighpx = dataWithZigZagsABCD['high'].iloc[idxC+1]
            Cnextlowpx = dataWithZigZagsABCD['low'].iloc[idxC+1]
            
            #Down Trend: 
            #Peak A > Peak C < Valley D
            #ABdiff/BCdiff = 1.61 +- 0.05
            #Dpx < Bpx
            #C Px > C(+1) High Px
            
            if (dataWithZigZagsABCD['ZigZag Type'].iloc[i] == 'peak') and (Apx > Cpx > Dpx) and \
                (thresholdMean - thresholdVar <= ABdiff/BCdiff <= thresholdMean + thresholdVar) and (Dpx < Bpx) and (Cnexthighpx < Cpx):
                #Conditions met - find indices in main DF (B & D left) and insert labels
                idxB = dataWithZigZagsABCD[dataWithZigZagsABCD['time'] == zigzagDF['time'].iloc[zz_idxA+1]].index.values[0]
                idxD = dataWithZigZagsABCD[dataWithZigZagsABCD['time'] == zigzagDF['time'].iloc[zz_idxA+3]].index.values[0]
                
                #Multiple Mapping
                if (dataWithZigZagsABCD['ABCD1'].iloc[i] == '') and (dataWithZigZagsABCD['ABCD1'].iloc[idxB] == '') and (dataWithZigZagsABCD['ABCD1'].iloc[idxC] == '') and (dataWithZigZagsABCD['ABCD1'].iloc[idxD] == ''):
                
                    dataWithZigZagsABCD['ABCD1'].iloc[i] = 'A'
                    dataWithZigZagsABCD['ABCD1'].iloc[idxB] = 'B'
                    dataWithZigZagsABCD['ABCD1'].iloc[idxC] = 'C'
                    dataWithZigZagsABCD['ABCD1'].iloc[idxD] = 'D'
                
                elif (dataWithZigZagsABCD['ABCD2'].iloc[i] == '') and (dataWithZigZagsABCD['ABCD2'].iloc[idxB] == '') and (dataWithZigZagsABCD['ABCD2'].iloc[idxC] == '') and (dataWithZigZagsABCD['ABCD2'].iloc[idxD] == ''):
                
                    dataWithZigZagsABCD['ABCD2'].iloc[i] = 'A'
                    dataWithZigZagsABCD['ABCD2'].iloc[idxB] = 'B'
                    dataWithZigZagsABCD['ABCD2'].iloc[idxC] = 'C'
                    dataWithZigZagsABCD['ABCD2'].iloc[idxD] = 'D'
                
                elif (dataWithZigZagsABCD['ABCD3'].iloc[i] == '') and (dataWithZigZagsABCD['ABCD3'].iloc[idxB] == '') and (dataWithZigZagsABCD['ABCD3'].iloc[idxC] == '') and (dataWithZigZagsABCD['ABCD3'].iloc[idxD] == ''):
                
                    dataWithZigZagsABCD['ABCD3'].iloc[i] = 'A'
                    dataWithZigZagsABCD['ABCD3'].iloc[idxB] = 'B'
                    dataWithZigZagsABCD['ABCD3'].iloc[idxC] = 'C'
                    dataWithZigZagsABCD['ABCD3'].iloc[idxD] = 'D'
                
                elif (dataWithZigZagsABCD['ABCD4'].iloc[i] == '') and (dataWithZigZagsABCD['ABCD4'].iloc[idxB] == '') and (dataWithZigZagsABCD['ABCD4'].iloc[idxC] == '') and (dataWithZigZagsABCD['ABCD4'].iloc[idxD] == ''):
                
                    dataWithZigZagsABCD['ABCD4'].iloc[i] = 'A'
                    dataWithZigZagsABCD['ABCD4'].iloc[idxB] = 'B'
                    dataWithZigZagsABCD['ABCD4'].iloc[idxC] = 'C'
                    dataWithZigZagsABCD['ABCD4'].iloc[idxD] = 'D'
                                    
                                    
            #Up Trend: 
            #Valley A < Valley C < Peak B
            #ABdiff/BCdiff = 1.61 +- 0.05
            #Dpx > Bpx
            #C Px > C(+1) Low Px
            
            if (dataWithZigZagsABCD['ZigZag Type'].iloc[i] == 'valley') and (Apx < Cpx < Dpx) and \
                (thresholdMean - thresholdVar <= ABdiff/BCdiff <= thresholdMean + thresholdVar) and (Dpx > Bpx) and (Cnextlowpx < Cpx):
                #Conditions met - find indices in main DF (B & D left) and insert labels
                idxB = dataWithZigZagsABCD[dataWithZigZagsABCD['time'] == zigzagDF['time'].iloc[zz_idxA+1]].index.values[0]
                idxD = dataWithZigZagsABCD[dataWithZigZagsABCD['time'] == zigzagDF['time'].iloc[zz_idxA+3]].index.values[0]
                
                #Multiple Mapping
                if (dataWithZigZagsABCD['ABCD1'].iloc[i] == '') and (dataWithZigZagsABCD['ABCD1'].iloc[idxB] == '') and (dataWithZigZagsABCD['ABCD1'].iloc[idxC] == '') and (dataWithZigZagsABCD['ABCD1'].iloc[idxD] == ''):
                
                    dataWithZigZagsABCD['ABCD1'].iloc[i] = 'A'
                    dataWithZigZagsABCD['ABCD1'].iloc[idxB] = 'B'
                    dataWithZigZagsABCD['ABCD1'].iloc[idxC] = 'C'
                    dataWithZigZagsABCD['ABCD1'].iloc[idxD] = 'D'
                
                elif (dataWithZigZagsABCD['ABCD2'].iloc[i] == '') and (dataWithZigZagsABCD['ABCD2'].iloc[idxB] == '') and (dataWithZigZagsABCD['ABCD2'].iloc[idxC] == '') and (dataWithZigZagsABCD['ABCD2'].iloc[idxD] == ''):
                
                    dataWithZigZagsABCD['ABCD2'].iloc[i] = 'A'
                    dataWithZigZagsABCD['ABCD2'].iloc[idxB] = 'B'
                    dataWithZigZagsABCD['ABCD2'].iloc[idxC] = 'C'
                    dataWithZigZagsABCD['ABCD2'].iloc[idxD] = 'D'
                
                elif (dataWithZigZagsABCD['ABCD3'].iloc[i] == '') and (dataWithZigZagsABCD['ABCD3'].iloc[idxB] == '') and (dataWithZigZagsABCD['ABCD3'].iloc[idxC] == '') and (dataWithZigZagsABCD['ABCD3'].iloc[idxD] == ''):
                
                    dataWithZigZagsABCD['ABCD3'].iloc[i] = 'A'
                    dataWithZigZagsABCD['ABCD3'].iloc[idxB] = 'B'
                    dataWithZigZagsABCD['ABCD3'].iloc[idxC] = 'C'
                    dataWithZigZagsABCD['ABCD3'].iloc[idxD] = 'D'
                
                elif (dataWithZigZagsABCD['ABCD4'].iloc[i] == '') and (dataWithZigZagsABCD['ABCD4'].iloc[idxB] == '') and (dataWithZigZagsABCD['ABCD4'].iloc[idxC] == '') and (dataWithZigZagsABCD['ABCD4'].iloc[idxD] == ''):
                
                    dataWithZigZagsABCD['ABCD4'].iloc[i] = 'A'
                    dataWithZigZagsABCD['ABCD4'].iloc[idxB] = 'B'
                    dataWithZigZagsABCD['ABCD4'].iloc[idxC] = 'C'
                    dataWithZigZagsABCD['ABCD4'].iloc[idxD] = 'D'         

    if labelSignal == 1:
        signals = np.zeros(len(dataWithZigZagsABCD))
        longIdxs = list(dataWithZigZagsABCD.loc[dataWithZigZagsABCD['ABCD1'] == 'C'].loc[dataWithZigZagsABCD['ZigZag Type'] == 'valley'].index.values)
        shortIdxs = list(dataWithZigZagsABCD.loc[dataWithZigZagsABCD['ABCD1'] == 'C'].loc[dataWithZigZagsABCD['ZigZag Type'] == 'peak'].index.values)

        signals[longIdxs] = 1
        signals[shortIdxs] = -1

        dataWithZigZagsABCD['Signal'] = signals.astype('int')

    return dataWithZigZagsABCD