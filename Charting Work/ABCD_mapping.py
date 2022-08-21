#Forward Looking
import pandas as pd

## To DO - check on the threshold (1.61 +- 0.05)... only returned 1 

def ABCD_mapping(data):
    zigzagDF = data[data['ZigZag Type'] != ''][['time', 'ZigZag Type', 'ZigZag Value']].copy().reset_index(drop = True)
    data['ABCD1'] = [""] * len(data)
    data['ABCD2'] = [""] * len(data)
    data['ABCD3'] = [""] * len(data)
    data['ABCD4'] = [""] * len(data)

    for i in range(len(data)):
        if data['ZigZag Type'].iloc[i] != '' and data['time'].iloc[i] < zigzagDF['time'].iloc[-3]:
            zz_idxA = zigzagDF[zigzagDF['time'] == data['time'].iloc[i]].index.values[0]
            
            Apx = zigzagDF['ZigZag Value'].iloc[zz_idxA]
            Bpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+1]
            Cpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+2]
            Dpx = zigzagDF['ZigZag Value'].iloc[zz_idxA+3]
            
            ABdiff = abs(Bpx - Apx)
            BCdiff = abs(Cpx - Bpx)
            
            idxC = data[data['time'] == zigzagDF['time'].iloc[zz_idxA+2]].index.values[0]
            Cnexthighpx = data['high'].iloc[idxC+1]
            Cnextlowpx = data['low'].iloc[idxC+1]
            
            #Down Trend: 
            #Peak A > Peak C < Valley D
            #ABdiff/BCdiff = 1.61 +- 0.05
            #Dpx < Bpx
            #C Px > C(+1) High Px
            
            #if (data['ZigZag Type'].iloc[i] == 'peak') and (Apx > Cpx > Dpx) and (1.56 <= ABdiff/BCdiff <= 1.66) and (Dpx < Bpx) and (Cnexthighpx < Cpx):
            if (data['ZigZag Type'].iloc[i] == 'peak') and (Apx > Cpx > Dpx) and (Dpx < Bpx) and (Cnexthighpx < Cpx):
                #Conditions met - find indices in main DF (B & D left) and insert labels
                idxB = data[data['time'] == zigzagDF['time'].iloc[zz_idxA+1]].index.values[0]
                idxD = data[data['time'] == zigzagDF['time'].iloc[zz_idxA+3]].index.values[0]
                
                #Multiple Mapping
                if (data['ABCD1'].iloc[i] == '') and (data['ABCD1'].iloc[idxB] == '') and (data['ABCD1'].iloc[idxC] == '') and (data['ABCD1'].iloc[idxD] == ''):
                
                    data['ABCD1'].iloc[i] = 'A'
                    data['ABCD1'].iloc[idxB] = 'B'
                    data['ABCD1'].iloc[idxC] = 'C'
                    data['ABCD1'].iloc[idxD] = 'D'
                
                elif (data['ABCD2'].iloc[i] == '') and (data['ABCD2'].iloc[idxB] == '') and (data['ABCD2'].iloc[idxC] == '') and (data['ABCD2'].iloc[idxD] == ''):
                
                    data['ABCD2'].iloc[i] = 'A'
                    data['ABCD2'].iloc[idxB] = 'B'
                    data['ABCD2'].iloc[idxC] = 'C'
                    data['ABCD2'].iloc[idxD] = 'D'
                
                elif (data['ABCD3'].iloc[i] == '') and (data['ABCD3'].iloc[idxB] == '') and (data['ABCD3'].iloc[idxC] == '') and (data['ABCD3'].iloc[idxD] == ''):
                
                    data['ABCD3'].iloc[i] = 'A'
                    data['ABCD3'].iloc[idxB] = 'B'
                    data['ABCD3'].iloc[idxC] = 'C'
                    data['ABCD3'].iloc[idxD] = 'D'
                
                elif (data['ABCD4'].iloc[i] == '') and (data['ABCD4'].iloc[idxB] == '') and (data['ABCD4'].iloc[idxC] == '') and (data['ABCD4'].iloc[idxD] == ''):
                
                    data['ABCD4'].iloc[i] = 'A'
                    data['ABCD4'].iloc[idxB] = 'B'
                    data['ABCD4'].iloc[idxC] = 'C'
                    data['ABCD4'].iloc[idxD] = 'D'
                                    
                                    
            #Up Trend: 
            #Valley A < Valley C < Peak B
            #ABdiff/BCdiff = 1.61 +- 0.05
            #Dpx > Bpx
            #C Px > C(+1) Low Px
            
            #if (data['ZigZag Type'].iloc[i] == 'valley') and (Apx < Cpx < Dpx) and (1.56 <= ABdiff/BCdiff <= 1.66) and (Dpx > Bpx) and (Cnextlowpx < Cpx):
            if (data['ZigZag Type'].iloc[i] == 'valley') and (Apx < Cpx < Dpx) and (Dpx > Bpx) and (Cnextlowpx < Cpx):
                #Conditions met - find indices in main DF (B & D left) and insert labels
                idxB = data[data['time'] == zigzagDF['time'].iloc[zz_idxA+1]].index.values[0]
                idxD = data[data['time'] == zigzagDF['time'].iloc[zz_idxA+3]].index.values[0]
                
                #Multiple Mapping
                if (data['ABCD1'].iloc[i] == '') and (data['ABCD1'].iloc[idxB] == '') and (data['ABCD1'].iloc[idxC] == '') and (data['ABCD1'].iloc[idxD] == ''):
                
                    data['ABCD1'].iloc[i] = 'A'
                    data['ABCD1'].iloc[idxB] = 'B'
                    data['ABCD1'].iloc[idxC] = 'C'
                    data['ABCD1'].iloc[idxD] = 'D'
                
                elif (data['ABCD2'].iloc[i] == '') and (data['ABCD2'].iloc[idxB] == '') and (data['ABCD2'].iloc[idxC] == '') and (data['ABCD2'].iloc[idxD] == ''):
                
                    data['ABCD2'].iloc[i] = 'A'
                    data['ABCD2'].iloc[idxB] = 'B'
                    data['ABCD2'].iloc[idxC] = 'C'
                    data['ABCD2'].iloc[idxD] = 'D'
                
                elif (data['ABCD3'].iloc[i] == '') and (data['ABCD3'].iloc[idxB] == '') and (data['ABCD3'].iloc[idxC] == '') and (data['ABCD3'].iloc[idxD] == ''):
                
                    data['ABCD3'].iloc[i] = 'A'
                    data['ABCD3'].iloc[idxB] = 'B'
                    data['ABCD3'].iloc[idxC] = 'C'
                    data['ABCD3'].iloc[idxD] = 'D'
                
                elif (data['ABCD4'].iloc[i] == '') and (data['ABCD4'].iloc[idxB] == '') and (data['ABCD4'].iloc[idxC] == '') and (data['ABCD4'].iloc[idxD] == ''):
                
                    data['ABCD4'].iloc[i] = 'A'
                    data['ABCD4'].iloc[idxB] = 'B'
                    data['ABCD4'].iloc[idxC] = 'C'
                    data['ABCD4'].iloc[idxD] = 'D'         