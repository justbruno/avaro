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
    Dummy strat for testing
    """
    
    def __init__(self, book_monitor, asset_manager, conf_file=None):
        super().__init__()
        self.callbacks = []
        self.verbose = False        
        if conf_file == None:
            self.conf_file = config.BUY_CONF
        self.conf = io_handler.load_conf(self.conf_file)

    def print_report(self):
        pass
    
    def run(self):        
        running = True
        counter = 0
        
        while running:            
            clock.sleep(self.conf['ITERATION_SLEEP'])
            clock.Clock.register_buy() # For simulation sync
                        
