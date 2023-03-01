#!/usr/bin/env python3

"""
Sell strategy.
"""

CONF_REFRESH_ITERATIONS = 25

import numpy as np
import time
import datetime
from iotools import logger
from conf import constants
from iotools import io_handler
from conf import config
import clock
import strats.strat

class Strat(strats.strat.Strat):
    """
    This class implements a sell strat.

    When the best bid in the book exceeds some profit threshold, a procedure is triggered. 
    A target selling price is maintained, and increased iteratively. When the bid goes below 
    said target price, the strat decides to sell. This is meant to take advantage of rallies.    
    """
    
    def __init__(self, book_monitor, asset_manager, conf_file=None):
        super().__init__()
        self.book_monitor = book_monitor
        self.asset_manager = asset_manager
        self.COOLDOWN = 3
        
        if conf_file == None:
            self.conf_file = config.SELL_CONF
        self.conf = io_handler.load_conf(conf_file)


        self.sell_thr = 0
        self.floor = 0
        self.current_max = 0
        self.gone_through = False
        self.alpha = 1.
        self.iterations_since_update = 0
        self.dips = 0
        
        self.pinged = False

        # When this object decides to sell, it will call the functions in this list
        self.callbacks = []

    
    def print_report(self):

        mmp = self.book_monitor.get_mmp()
        ask, bid = self.book_monitor.get_ask_bid()

        if len(self.asset_manager.get_assets()) <= 0:
            logger.trace('No pending orders')
            BUY_PRICE = np.inf
            BREAK_EVEN_PRICE = 0
            BTC_VOL = 0
        else:
            current_order = self.asset_manager.get_first()
            # Use this variable to lower the sell threshold, depending on current progress
            thr_shave = current_order['progress']/(current_order['price']*current_order['volume'])            
            BUY_PRICE = current_order['price']
            BREAK_EVEN_PRICE = float(BUY_PRICE)*(1+2*constants.FEE-thr_shave)        
            BTC_VOL = np.round(current_order['volume'], decimals=8)
            
        logger.trace('='*50)
        logger.trace('Sell decision report:')
        logger.trace('MMP: {}'.format(mmp))
        logger.trace('BID: {}'.format(bid))
        logger.trace('MAX: {}'.format(self.current_max))        
        logger.trace(f'If buying now, BEP would be {bid*(1+2*constants.FEE):.2f}')
        if len(self.asset_manager.get_assets()) > 0:        
            logger.trace('Looking to sell {} BTC bought at {}'.format(BTC_VOL, BUY_PRICE))
            logger.trace('BEP (margin): {} ({})'.format(BREAK_EVEN_PRICE, self.conf['MARGIN']))
            logger.trace('SELL_THR: {} ({})'.format(self.sell_thr, self.sell_thr/BUY_PRICE))
        logger.trace('-'*50)

        
        if not self.pinged:
            self.book_monitor.ping()
            self.pinged = True


    def reset(self):
        self.gone_through = False
        self.alpha = 1.
        self.current_max = 0
        self.floor = 0
        self.sell_thr = 0
        self.dips = 0


    def reset_max(self):
        self.current_max = 0

        
    def update_chaser(self):
        """
        We have a floor price, starting at BEP. When price goes up, 
        we start slowly increasing alpha to approach bid. Order thr
        is alpha*floor + (1-alpha)*bid.
        Each iteration, alpha decreases by a small amount, down to a min of 0.
        Each time bid goes up, alpha goes back to 0.
        """

        queue = self.asset_manager.get_assets()       
        if len(queue) <= 0:
            return

        # Get order info
        current_order = self.asset_manager.get_first()
        # Use this variable to lower the sell threshold, depending on current progress
        thr_shave = current_order['progress']/(current_order['price']*current_order['volume'])
        BUY_PRICE = current_order['price']
        trigger_price = float(BUY_PRICE)*(self.conf['PROFIT_THR']-thr_shave)
        BTC_VOL = np.round(current_order['volume'], decimals=8)
        self.floor = np.max([self.floor, trigger_price])

        bid = self.book_monitor.get_bid()
        # Check if we have already gone through
        if bid > trigger_price + self.conf['MARGIN']:
            if not self.gone_through: # If it's the first time, mark the timestamp
                gone_through_time = time.time()
                logger.trace('Went through  for the first time')
                self.sell_thr = trigger_price
                self.floor = trigger_price
                self.current_max = 0
                
            self.gone_through = True
        
        # Update THR
        if self.gone_through:
            logger.trace('Chasing the rally. Sell price: {:.2f}. Alpha: {:.2f}. Bid:{}. Ratio: {}'.format(self.sell_thr, self.alpha, bid, self.sell_thr/BUY_PRICE))
            self.iterations_since_update += 1
            self.alpha = np.exp(-self.iterations_since_update*self.conf['ISU_FACTOR'])
            new_thr = self.alpha*self.floor + (1-self.alpha)*bid        
            self.sell_thr = np.max([self.sell_thr, new_thr])
        else:
            self.sell_thr = trigger_price#current_order['price']*self.conf['PROFIT_THR']
            
        # Reset increase rate when a new max is reached
        if bid > self.current_max:
            logger.trace('Bid > MAX ({} > {})'.format(bid, self.current_max))
            self.current_max = bid        
            self.alpha = 1.
            #trigger_price = float(BUY_PRICE)*(self.conf['PROFIT_THR']-thr_shave)
            #self.sell_thr = 0
            self.floor = self.sell_thr
            self.iterations_since_update = 0
            self.dips = 0
            logger.trace('FLOOR: {}'.format(self.floor))

        # Check if the bid price dips below our current sell threshold
        if bid < self.sell_thr and self.gone_through:
            self.dips += 1
            logger.trace('Dips: {}'.format(self.dips))
            if self.dips >= self.conf['DIP_LIMIT']: # To prevent a momentary dip from triggering a release
                logger.info('The sell decider triggered a sell')
                for callback in self.callbacks:
                    callback(price=self.sell_thr)
                self.reset()
        else:
            self.dips = 0


    def run(self):        
        self.alpha = 1 # For the convex combination: sell at self.alpha*MIN_MARGIN + (1-self.alpha)*MAX_MARGIN
        self.current_max = 0
        self.sell_thr = 0
        running = True
        counter=0
        while running:
            counter += 1
            if counter % CONF_REFRESH_ITERATIONS == 0:
                self.conf = io_handler.load_conf(self.conf_file)
            if len(self.asset_manager.get_assets()) <= 0:
                #logger.trace('WL waiting for an order...')
                clock.sleep(5)
            #if counter % 50 == 0:
            #    logger.trace('/\\'*50)
            #    logger.trace('The sell strat is alive')

            self.update_chaser()

            clock.sleep(self.conf['ITERATION_SLEEP'])
            clock.Clock.register_sell() # For simulation sync
            

        
