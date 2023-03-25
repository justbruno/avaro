#!/usr/bin/env python3

import sys
sys.path.insert(0,'/home/b/git/avaro')
from exchange import kraken_interface as exchange_interface
import numpy as np


from statsmodels.tsa.stattools import pacf

e = exchange_interface.ExchangeInterface()
candles = e.get_candles()['result']['XXBTZEUR']

close = np.array([float(i[4]) for i in candles])
print(pacf(close, nlags=60))

