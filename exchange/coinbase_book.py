#!/usr/bin/env python3

"""
Coinbase order book monitoring tools.
"""
URL = "wss://ws-feed.pro.coinbase.com"

import sys
import pickle
import json
import exchange.book
from iotools import logger
import websocket

import requests
import time, datetime
import numpy as np
import sys
import pickle
from requests.adapters import HTTPAdapter

def remove_key(d, key):
    r = dict(d)
    del r[key]
    return r

def rfloat(s, decimals=4):
    return np.around(float(s), decimals=decimals)

class BookMonitor(exchange.book.BookMonitor):
    """
    This class monitors the Coinbase order book. To use it, run 
    BookMonitor.start in its own thread.
    """
    
    def __init__(self, market='BTC-EUR'):
        self.market = market
        super().__init__()
        self.best_ask = 0.
        self.best_bid = 0.       
        self.bids = []
        self.asks = []
        self.running = True
        self.ping_id = 0
        self.responsive = True
        
        # The book monitor will call these functions when it receives a message,
        # passing the message as argument.
        self.callbacks = []

        self.started = False
        

    def add_callback(self, f):
        self.callbacks.append(f)


    def on_open(self, socket):
        params = {
            "type": "subscribe",
            #"channels": [{"name": "ticker", "product_ids": ["BTC-EUR"]},{"name": "level2", "product_ids": ["BTC-EUR"]}]
            "channels": [{"name": "ticker", "product_ids": [self.market]},{"name": "level2", "product_ids": [self.market]}]
        }
        socket.send(json.dumps(params))

        
        

    def on_message(self, _, message):
        self.responsive = True
        for callback in self.callbacks:
            callback(message)                    

        data = json.loads(message)

        if data['type'] == 'snapshot':
            self.bids = {rfloat(i[0]):float(i[1]) for i in data['bids']}
            self.asks = {rfloat(i[0]):float(i[1]) for i in data['asks']}
        elif data['type'] == 'l2update':
            #print('MMP: {:<10} {}'.format(rfloat(self.get_mmp(), decimals=3), rfloat(self.get_spread())))
            for i in data['changes']:
                if i[0] == 'buy':
                    self.bids[rfloat(i[1])] = float(i[2])
                elif i[0] == 'sell':
                    self.asks[rfloat(i[1])] = float(i[2])
            self.clean_up()
            self.best_ask = min(self.asks.keys())
            self.best_bid = max(self.bids.keys())            


    def on_error(self, socket, error):
        logger.error(f'Socket error: {error}')

            
    def start(self, channel='spread'):

        #self.ws = websocket.WebSocketApp(URL, on_open=on_open, on_message=on_message, on_error=on_error)
        websocket.enableTrace(True)

        self.ws = websocket.WebSocketApp(URL, on_open=lambda ws: self.on_open(ws), on_message=lambda ws, msg: self.on_message(ws, msg), on_error=lambda ws,error: self.on_error(ws, error))

        logger.trace('Starting...')
        while self.running:
            retval = self.ws.run_forever()
            #print('='*50)
            logger.trace('WS released control. Return value: {}'.format(retval))
            time.sleep(1)


    def stop(self):
        self.running=False
        self.ws.close()

        
    def ping(self):
        # TODO
        self.responsive = False

    

    def clean_up(self):
        to_remove = []
        for i in self.asks:
            if self.asks[i] == 0:
                to_remove.append(i)
        for i in to_remove:
            self.asks = remove_key(self.asks, i)

        to_remove = []
        for i in self.bids:
            if self.bids[i] == 0:
                to_remove.append(i)
        for i in to_remove:
            self.bids = remove_key(self.bids, i)

