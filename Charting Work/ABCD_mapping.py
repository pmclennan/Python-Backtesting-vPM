#Forward Looking
import pandas as pd

## To DO - check on the threshold (1.61 +- 0.05)... only returned 1 

def ABCD_mapping(dataWithZigZags):

    #At this stage this requires the data input from the format of ZigZag_mapping/ZigZagPoints
    #NB - this adjusts the input dataframe and does not return anything/a new dataframe
    #Basically here just check mapped ZigZags against the conditions in a forward looking fashion
    
    #Currently have switched the threshold of ABdiff/BCdiff off (1.61+-0.05) as was limiting mapping... 
    #Need to check this but can be switched on by commenting/uncommenting the around lines 41 & 85
    
    #Regarding the multilabel mapping... new ABCD formats can form with the same zigzags as current ABCD forms.
    #This can result in the mapping being like [A, B, A, B, C, D] - that is, a new ABCD is mapped over a current one in progress.
    #Need to check this but for now have split this into 4 columns.

    zigzagDF = dataWithZigZags[dataWithZigZags['ZigZag Type'] != ''][['time', 'ZigZag Type', 'ZigZag Value']].copy().reset_index(drop = True)
    dataWithZigZags['ABCD1'] = [""] * len(dataWithZigZags)
    dataWithZigZags['ABCD2'] = [""] * len(dataWithZigZags)
    dataWithZigZags['ABCD3'] = [""] * len(dataWithZigZags)
    dataWithZigZags['ABCD4'] = [""] * len(dataWithZigZags)

    for i in range(len(dataWithZigZags)):
        if dataWithZigZags['ZigZag Type'].iloc[i] != '' and dataWithZigZags['time'].iloc[i] < zigzagDF['time'].iloc[-3]:
            zz_idxA = zigzagDF[zigzagDF['time'] == dataWithZigZags['time'].iloc[i]].index.values[0]
            
            Apx = zigzagDF['ZigZag Value'].iloc[zz_idxA]
            Bpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+1]
            Cpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+2]
            Dpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+3]
            
            ABdiff = abs(Bpx - Apx)
            BCdiff = abs(Cpx - Bpx)
            
            idxC = dataWithZigZags[dataWithZigZags['time'] == zigzagDF['time'].iloc[zz_idxA+2]].index.values[0]
            Cnexthighpx = dataWithZigZags['high'].iloc[idxC+1]
            Cnextlowpx = dataWithZigZags['low'].iloc[idxC+1]
            
            #Down Trend: 
            #Peak A > Peak C < Valley D
            #ABdiff/BCdiff = 1.61 +- 0.05
            #Dpx < Bpx
            #C Px > C(+1) High Px
            
            #if (dataWithZigZags['ZigZag Type'].iloc[i] == 'peak') and (Apx > Cpx > Dpx) and (1.56 <= ABdiff/BCdiff <= 1.66) and (Dpx < Bpx) and (Cnexthighpx < Cpx):
            if (dataWithZigZags['ZigZag Type'].iloc[i] == 'peak') and (Apx > Cpx > Dpx) and (Dpx < Bpx) and (Cnexthighpx < Cpx):
                #Conditions met - find indices in main DF (B & D left) and insert labels
                idxB = dataWithZigZags[dataWithZigZags['time'] == zigzagDF['time'].iloc[zz_idxA+1]].index.values[0]
                idxD = dataWithZigZags[dataWithZigZags['time'] == zigzagDF['time'].iloc[zz_idxA+3]].index.values[0]
                
                #Multiple Mapping
                if (dataWithZigZags['ABCD1'].iloc[i] == '') and (dataWithZigZags['ABCD1'].iloc[idxB] == '') and (dataWithZigZags['ABCD1'].iloc[idxC] == '') and (dataWithZigZags['ABCD1'].iloc[idxD] == ''):
                
                    dataWithZigZags['ABCD1'].iloc[i] = 'A'
                    dataWithZigZags['ABCD1'].iloc[idxB] = 'B'
                    dataWithZigZags['ABCD1'].iloc[idxC] = 'C'
                    dataWithZigZags['ABCD1'].iloc[idxD] = 'D'
                
                elif (dataWithZigZags['ABCD2'].iloc[i] == '') and (dataWithZigZags['ABCD2'].iloc[idxB] == '') and (dataWithZigZags['ABCD2'].iloc[idxC] == '') and (dataWithZigZags['ABCD2'].iloc[idxD] == ''):
                
                    dataWithZigZags['ABCD2'].iloc[i] = 'A'
                    dataWithZigZags['ABCD2'].iloc[idxB] = 'B'
                    dataWithZigZags['ABCD2'].iloc[idxC] = 'C'
                    dataWithZigZags['ABCD2'].iloc[idxD] = 'D'
                
                elif (dataWithZigZags['ABCD3'].iloc[i] == '') and (dataWithZigZags['ABCD3'].iloc[idxB] == '') and (dataWithZigZags['ABCD3'].iloc[idxC] == '') and (dataWithZigZags['ABCD3'].iloc[idxD] == ''):
                
                    dataWithZigZags['ABCD3'].iloc[i] = 'A'
                    dataWithZigZags['ABCD3'].iloc[idxB] = 'B'
                    dataWithZigZags['ABCD3'].iloc[idxC] = 'C'
                    dataWithZigZags['ABCD3'].iloc[idxD] = 'D'
                
                elif (dataWithZigZags['ABCD4'].iloc[i] == '') and (dataWithZigZags['ABCD4'].iloc[idxB] == '') and (dataWithZigZags['ABCD4'].iloc[idxC] == '') and (dataWithZigZags['ABCD4'].iloc[idxD] == ''):
                
                    dataWithZigZags['ABCD4'].iloc[i] = 'A'
                    dataWithZigZags['ABCD4'].iloc[idxB] = 'B'
                    dataWithZigZags['ABCD4'].iloc[idxC] = 'C'
                    dataWithZigZags['ABCD4'].iloc[idxD] = 'D'
                                    
                                    
            #Up Trend: 
            #Valley A < Valley C < Peak B
            #ABdiff/BCdiff = 1.61 +- 0.05
            #Dpx > Bpx
            #C Px > C(+1) Low Px
            
            #if (dataWithZigZags['ZigZag Type'].iloc[i] == 'valley') and (Apx < Cpx < Dpx) and (1.56 <= ABdiff/BCdiff <= 1.66) and (Dpx > Bpx) and (Cnextlowpx < Cpx):
            if (dataWithZigZags['ZigZag Type'].iloc[i] == 'valley') and (Apx < Cpx < Dpx) and (Dpx > Bpx) and (Cnextlowpx < Cpx):
                #Conditions met - find indices in main DF (B & D left) and insert labels
                idxB = dataWithZigZags[dataWithZigZags['time'] == zigzagDF['time'].iloc[zz_idxA+1]].index.values[0]
                idxD = dataWithZigZags[dataWithZigZags['time'] == zigzagDF['time'].iloc[zz_idxA+3]].index.values[0]
                
                #Multiple Mapping
                if (dataWithZigZags['ABCD1'].iloc[i] == '') and (dataWithZigZags['ABCD1'].iloc[idxB] == '') and (dataWithZigZags['ABCD1'].iloc[idxC] == '') and (dataWithZigZags['ABCD1'].iloc[idxD] == ''):
                
                    dataWithZigZags['ABCD1'].iloc[i] = 'A'
                    dataWithZigZags['ABCD1'].iloc[idxB] = 'B'
                    dataWithZigZags['ABCD1'].iloc[idxC] = 'C'
                    dataWithZigZags['ABCD1'].iloc[idxD] = 'D'
                
                elif (dataWithZigZags['ABCD2'].iloc[i] == '') and (dataWithZigZags['ABCD2'].iloc[idxB] == '') and (dataWithZigZags['ABCD2'].iloc[idxC] == '') and (dataWithZigZags['ABCD2'].iloc[idxD] == ''):
                
                    dataWithZigZags['ABCD2'].iloc[i] = 'A'
                    dataWithZigZags['ABCD2'].iloc[idxB] = 'B'
                    dataWithZigZags['ABCD2'].iloc[idxC] = 'C'
                    dataWithZigZags['ABCD2'].iloc[idxD] = 'D'
                
                elif (dataWithZigZags['ABCD3'].iloc[i] == '') and (dataWithZigZags['ABCD3'].iloc[idxB] == '') and (dataWithZigZags['ABCD3'].iloc[idxC] == '') and (dataWithZigZags['ABCD3'].iloc[idxD] == ''):
                
                    dataWithZigZags['ABCD3'].iloc[i] = 'A'
                    dataWithZigZags['ABCD3'].iloc[idxB] = 'B'
                    dataWithZigZags['ABCD3'].iloc[idxC] = 'C'
                    dataWithZigZags['ABCD3'].iloc[idxD] = 'D'
                
                elif (dataWithZigZags['ABCD4'].iloc[i] == '') and (dataWithZigZags['ABCD4'].iloc[idxB] == '') and (dataWithZigZags['ABCD4'].iloc[idxC] == '') and (dataWithZigZags['ABCD4'].iloc[idxD] == ''):
                
                    dataWithZigZags['ABCD4'].iloc[i] = 'A'
                    dataWithZigZags['ABCD4'].iloc[idxB] = 'B'
                    dataWithZigZags['ABCD4'].iloc[idxC] = 'C'
                    dataWithZigZags['ABCD4'].iloc[idxD] = 'D'         