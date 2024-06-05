#!/usr/bin/env python3

"""
Buy strategy.
"""
    
CONF_REFRESH_ITERATIONS = 50
BUY_SIZE_BASE = 20

import numpy as np
import time
import datetime
from iotools import logger
from iotools import io_handler
from conf import config
import clock
import strats.strat

class Strat(strats.strat.Strat):
    """
    This class implements a buy strat.

    """
    
    def __init__(self, book_monitor, asset_manager, conf_file=None):
        super().__init__()
        self.book_monitor = book_monitor
        self.asset_manager = asset_manager

        self.buy_size = BUY_SIZE_BASE

        if conf_file == None:
            self.conf_file = config.BUY_CONF
        self.conf = io_handler.load_conf(self.conf_file)
        self.rebuy_margin = self.conf['REBUY_MARGIN']
        
        self.set_buy_criteria()
        
        # When this object decides to buy, it will call the functions in this list
        self.callbacks = []

        self.verbose = False


    def set_buy_criteria(self):
        queue = self.asset_manager.get_assets()
        if len(queue) > 0:
            self.last_buy_price = self.asset_manager.get_cheapest()['price']
            self.last_buy_time = self.asset_manager.get_cheapest()['timestamp']
            self.buy_cooldown = 2**(len(queue)-1) * self.conf['BUY_COOLDOWN_BASE']
        else:
            self.last_buy_price = np.inf
            self.last_buy_time = 0
            self.buy_cooldown = 0
        
        
        
    def print_report(self):
        ask, bid = self.book_monitor.get_ask_bid()
        lapse = time.time()-self.last_buy_time
        queue = self.asset_manager.get_assets()
        logger.trace('='*50)
        logger.trace('Buy strat report')
        logger.trace(f"Margin: {self.last_buy_price-bid} ({self.rebuy_margin} required). Lapse: {lapse} ({self.buy_cooldown} required)")
        logger.trace(f"Next buy: {BUY_SIZE_BASE * 2**len(queue)}")
        logger.trace('-'*50)

            
    def run(self):        
        running = True
        counter = 0
        
        while running:            
            counter += 1
            # Print info and reload conf
            if counter % 50 == 0:
                logger.trace('/\\'*50)
                logger.trace('The buy strat is alive')
            if counter % CONF_REFRESH_ITERATIONS == 0:
                self.conf = io_handler.load_conf(self.conf_file)

            ask, bid = self.book_monitor.get_ask_bid()

            self.set_buy_criteria()
            queue = self.asset_manager.get_assets()                
            buy_size = np.min([self.conf['MAX_VOL'], BUY_SIZE_BASE * 2**len(queue)])
            self.rebuy_margin = self.conf['REBUY_MARGIN'] * 2**len(queue)
            
            if time.time()-self.last_buy_time >= self.buy_cooldown\
               and self.last_buy_price-bid >= self.rebuy_margin\
               and np.random.random() < self.conf['BUY_CHANCE']:
                logger.info(f'Triggering BUY order: {bid}')
                for callback in self.callbacks:
                    callback(amount=buy_size, price=bid)                          

            clock.sleep(self.conf['ITERATION_SLEEP'])
            clock.Clock.register_buy() # For simulation sync
                        
