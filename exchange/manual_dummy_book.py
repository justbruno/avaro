#!/usr/bin/env python3

"""
Simulated book monitor base on manual input.
"""

import logger
import time
import exchange.book

MANUAL_READ_SLEEP = 1

class BookMonitor(exchange.book.BookMonitor):
    """
    This class implements a simulated order book monitor based
    on the given input file, which is mean to be manually manipulated
    in real time. The file should contain a single line, with the
    following comma-separated values:
    mid-market price, spread
    """
    def __init__(self, book_input=None):
        super().__init__()
        logger.trace('USING MANUAL DUMMY BOOK')
        logger.trace(f'input: {book_input}')
        self.running = True
        self.book_input = book_input
        
    def start(self, channel='spread'):
        self.read()

    def read(self):
        while True:
            with open(self.book_input, 'r') as f:
                s = f.readline().strip('\n').split(',')
                mmp = float(s[0])
                spread = float(s[1])
                self.best_bid = mmp-spread
                self.best_ask = mmp+spread
            time.sleep(MANUAL_READ_SLEEP)


    def is_finished(self):
        return self.finished

            
    def ping(self):
        pass


    def stop(self):
        pass
