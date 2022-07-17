import matplotlib.pyplot as plt
import os
import numpy as np

class visualise:

    def __init__(self,data):
        self.data = data

        # Chart look and feel
        self.line_color = 'blue'
        self.buy_marker = '^'
        self.sell_marker = 'v'
        self.hold_marker = 'None'
        self.buy_marker_color = 'green'
        self.sell_marker_color = 'red'
        self.hold_marker_color = 'grey'
        self.marker_size = 9
        
        
        
        arr_action = []
        arr_action.extend(data['action'])
        self.arr_open = []
        self.arr_open.extend(data['open'])
        self.arr_close = []
        self.arr_close.extend(data['close'])
        self.series_dates = data['time']
        self.arr_buy =[]
        self.arr_sell = []
        self.arr_hold = []
        for i in range(len(self.arr_close)):
            if arr_action[i] == "buy" or arr_action[i] == "close short":
                self.arr_buy.append((i, self.arr_close[i]))
            elif arr_action[i] == "short" or arr_action[i] == "close long":
                
                self.arr_sell.append((i, self.arr_close[i]))
            elif arr_action[i] == "hold":
                self.arr_hold.append((i, self.arr_close[i]))
            #else:
            #    print("Unrecognised Action!!")

    def plotFig(self, image_filename_path = None, show_plot = True):
        if not self.arr_sell or not self.arr_buy or not self.arr_hold:
            print("Insufficient trades to plot")
        else:
            plt.plot(self.arr_close,color=self.line_color,marker='None')
            x,y = zip(*self.arr_buy)
            plt.plot(x, y,markerfacecolor=self.buy_marker_color, linestyle='None',marker=self.buy_marker, markersize=self.marker_size,markeredgecolor=self.buy_marker_color)
            x,y = zip(*self.arr_sell)
            plt.plot(x, y, markerfacecolor=self.sell_marker_color,linestyle='None', marker=self.sell_marker, markersize=self.marker_size,markeredgecolor=self.sell_marker_color)
            x,y = zip(*self.arr_hold)
            plt.plot(x, y, markerfacecolor=self.hold_marker_color,linestyle='None', marker=self.hold_marker, markersize=self.marker_size,markeredgecolor=self.hold_marker_color)

            x_range = np.arange(0, len(self.arr_close))
            plot_tl = [str(self.series_dates.dt.date.iloc[x]) + " " + str(self.series_dates.dt.time.iloc[x]) for x in range(0, len(self.series_dates))]
            xtick_iter = round(len(self.series_dates)/10)
            plt.xticks(x_range[::xtick_iter], plot_tl[::xtick_iter], rotation = 30)

            if image_filename_path != None:
                plt.savefig(image_filename_path, bbox_inches = 'tight') #Save before plotting
            if show_plot:
                plt.show()