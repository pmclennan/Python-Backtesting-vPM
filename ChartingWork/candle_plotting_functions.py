import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import numpy as np

def plotCandles(data, start = 0, end = 0, xtick_iter = 8, gridOn = False, minorTicksOn = True, vertLineStamp = None):

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

    if start == 0 and end == 0:
        end = len(data)    

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

def plotCandlesWithZigZag(data, start = 0, end = 0, xtick_iter = 8, gridOn = False, ticksOn = True, vertLineStamp = None):
    
    if start == 0 and end == 0:
        end = len(data)

    data.loc[data['ZigZag Value'] == 0, ['ZigZag Value', 'ZigZag Type']] = '' #Hack to allow zeros to work

    dat_plot = data.iloc[start:end].reset_index(drop = True, inplace = False)
    x = np.arange(0, len(dat_plot))
    plot_tl = [str(dat_plot['time'].dt.date.iloc[x]) + " " + str(dat_plot['time'].dt.time.iloc[x]) for x in range(0, len(dat_plot))]

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
    
    #Extrapolation for visualisation..
    if not data.loc[:start].loc[data['ZigZag Type'] != '']['ZigZag Value'].empty:
        leftYOut = data.loc[:start].loc[data['ZigZag Type'] != '']['ZigZag Value'].iloc[-1]
        leftYIn = data.loc[start:].loc[data['ZigZag Type'] != '']['ZigZag Value'].iloc[0]
        leftXOut = data.loc[:start].loc[data['ZigZag Type'] != ''].index.values[-1]
        leftXIn = data.loc[start:].loc[data['ZigZag Type'] != ''].index.values[0]
        dyLeft = (leftYIn-leftYOut)/(leftXIn-leftXOut)
        leftYExt = (leftYOut + (dyLeft * (start-leftXOut) * leftYOut))
        extLeftX = [0, leftXIn - start]
        extLeftY = [leftYExt, leftYIn]        
        plt.plot(extLeftX, extLeftY, linestyle = '--', color = 'b')
    
    if not data.loc[end:].loc[data['ZigZag Type'] != '']['ZigZag Value'].empty:
        rightYIn = data.loc[:end].loc[data['ZigZag Type'] != '']['ZigZag Value'].iloc[-1]
        rightYOut = data.loc[end:].loc[data['ZigZag Type'] != '']['ZigZag Value'].iloc[0]
        rightXIn = data.loc[:end].loc[data['ZigZag Type'] != ''].index.values[-1]
        rightXOut = data.loc[end:].loc[data['ZigZag Type'] != ''].index.values[0]
        dyRight = (rightYOut-rightYIn)/(rightXOut-rightXIn)
        rightYExt = (rightYIn + (dyRight * (end-rightXIn) * rightYIn))
        extRightX = [len(dat_plot) - (end - rightXIn), len(dat_plot)]
        extRightY = [rightYIn, rightYExt]    
        plt.plot(extRightX, extRightY, linestyle = '--', color = 'b')

    plt.xticks(x[::xtick_iter], plot_tl[::xtick_iter], rotation = 45)
    if gridOn:
        plt.grid(which = 'both')
    if ticksOn:
        ax.xaxis.set_minor_locator(MultipleLocator(1))
    plt.show()

def plotCandlesWithZigZagABCD(data, start = 0, end = 0, xtick_iter = None, gridOn = False, ticksOn = True, vertLineStamp = None):

    #Again, same as above but now includes the first column of ABCD mapping.
    #To do - check on the multiple mapping and incorporate here.

    if start == 0 and end == 0:
        end = len(data)

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
    yticksRange = max(plt.yticks()[0]) - min(plt.yticks()[0])

    for i in range(len(ABCD_x)):
        if ABCD_t[i] == 'peak':
            plt.plot(ABCD_x[i], ABCD_y[i] + 0.025 * yticksRange, marker = '$' + ABCD_m[i] + '$', lw = 0, color = 'black')
        elif ABCD_t[i] == 'valley':
            plt.plot(ABCD_x[i], ABCD_y[i] - 0.025 * yticksRange, marker = '$' + ABCD_m[i] + '$', lw = 0, color = 'black')

    #Extrapolation for visualisation..
    if not data.loc[:start].loc[data['ZigZag Type'] != '']['ZigZag Value'].empty:
        leftYOut = data.loc[:start].loc[data['ZigZag Type'] != '']['ZigZag Value'].iloc[-1]
        leftYIn = data.loc[start:].loc[data['ZigZag Type'] != '']['ZigZag Value'].iloc[0]
        leftXOut = data.loc[:start].loc[data['ZigZag Type'] != ''].index.values[-1]
        leftXIn = data.loc[start:].loc[data['ZigZag Type'] != ''].index.values[0]
        dyLeft = (leftYIn-leftYOut)/(leftXIn-leftXOut)
        leftYExt = (leftYOut + (dyLeft * (start-leftXOut) * leftYOut))
        extLeftX = [0, leftXIn - start]
        extLeftY = [leftYExt, leftYIn]        
        plt.plot(extLeftX, extLeftY, linestyle = '--', color = 'b')
    
    if not data.loc[end:].loc[data['ZigZag Type'] != '']['ZigZag Value'].empty:
        rightYIn = data.loc[:end].loc[data['ZigZag Type'] != '']['ZigZag Value'].iloc[-1]
        rightYOut = data.loc[end:].loc[data['ZigZag Type'] != '']['ZigZag Value'].iloc[0]
        rightXIn = data.loc[:end].loc[data['ZigZag Type'] != ''].index.values[-1]
        rightXOut = data.loc[end:].loc[data['ZigZag Type'] != ''].index.values[0]
        dyRight = (rightYOut-rightYIn)/(rightXOut-rightXIn)
        rightYExt = (rightYIn + (dyRight * (end-rightXIn) * rightYIn))
        extRightX = [len(dat_plot) - (end - rightXIn), len(dat_plot)]
        extRightY = [rightYIn, rightYExt]    
        plt.plot(extRightX, extRightY, linestyle = '--', color = 'b')

    plt.xticks(x[::xtick_iter], plot_tl[::xtick_iter], rotation = 45)
    if gridOn:
        plt.grid(which = 'both')
    if ticksOn:
        ax.xaxis.set_minor_locator(MultipleLocator(1))
    plt.show()

def plotCandlesWithPoint(data, pointX, pointY, start = 0, end = 0, xtick_iter = None, gridOn = False, minorTicksOn = True, vertLineStamp = None):

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

    if start == 0 and end == 0:
        end = len(data)    

    dat_plot = data.iloc[start:end].reset_index(drop = True, inplace = False)
    x = np.arange(0, len(dat_plot))
    plot_tl = [dat_plot['time'].iloc[x].strftime('%d-%b %H:%M') for x in range(0, len(dat_plot))]

    #Costmetic adjustment - major Xticks. Plot in line with something standard (eg 15/30min/1hr)
    if xtick_iter == None:
        freqMins = (dat_plot['time'].iloc[1] - dat_plot['time'].iloc[0])/pd.Timedelta('60s')
        if freqMins == 1:
            xtick_iter = 30
        if freqMins == 5:
            xtick_iter = 6
        elif freqMins == 10:
            xtick_iter = 3
        elif freqMins == 15:
            xtick_iter = 2    

    #Start major label at 0 or 30 mins
    startTick = dat_plot.loc[(dat_plot['time'].dt.minute == 0) | (dat_plot['time'].dt.minute == 30)].index.values[0]

    fig, ax = plt.subplots(figsize = (16, 9))

    for idx, val in dat_plot.iterrows():
        color = 'green'
        if val['open'] > val['close']:
            color = 'red'

        plt.plot([x[idx], x[idx]], [val['open'], val['close']], color = color, linewidth = 4)
        plt.plot([x[idx], x[idx]], [val['low'], val['open']], color = color)
        plt.plot([x[idx], x[idx]], [val['open'], val['high']], color = color)
    
    plt.scatter(pointX, (pointY['open']+pointY['close'])/2, s = 1000, edgecolors = 'black', facecolors = 'none')

    if vertLineStamp != None:
        plt.axvline(x = dat_plot[dat_plot['time'] == vertLineStamp].index.values[0], linestyle = '--')
   

    plt.xticks(x[startTick::xtick_iter], plot_tl[startTick::xtick_iter], rotation = 45)
    if gridOn:
        plt.grid(which = 'both')
    if minorTicksOn:
        ax.xaxis.set_minor_locator(MultipleLocator(1))
    plt.show()

def plotCandlesWithPointIndicators(data, Points, chartIndicators = None, start = 0, end = 0, xtick_iter = None, gridOn = False, minorTicksOn = True):

    #Purpose here is to show candles (OHLC) but also deal with Matplotlib 'discontinuity' of plotting over weekends
    #Former is done by just plotting O, H, L & C separately (Open-Close as a wider bar) 
    #Latter is done by setting an array for index, then splicing strings of the datetime
    
    #Inputs (below all follow similar format)
    #Data - just the dataframe to plot
    #Start - start index to plot, around 100-200 candles is best without getting to messing. E.g. do start = 100, end = 250 or so
    #xtick_iter - this is fidgety, but basically controls how many timestamps are flagged on the xaxis (xtick_iter = 4 -> 1 xaxis label per 4 bars (hourly))
    #gridOn - to put grid on
    #minorTicksOn - to put x Axis Minor ticks on.

    if start == 0 and end == 0:
        end = len(data)    

    dat_plot = data.iloc[start:end].reset_index(drop = True, inplace = False)
    x = np.arange(0, len(dat_plot))
    plot_tl = [dat_plot['time'].iloc[x].strftime('%d-%b %H:%M') for x in range(0, len(dat_plot))]

    #Costmetic adjustment - major Xticks. Plot in line with something standard (eg 15/30min/1hr)
    if xtick_iter == None:
        freqMins = (dat_plot['time'].iloc[1] - dat_plot['time'].iloc[0])/pd.Timedelta('60s')
        if freqMins == 1:
            xtick_iter = 30
        if freqMins == 5:
            xtick_iter = 6
        elif freqMins == 10:
            xtick_iter = 3
        elif freqMins == 15:
            xtick_iter = 2    

    #Start major label at 0 or 30 mins
    startTick = dat_plot.loc[(dat_plot['time'].dt.minute == 0) | (dat_plot['time'].dt.minute == 30)].index.values[0]
    
    #Assume chartIndicators is never None, otherwise use the above function
    nAxis = max(int(d['Axis']) for d in chartIndicators.values()) + 1
    #OHLC is main plot, indicators below that.
    heightRatios = [2] + [1] * (nAxis-1)
    fig, axs = plt.subplots(nAxis, 1, figsize = (16, 9), sharex = True,  gridspec_kw={'height_ratios': heightRatios})

    for idx, val in dat_plot.iterrows():
        color = 'green'
        if val['open'] > val['close']:
            color = 'red'

        axs[0].plot([x[idx], x[idx]], [val['open'], val['close']], color = color, linewidth = 4, label = '_nolegend_')
        axs[0].plot([x[idx], x[idx]], [val['low'], val['open']], color = color, label = '_nolegend_')
        axs[0].plot([x[idx], x[idx]], [val['open'], val['high']], color = color, label = '_nolegend_')
    
    axs[0].plot(Points.index.values, Points['high'], label = '_nolegend_', color = 'black')
    axs[0].plot(Points.index.values, Points['low'], label = '_nolegend_', color = 'black')
    
    axs[0].set_xticks(x[startTick::xtick_iter])
    axs[0].set_xticklabels(plot_tl[startTick::xtick_iter])
    axs[0].xaxis.set_tick_params(rotation = 45)

    if gridOn:
        plt.grid(which = 'both')
    if minorTicksOn:
        for ax in axs:
            ax.xaxis.set_minor_locator(MultipleLocator(1))        

    #Indicator plots
    for indicator in chartIndicators:
        indicatorAx = chartIndicators[indicator]['Axis']
        for column in chartIndicators[indicator]['Columns']:
            axs[indicatorAx].plot(x, dat_plot[column], label = column)
        if 'Horizontal Line' in chartIndicators[indicator]:
            for i in range(len(chartIndicators[indicator]['Horizontal Line'])):
                axs[indicatorAx].axhline(y = chartIndicators[indicator]['Horizontal Line'][i], color = 'black', linestyle = '--')

    #Legend
    for ax in axs:
        ax.legend()

    plt.show()