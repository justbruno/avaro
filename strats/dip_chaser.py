#!/usr/bin/env python3

"""
Buy strategy.
"""
    
CONF_REFRESH_ITERATIONS = 50

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

    When the best bid in the book experiences a sudden decrease (beyond DROP_THR), a procedure is triggered. 
    A target buying price is maintained, and decreased iteratively. When the bid goes above 
    said target price, the strat decides to buy. This is meant to take advantage of dips in price.    
    """
    
    def __init__(self, book_monitor, asset_manager, conf_file=None):
        super().__init__()
        self.book_monitor = book_monitor
        self.asset_manager = asset_manager

        if conf_file == None:
            self.conf_file = config.BUY_CONF
        self.conf = io_handler.load_conf(self.conf_file)
        
        self.max_drop = 0 # Max drop observed so far
        self.drop = 0 # Current drop

        # When this object decides to buy, it will call the functions in this list
        self.callbacks = []

        self.verbose = False


    def print_report(self):
        logger.trace('='*50)
        logger.trace('Buy strat report')
        logger.trace('Drop     Max drop Drop thr.')
        logger.trace(f"{self.drop:.5f}  {self.max_drop:.5f}  {self.conf['DROP_THR']}")
        logger.trace('-'*50)

            
    def run(self):        
        running = True
        counter = 0
        alpha = 1 # For the convex combination: sell at self.ALPHA*MIN_MARGIN + (1-self.ALPHA)*MAX_MARGIN
        
        ask, bid = self.book_monitor.get_ask_bid()                
        ceiling = bid
        min_bid = bid
        buy_thr = bid
        iterations_since_update = 1
        gone_through = False
        self.max_drop = 0
        
        while running:            
            counter += 1
            # Print info and reload conf
            if counter % 50 == 0:
                logger.trace('/\\'*50)
                logger.trace('The buy strat is alive')
            if counter % CONF_REFRESH_ITERATIONS == 0:
                self.conf = io_handler.load_conf(self.conf_file)

            ask, bid = self.book_monitor.get_ask_bid()

            if bid < min_bid:
                min_bid = bid
                if gone_through:
                    ceiling = buy_thr
                iterations_since_update = 1
            if not gone_through and bid > ceiling:
                ceiling = bid 
                buy_thr = bid
                alpha = 1 # Only useful when debugging, as alpha is set to 1 when here is a dip
                iterations_since_update = 1            

            self.drop = (ceiling-bid)/bid
            if self.drop > self.max_drop:
                self.max_drop = self.drop
            dip = self.drop > self.conf['DROP_THR']
            if not gone_through and dip:
                gone_through = True
                alpha = 1
                buy_thr = ceiling
                
            # Update THR
            iterations_since_update += 1
            alpha = np.exp(-iterations_since_update*self.conf['ISU_FACTOR'])
            new_thr = alpha*ceiling + (1-alpha)*bid        
            buy_thr = np.min([buy_thr, new_thr])
            if self.verbose:
                logger.trace('='*50)
                logger.trace('Buy decision report')
                logger.trace('drop     alpha ceiling  bid      new_thr  buy_thr  self.max_drop min_bid  bthr-bid')
                logger.trace(f'{self.drop:.5f}, {alpha:.2f}, {ceiling:.1f}, {bid:.1f}, {new_thr:.1f}, {buy_thr:.1f}, {self.max_drop:.5f}, {min_bid:.1f}, {buy_thr-bid}')
                logger.trace('-'*50)
            if gone_through:
                logger.trace('Chasing the dip: {:.2f} ({:.2f}) - {}'.format(buy_thr, alpha, bid))
                if bid > buy_thr:
                    gone_through = False
                    ceiling = bid
                    min_bid = bid
                    buy_thr = bid
                    logger.info(f'Triggering BUY order: {bid}')
                    for callback in self.callbacks:
                        callback(price=buy_thr)
            else:
                ceiling = new_thr

            clock.sleep(self.conf['ITERATION_SLEEP'])
            clock.Clock.register_buy() # For simulation sync
                        
