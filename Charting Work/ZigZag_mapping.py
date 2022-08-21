import pandas as pd

def ZigZagPoints(data, depth, deviation, backstep, pipsize):

    dat_zigzag = data.copy().reset_index(drop = True)
    start_val = dat_zigzag['close'].iloc[0]

    start_high_diff = abs(max(dat_zigzag['high'].iloc[0:depth]) - start_val)
    start_low_diff = abs(min(dat_zigzag['low'].iloc[0:depth]) - start_val)

    if start_high_diff > start_low_diff:
        start_pos = 'peak'
        start_idx = dat_zigzag['high'].iloc[0:depth].idxmax()
        start_px = max(dat_zigzag['high'].iloc[0:depth])
    else:
        start_pos = 'valley'
        start_idx = dat_zigzag['low'].iloc[0:depth].idxmin()
        start_px = min(dat_zigzag['low'].iloc[0:depth])

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
    

    for i in range(0, len(pos_list)):
        if pos_list[i] == 'peak':
            zigzag_vals[i] = dat_zigzag['high'].iloc[i]
        elif pos_list[i] == 'valley':
            zigzag_vals[i] = dat_zigzag['low'].iloc[i]
        dat_zigzag['ZigZag Value'] = zigzag_vals        
        
    return dat_zigzag