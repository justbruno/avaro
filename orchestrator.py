#!/usr/bin/env python3

"""
Contains the Orchestrator class, which instantiates the main classes
and starts the threads required for the bot to run.

It also prints periodic reports.
"""


import os
import time, datetime
import numpy as np
import threading
from conf import constants

import execution
import sys
from iotools import logger
import assets
import dispatch
import filters
import reports
from conf import config
import clock

def book_starter(book_monitor):
    logger.trace('Thread starting...')    
    book_monitor.start()

def strat_starter(strat):
    strat.run()

class Orchestrator:    
    """
    This class creates the main objects and manages the background threads where they run.
    """    
    
    def __init__(self, exchange_interface, book_monitor, buy_strat, sell_strat):

        logger.info('Initialising Orchestrator...')

        self.book_unresponsive = 0
        
        # Exchange interface 
        self.exchange = exchange_interface.ExchangeInterface()
        # Manages the trade book stream
        self.book_monitor = book_monitor

        # Carries out buys and sells safely, to ensure we record trades locally
        self.operator = execution.Operator(self.exchange, self.book_monitor)

        # Keeps the list of crypto assets wwe have bought, including price and other information
        self.asset_manager = assets.AssetManager()

        # We put buy requests through this filter, in case we want to prevent some trades from happening
        self.op_filter = filters.Filter(book_monitor=self.book_monitor, exchange=self.exchange, asset_manager=self.asset_manager)

        # Listens to the strat for order requests, and dispatches these to the operator
        self.dispatcher = dispatch.OrderDispatcher(asset_manager=self.asset_manager, operator=self.operator, op_filter=self.op_filter)

        # Buy/sell strats. When they decide to buy/sell, they call the given callback functions
        self.buy_strat = buy_strat.Strat(self.book_monitor)
        self.buy_strat.add_callback(self.dispatcher.emit_buy)
        self.sell_strat = sell_strat.Strat(self.book_monitor, self.asset_manager)
        self.sell_strat.add_callback(self.dispatcher.emit_sell)
                

        # Start background threads
        book_thread = threading.Thread(target=book_starter, args=(self.book_monitor,))
        book_thread.start() 

        # Wait until the book monitor starts
        mmp = self.book_monitor.get_mmp()
        while mmp == 0.0:
            logger.trace('MMP is {}. Waiting for book monitor to be ready...'.format(mmp))
            clock.sleep(1)
            mmp = self.book_monitor.get_mmp()
        logger.trace('MMP is {}.'.format(mmp))

        sell_thread = threading.Thread(target=strat_starter, args=(self.sell_strat,))
        sell_thread.start() 
        buy_thread = threading.Thread(target=strat_starter, args=(self.buy_strat,))
        buy_thread.start() 

        self.asset_manager.sort_asset_list()
        
    
    def trigger(self):

        logger.trace('Reading trigger file...')
        trigger = 0
        bypass = 0
        try:
            with open('trigger.txt', 'r') as f:
                trigger = int(f.readline())
            with open('trigger.txt', 'w') as out:
                out.write('0'.format(bypass))

            logger.trace('Trigger: {}'.format(trigger))
            if trigger == 1:
                logger.trace('Trigger ON')
                return True
        except Exception as e:
            logger.error('Error while handling trigger.')

    def run(self):
        running = True
        while running:
            try:
                self.sell_strat.print_report()
                self.buy_strat.print_report()
            except Exception as e:
                logger.error('Failed to print report')
                logger.error(e)
                
            reports.print_asset_list(self.asset_manager, self.book_monitor)

                
            if self.trigger():
                self.dispatcher.emit_buy(config.DEFAULT_BUY_VOL_EUR)

            self.book_monitor.ping()

            time.sleep(config.ORCHESTRATOR_SLEEP)

            if not self.book_monitor.responsive:
                logger.info('The book is unresponsive')
                self.book_unresponsive += 1
                if self.book_unresponsive >= config.MAX_BOOK_UNRESPONSIVE:
                    running = False
                    os._exit(0)
            else:
                self.book_unresponsive = 0    

            
if __name__ == "__main__":
    o = Orchestrator()
    o.run()
