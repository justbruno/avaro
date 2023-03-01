#!/usr/bin/env python3

"""
Order book monitor interface.
"""

import numpy as np
import sys
import pickle
import json

def rfloat(s, decimals=2):
    return np.around(float(s), decimals=decimals)

class BookMonitor:
    """
    This class provides an interface and basic functions for order book monitors.
    """
    
    def __init__(self):
        self.best_ask = 0.
        self.best_bid = 0.       
        self.bids = []
        self.asks = []

        # The book monitor will call these functions when it receives a message,
        # passing the message as argument.
        self.callbacks = []
        
        self.responsive = True

    def add_callback(self, f):
        self.callbacks.append(f)

       
    def get_mmp(self):
        return np.mean([self.best_ask, self.best_bid])

    def get_ask_bid(self):
        return self.best_ask, self.best_bid

    def get_ask(self):
        return self.best_ask

    def get_bid(self):
        return self.best_bid

    def get_spread(self):
        return np.abs(self.best_ask-self.best_bid)
