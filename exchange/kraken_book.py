#!/usr/bin/env python3

"""
Kraken order book monitoring tools.
"""

from kraken_wsclient_py import kraken_wsclient_py as client
import time, datetime
import numpy as np
import sys
import pickle
import json
import exchange.book

def rfloat(s, decimals=2):
    return np.around(float(s), decimals=decimals)

class BookMonitor(exchange.book.BookMonitor):
    """
    This class monitors the Kraken order book. To use it, run 
    BookMonitor.start in its own thread.
    """
    
    def __init__(self):
        super().__init__()
        self.best_ask = 0.
        self.best_bid = 0.       
        self.bids = []
        self.asks = []
        self.running = True
        self.ws = None
        self.channel_id = None
        self.ping_id = 0
        self.responsive = True
        
        # The book monitor will call these functions when it receives a message,
        # passing the message as argument.
        self.callbacks = []

        self.started = False
        

    def add_callback(self, f):
        self.callbacks.append(f)


    def on_message(self, message):
        self.responsive = True
        for callback in self.callbacks:
            callback(message)                    

        try: 
            # TODO ChannelID is deprecated. Remove if safe
            if 'channelID' in message:
                self.channel_id = message['channelID']
                #print('Set channel ID:{}'.format(self.channel_id))

            if self.channel_id in message:
                data = message[1]
                self.best_bid = rfloat(data[0])
                self.best_ask = rfloat(data[1])

        except:
            pass


    def start(self, channel='spread'):
        print('Trying to start book')
        if not self.started:
            print('Starting book')
            self.ws = client.WssClient()
            self.ws.start()

            self.ws.subscribe_public(
                subscription = {
                    'name': channel
                },
                pair = ['XBT/EUR'],
                callback = self.on_message
            )
            self.started = True


    def ping(self):
        self.responsive = False
        self.ping_id += 1        
        request = {
            'event': 'ping',
            'reqid': self.ping_id
        }
        callback = self.pong_handler        
        payload = json.dumps(request, ensure_ascii=False).encode('utf8')
        
        id_ = 'ping'+str(self.ping_id)
        self.ws._start_socket(id_, payload, callback, private=True)
        self.ws.stop_socket(id_)


    def pong_handler(self, message):
        self.responsive = True
        #print(message)


    def stop(self):
        self.ws.stop()
        self.ws.close()

        
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

    def wait_till_ready(self):
        mmp = self.get_mmp()
        while mmp == 0.0:
            time.sleep(1)
            mmp = self.get_mmp()
    
