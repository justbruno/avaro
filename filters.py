#!/usr/bin/env python3
import time
import numpy as np
from conf import constants
from iotools import logger
from conf import config
from iotools import io_handler

class Filter:
    """
    This class implements trade decision filters, to override the decisions made by the strats.
    """
    
    def __init__(self, book_monitor, exchange, asset_manager):
        self.book_monitor = book_monitor
        self.exchange = exchange
        self.asset_manager = asset_manager
        
    
    def buy_filter(self):
        """
        This function checks if certain conditions are met, so that we can control when assets are bought.
        
        Returns True if the filter is passed (i.e. we're good to buy), False otherwise.
        """

        conf = io_handler.load_conf(config.FILTER_CONF)       
        
        if conf['BYPASS']:
            return True
        if conf['BLOCK']:
            return False

        funds = self.exchange.get_balance('EUR')
        #funds = float(r['result']['ZEUR']) #

        # For margin from last buy
        queue = self.asset_manager.get_assets()
        if len(queue) > 0:
            last_buy_price = self.asset_manager.get_first()['price']
            last_buy_time = self.asset_manager.get_first()['timestamp']
            BUY_COOLDOWN = 2**(len(queue)-1) * conf['BUY_COOLDOWN_BASE']
        else:
            last_buy_price = np.inf
            last_buy_time = 0
            BUY_COOLDOWN = 0

        buy_price = self.book_monitor.get_bid()

        logger.trace('='*50)
        logger.trace('Checking conditions for buy')
        logger.trace(f'Funds: {funds}. Required: {config.DEFAULT_BUY_VOL_EUR}')
        logger.trace(f'Elapsed since last buy: {time.time()-last_buy_time}. Required: {BUY_COOLDOWN}')
        logger.trace(f"Margin from last buy (*): {last_buy_price-buy_price}. Required: {conf['REBUY_MARGIN']}")    
        logger.trace(f"Queue length: {len(queue)}. Required: {conf['AUTO_BUYS']}")    
        logger.trace('-'*20)
        logger.trace()

        return funds >= config.DEFAULT_BUY_VOL_EUR \
            and time.time()-last_buy_time >= BUY_COOLDOWN \
            and last_buy_price-buy_price >= conf['REBUY_MARGIN'] \
            and len(queue) < conf['AUTO_BUYS'] \
            #and np.random.random() < 1/(1.5**len(queue))

