import pandas as pd

def ZigZagPoints(data, depth, deviation, backstep, pipsize):

    dat_zigzag = data.copy().reset_index(drop = True)
    start_val = dat_zigzag['close'].iloc[0]

    #Find first zig/zag within the first 2 bars.
    #The main loop will overtake this

    start_high_diff = abs(max(dat_zigzag['high'].iloc[0:1]) - start_val)
    start_low_diff = abs(min(dat_zigzag['low'].iloc[0:1]) - start_val)

    if start_high_diff > start_low_diff:
        start_pos = 'peak'
        start_idx = dat_zigzag['high'].iloc[0:1].idxmax()
        start_px = max(dat_zigzag['high'].iloc[0:1])
    else:
        start_pos = 'valley'
        start_idx = dat_zigzag['low'].iloc[0:1].idxmin()
        start_px = min(dat_zigzag['low'].iloc[0:1])

    #Set up initial references

    curr_pos = start_pos
    curr_px = start_px
    curr_idx = start_idx
    pos_list = [''] * len(dat_zigzag)
    pos_list[curr_idx] = curr_pos

    if curr_pos == 'peak':
        last_peak_idx = curr_idx
        last_valley_idx = 0
    else:
        last_valley_idx = curr_idx
        last_peak_idx = 0

    for i in range(start_idx, len(dat_zigzag)):   

        #Iterate though from the starting peak/valley
        #Going via the following rules:
            #First check for an overriding peak/valley
            #Then check for new/the opposing valley/peak, within the backstep & depth parameters, and override this.
            #Parameters intepreted as:
                #Depth: Minimum between previous peak/valley to next peak/valley respectively
                #Baskstep: Minimum between previous peak/valley to next valley/peak respectively
                    #IE, if peak at candle X, valley at candle Y, and new peak then at candle Z
                    #-> Y >= X + Backstep, and Z >= X + depth.
                #Deviation: Minimum price differential to establish new peak/valley (seen this to be referred in pips for FX)
                    #IE, abs(newPrice/prevPrice >= deviation * pip_size (so 0.00001))

            #Some sources (with fleshed out description of parameters): 
            # https://tradeasy.tech/en/zig-zag/, http://www.fxcorporate.com/help/MS/NOTFIFO/i_ZigZag.html & https://www.daytradetheworld.com/trading-blog/zig-zag-indicator/ 

        if curr_pos == 'peak':
            if dat_zigzag['high'].iloc[i] > curr_px:
                pos_list[last_peak_idx] = ''
                pos_list[i] = 'peak'
                curr_idx = i
                curr_px = dat_zigzag['high'].iloc[i]
                last_peak_idx = i

            elif curr_px/dat_zigzag['low'].iloc[i] >= 1 + (deviation/(100 / pipsize)) and i >= curr_idx + backstep + 1 and i >= last_valley_idx + depth:
                pos_list[i] = 'valley'
                curr_px = dat_zigzag['low'].iloc[i]
                curr_pos = 'valley'
                curr_idx = i
                last_valley_idx = i

        if curr_pos == 'valley':
            if dat_zigzag['low'].iloc[i] < curr_px:
                pos_list[last_valley_idx] = ''
                pos_list[i] = 'valley'
                curr_idx = i
                curr_px = dat_zigzag['low'].iloc[i]
                last_valley_idx = i

            elif dat_zigzag['high'].iloc[i]/curr_px >= 1 + (deviation/(100 / pipsize)) and i >= curr_idx + backstep + 1 and i >= last_peak_idx + depth:
                pos_list[i] = 'peak'            
                curr_px = dat_zigzag['high'].iloc[i]
                curr_pos = 'peak'
                curr_idx = i
                last_peak_idx = i    
                
    dat_zigzag['ZigZag Type'] = pos_list
    zigzag_vals = pos_list.copy()
    

    #Mapping the price values - plotting and reference purposes
    for i in range(0, len(pos_list)):
        if pos_list[i] == 'peak':
            zigzag_vals[i] = dat_zigzag['high'].iloc[i]
        elif pos_list[i] == 'valley':
            zigzag_vals[i] = dat_zigzag['low'].iloc[i]
        dat_zigzag['ZigZag Value'] = zigzag_vals        
        
    return dat_zigzag