#!/usr/bin/env python3

"""
Simulated book monitor base on data dump.
"""

from iotools import logger
import time, datetime
import numpy as np
import sys
import pickle
import clock
import exchange.book

class BookMonitor(exchange.book.BookMonitor):
    """
    This class implements a simulated order book monitor based
    on the given input file, which should contain an order book dump
    in the following format: each line should contain these comma-separated values:
    best_bid, best_ask, timestamp, bid volume, ask volume.

    This class is by default synchronized with the strats (see the clock module),
    but this can be turned off by passing sync=False to the constructor.
    """
    def __init__(self, book_input=None, sync=False):
        super().__init__()
        logger.trace('USING DUMMY BOOK')
        logger.trace(f'input: {book_input}')
        self.running = True
        self.book_input = book_input
        self.finished = False
        self.sync = sync
        
    def start(self, channel='spread'):
        self.read()


    def process_line(self, l):
        s = l.strip('\n').split(',')
        return s

    def read(self):
        # We read the data into memory for faster iteration
        events = []
        with open(self.book_input, 'r') as f:
            s = self.process_line(f.readline())
            for l in f:
                try:
                    s = l.strip('\n').split(',')
                    events.append(s)
                except Exception as e:
                    logger.error(f'Error reading book dump: {e}. \nLine: {s}')

        self.best_bid = float(events[0][0])
        self.best_ask = float(events[0][1])
        last_ts = float(events[0][2])

        # Iterate over all events and update attributes accordingly
        count = 0
        for s in events:
            try:
                if self.sync: # In sync mode, we wait for the strats to iterate
                    clock.Clock.book_lock()
                else: 
                    ts = float(s[2])                    
                    clock.sleep(np.max([0,ts-last_ts]))
                    last_ts = ts

                self.best_bid = float(s[0])
                self.best_ask = float(s[1])
                count += 1
                if count % 1000 == 0:
                    logger.info(count)
            except Exception as e:
                print('Error in dummy book', e)
                
        logger.info('Finished reading dump')
        self.finished = True
    

    def is_finished(self):
        return self.finished
            
    def ping(self):
        pass

    def stop(self):
        pass
