import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import numpy as np

def plotCandles(data, start, end, xtick_iter = 8, gridOn = False, minorTicksOn = True, vertLineStamp = None):

    #Purpose here is to show candles (OHLC) but also deal with Matplotlib 'discontinuity' of plotting over weekends
    #Former is done by just plotting O, H, L & C separately (Open-Close as a wider bar) 
    #Latter is done by setting an array for index, then splicing strings of the datetime
    #Also ability to add a vertical line at an input timestamp (e.g. vertLineStamp = '2022-08-01 14:00:00+00:00')

    #Inputs (below all follow similar format)
    #Data - just the dataframe to plot
    #Start - start index to plot, around 100-200 candles is best without getting to messing. E.g. do start = 100, end = 250 or so
    #xtick_iter - this is fidgety, but basically controls how many timestamps are flagged on the xaxis (xtick_iter = 4 -> 1 xaxis label per 4 bars (hourly))
    #gridOn - to put grid on
    #minorTicksOn - to put x Axis Minor ticks on.
    #vertLineStampe - as flagged above.

    dat_plot = data.iloc[start:end].reset_index(drop = True, inplace = False)
    x = np.arange(0, len(dat_plot))
    plot_tl = [dat_plot['time'].iloc[x].strftime('%d-%b %H:%M') for x in range(0, len(dat_plot))]

    fig, ax = plt.subplots(figsize = (16, 9))

    for idx, val in dat_plot.iterrows():
        color = 'green'
        if val['open'] > val['close']:
            color = 'red'

        plt.plot([x[idx], x[idx]], [val['open'], val['close']], color = color, linewidth = 4)
        plt.plot([x[idx], x[idx]], [val['low'], val['open']], color = color)
        plt.plot([x[idx], x[idx]], [val['open'], val['high']], color = color)
    
    
    if vertLineStamp != None:
        plt.axvline(x = dat_plot[dat_plot['time'] == vertLineStamp].index.values[0], linestyle = '--')


    plt.xticks(x[::xtick_iter], plot_tl[::xtick_iter], rotation = 45)
    if gridOn:
        plt.grid(which = 'both')
    if minorTicksOn:
        ax.xaxis.set_minor_locator(MultipleLocator(1))
    plt.show()

def plotCandlesWithZigZag(data, start, end, xtick_iter = 8, gridOn = False, minorTicksOn = True, vertLineStamp = None):
    
    #As above, but adds line for zigzags
    #NB, requires a dataframe with ZigZag mapping from the function.

    dat_plot = data.iloc[start:end].reset_index(drop = True, inplace = False)
    x = np.arange(0, len(dat_plot))
    plot_tl = [dat_plot['time'].iloc[x].strftime('%d-%b %H:%M') for x in range(0, len(dat_plot))]

    fig, ax = plt.subplots(figsize = (16, 9))

    for idx, val in dat_plot.iterrows():
        color = 'green'
        if val['open'] > val['close']:
            color = 'red'

        plt.plot([x[idx], x[idx]], [val['open'], val['close']], color = color, linewidth = 4)
        plt.plot([x[idx], x[idx]], [val['low'], val['open']], color = color)
        plt.plot([x[idx], x[idx]], [val['open'], val['high']], color = color)
    
    
    if vertLineStamp != None:
        plt.axvline(x = dat_plot[dat_plot['time'] == vertLineStamp].index.values[0], linestyle = '--')
                          
    cols = list(dat_plot['ZigZag Type'][dat_plot['ZigZag Type'] != ''].copy())
    for i in range(0, len(cols)):
        if cols[i] == 'peak':
            cols[i] = 'green'
        elif cols[i] == 'valley':
            cols[i] = 'red'       
        
    zigZagX = list(dat_plot[dat_plot['ZigZag Type'] != ''].index.values)
    zigZagY = list(dat_plot['ZigZag Value'][dat_plot['ZigZag Value'] != ''])
    plt.plot(zigZagX, zigZagY)


    plt.xticks(x[::xtick_iter], plot_tl[::xtick_iter], rotation = 45)
    if gridOn:
        plt.grid(which = 'both')
    if minorTicksOn:
        ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.tick_right()
    plt.show()

def plotCandlesWithZigZagABCD(data, start, end, xtick_iter = 8, gridOn = False, ticksOn = True, vertLineStamp = None):

    #Again, same as above but now includes the first column of ABCD mapping.
    #To do - check on the multiple mapping and incorporate here.

    dat_plot = data.iloc[start:end].reset_index(drop = True, inplace = False)
    x = np.arange(0, len(dat_plot))
    plot_tl = [dat_plot['time'].iloc[x].strftime('%d-%b %H:%M') for x in range(0, len(dat_plot))]

    fig, ax = plt.subplots(figsize = (16, 9))

    for idx, val in dat_plot.iterrows():
        color = 'green'
        if val['open'] > val['close']:
            color = 'red'

        plt.plot([x[idx], x[idx]], [val['open'], val['close']], color = color, linewidth = 4)
        plt.plot([x[idx], x[idx]], [val['low'], val['open']], color = color)
        plt.plot([x[idx], x[idx]], [val['open'], val['high']], color = color)
    
    
    if vertLineStamp != None:
        plt.axvline(x = dat_plot[dat_plot['time'] == vertLineStamp].index.values[0], linestyle = '--')
                          
    cols = list(dat_plot['ZigZag Type'][dat_plot['ZigZag Type'] != ''].copy())
    for i in range(0, len(cols)):
        if cols[i] == 'peak':
            cols[i] = 'green'
        elif cols[i] == 'valley':
            cols[i] = 'red'       
        
    zigZagX = list(dat_plot[dat_plot['ZigZag Type'] != ''].index.values)
    zigZagY = list(dat_plot['ZigZag Value'][dat_plot['ZigZag Value'] != ''])
    plt.plot(zigZagX, zigZagY)

    ABCD_x = list(dat_plot[dat_plot['ABCD1'] != ''].index.values)
    ABCD_y = list(dat_plot['ZigZag Value'][dat_plot['ABCD1'] != ''])
    ABCD_m = list(dat_plot['ABCD1'][dat_plot['ABCD1'] != ''])
    ABCD_t = list(dat_plot['ZigZag Type'][dat_plot['ABCD1'] != ''])
    
    for i in range(len(ABCD_x)):
        if ABCD_t[i] == 'peak':
            plt.plot(ABCD_x[i], ABCD_y[i] + 0.0005, marker = '$' + ABCD_m[i] + '$', lw = 0, color = 'black')
        elif ABCD_t[i] == 'valley':
            plt.plot(ABCD_x[i], ABCD_y[i] - 0.0005, marker = '$' + ABCD_m[i] + '$', lw = 0, color = 'black')

    plt.xticks(x[::xtick_iter], plot_tl[::xtick_iter], rotation = 45)
    if gridOn:
        plt.grid(which = 'both')
    if ticksOn:
        ax.xaxis.set_minor_locator(MultipleLocator(1))
    plt.show()