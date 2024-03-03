#!/usr/bin/env python3

"""
"""

MAX_DATA = 720

import threading
import time
import exchange.kraken_interface as exchange
import numpy as np
import matplotlib.pyplot as plt

plt.ion()

def get_regression_coefficients(data):
    y = data-np.mean(data)
    x = np.arange(len(data)).reshape((len(data),1))
    X = np.hstack([x, np.ones((len(data),1))])
    return np.linalg.pinv(X).dot(y)
    
def plot_regression_line(data, ax):
    coeff, bias = get_regression_coefficients(data)
    ldata = len(data)
    print(f"Regression coefficient {ldata}: {coeff}")
    reg_line = coeff*np.arange(ldata)+bias
    x = np.arange(ldata)
    ax.plot(x+MAX_DATA-ldata, reg_line+np.mean(data))

def get_extrema(data):
    length = 12
    maxs, mins = [], []
    for i in range(length):
        lower = int(i/length*len(data))
        upper = int((i+1)/length*len(data))
        maxs.append(np.max(data[lower:upper]))
        mins.append(np.min(data[lower:upper]))
    return maxs, mins
        
exchange_interface = exchange.ExchangeInterface()

while(True):    
    candles = exchange_interface.get_candles()['result']['XXBTZEUR']
    all_close = [float(x[4]) for x in candles]

    f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

    f.canvas.set_window_title('avaro Analysis')
    
    ax1.set_ylim(np.min(all_close)/1.001, np.max(all_close)*1.001)
    ax1.plot(all_close)

    plot_regression_line(all_close, ax1)
    plot_regression_line(all_close[-int(len(all_close)/2):], ax1)
    plot_regression_line(all_close[-int(len(all_close)/4):], ax1)

    maxs, mins = get_extrema(all_close)
    print(maxs)
    print(mins)
    ax2.plot(maxs, label="max")
    ax2.plot(mins, label="min")
    ax2.legend()
    
    
    plt.show(block=False)
    plt.pause(59)
    time.sleep(60)
    plt.close()

    
