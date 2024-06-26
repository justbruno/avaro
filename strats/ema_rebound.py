#!/usr/bin/env python3

"""
Buy strategy.
"""

CONF_REFRESH_ITERATIONS = 25

import numpy as np
from iotools import logger
from iotools import io_handler
from conf import config
import clock
import strats.strat

class Strat(strats.strat.Strat):
    """
    This class implements a simple buy strat. 

    It keeps a buffer of exponential moving averages (EMAs) of the mid market price.
    When this average increases by a certain amount, the strat interprets there is positive momentum
    and a decision to buy is made.
    """
    
    def __init__(self, book_monitor, asset_manager, conf_file=None):
        super().__init__()
        self.book_monitor = book_monitor        
        if conf_file == None:
            self.conf_file = config.BUY_CONF
        self.conf = io_handler.load_conf(config.BUY_CONF)
        self.queue = [] # The buffer containing the EMAs
        
        # When this object decides to sell, it will call the functions in this list
        self.callbacks = []

            
    def print_report(self):
        logger.trace(f'Buy strat report:')
        logger.trace(f'EMA: {self.queue[-1]}')
        logger.trace(f'Momentum: {self.compute_momentum(self.queue)}')
        logger.trace(f"Threshold: {self.conf['THR']}")


    def compute_momentum(self, queue):
        return np.sum(np.diff(queue))/queue[0]
        
    def run(self):
 
        mmp = self.book_monitor.get_mmp()
        self.queue = [mmp]*self.conf['QUEUE_LENGTH']
        
        running = True
        counter=0
        watching = False
        while running:
            np.set_printoptions(precision=2, suppress=True)
            # Re-read configuration file
            counter += 1            
            if counter % CONF_REFRESH_ITERATIONS == 0:
                self.conf = io_handler.load_conf(config.BUY_CONF)

            # Compute the new EMA and add to the queue
            mmp = self.book_monitor.get_mmp()
            average = (1-self.conf['ALPHA'])*self.queue[-1] + self.conf['ALPHA']*mmp
            self.queue = self.queue[1:]
            self.queue.append(average)

            # Compute momentum to make a decision
            momentum = self.compute_momentum(self.queue)
            #logger.trace(f'MMT: {momentum}. MMP: {mmp}. Watching: {watching}')
            if momentum <= self.conf['THR']:
                watching = True
            if watching and momentum >= self.conf['REBOUND_THR']:
                for callback in self.callbacks:
                    callback(order_type='limit')
                watching = False
                # We reset the queue to avoid another trigger based on the current momentum
                self.queue = [mmp]*self.conf['QUEUE_LENGTH']
                                    
            clock.sleep(self.conf['ITERATION_SLEEP'])
            clock.Clock.register_buy() # For simulation sync
