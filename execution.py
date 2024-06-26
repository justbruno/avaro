#!/usr/bin/env python3
from iotools import logger
import numpy as np
import datetime
import time
from conf import constants
from conf import config
import clock

class Operator:

    """
    This class offers routines for automated market operations. This
    class is not responsible for deciding when to trade. Rather, it
    receives trade orders and carries them out in a way that satisfies
    certain requisites. 
    
    The functions implemented here emit orders and track their status,
    which they report back so that filled trades can be recorded. 

    In particular, limit orders are tracked in order to know whether
    they were filled or not, and cancelled if the market moves far
    away from the desired price. 

    """
    
    def __init__(self, exchange, book_monitor):
        self.exchange = exchange
        self.book_monitor = book_monitor


    def gbp_bid(self):
        ask, bid = self.book_monitor.get_ask_bid()
        return bid

        
    def buy_limit(self, amount, price=None, expiry=9999, give_up_margin=None):
        """
        Emits a limit buy order, for the given amount in fiat currency (or pair right side, e.g. EUR for BTC-EUR) at the given price.

        If the price increases by a certain amount from the buy price, we cancel the operation and deem it unsuccessful.

        :param float amount: the amount to buy, in fiat currency
        :param float price: the price of the limit order. If None, an internal routine is run to determine the price
        :return: A tuple (success, result). If the operation was unsuccessful, success is False and result is undefined. If successful, success is True and result is a dictionary {'volume':(size in crypto), 'price':(price of executed order), 'timestamp':(approximate time of execution, estimated internally, not obtained from exchange)}.
        """

        if give_up_margin == None:
            give_up_margin = config.GIVE_UP_MARGIN
        
        # Emit the order
        try:
            if price == None:
                price = self.gbp_bid()
            size = amount/price
            size = np.around(size, decimals=8)        
            order = self.exchange.buy_limit(size, price)    
        except Exception as e:
            logger.trace(e)
            return (False, None)

        start_time = time.time()
        
        logger.trace(order)
        logger.trace('*'*50)
        s = 'BUY LIMIT ORDER - {} at {}'.format(size, price)
        logger.trace(s)

        # Next, we track the order status to determine whether it went through
        # Wait until the order goes through, or the price increases
        # too much, in which case we cancel and give up
        completed = False
        success = False

        while not completed:
            logger.trace('The operator is tracking a BUY LIMIT order')
            logger.trace(order)

            # If the order is closed, we interpret that we managed to buy
            completed = self.exchange.order_is_closed(order)

            if completed:
                order['timestamp'] = time.time()
                success = True
            else:
                clock.sleep(5)

            # If the price went up too much or the order expired...
            ask, bid = self.book_monitor.get_ask_bid()
            if not completed and (bid - price >= give_up_margin or (time.time()-start_time)/60 > expiry):
                logger.trace('Trying to cancel...')
                try:
                    r = self.exchange.cancel_order(order)
                except Exception as e:
                    logger.error('Error cancelling limit order in execution.py: {}'.format(e))
                    continue                    
                s = 'CANCEL - {}'.format(self.book_monitor.get_ask_bid()[1])
                logger.info(s)
                # The order might have been partially filled. In that case,
                # we consider the buy successful.
                partial_vol = self.exchange.get_order_filled_volume(order)
                if partial_vol > 0:
                    success = True
                    order['volume'] = partial_vol
                    order['timestamp'] = time.time()
                else:
                    success = False
                    order = None
                completed = True
                
        return success, order

                
    def buy_market(self, amount):
        try:
            buy_order_price = self.gbp_bid() # To calculate the amount in target currency
            amount = config.DEFAULT_BUY_VOL_EUR/buy_order_price
            amount = np.around(amount, decimals=8)        
            order = self.exchange.buy_market(amount)    
        except Exception as e:
            logger.trace('Error buying market in execution.py: {}'.format(e))
            return False, None
        logger.trace(order)
        logger.trace('*'*50)
        s = 'BUY MARKET ORDER - {} at {}'.format(amount, buy_order_price)
        logger.trace(s)

        order['timestamp'] = time.time()
        success = True
        return success, order
        

    def sell_limit(self, order, price=None):
        """
        Emits a limit sell order, for the given order at the given price.

        If no price is given, we set the selling price to be the current MMP.

        :param float order: an object containing information about the buy order we want to sell (e.g. we will sell the amount that was bought)
        :param float price: the price of the limit order. If None, MMP is used.
        :return: A tuple (success, price). If the operation was unsuccessful, success is False. If successful, success is True and price is as set in the sell order.
        """
        if price == None:
            price = self.book_monitor.get_mmp()
        
        amount = np.round(order['volume'], decimals=8)
        logger.trace('Selling {} at {}'.format(amount, price))

        completed = False
        success = False
        while not completed:
            try:
                r = self.exchange.sell_limit(amount, price)
                s = 'Emitted SELL ORDER - {} at {}'.format(amount, price)
                logger.info(s)
                if 'error' in r:
                    if len(r['error']) > 0:
                        completed = True
                        success = False
                    logger.error(f'ERROR placing limit order in execution.py: {r}')
                    if 'EOrder:Insufficient funds' in r['error']:
                        completed = True
                        success = False
                else:
                    completed = True
                    success = True
                    logger.info(f'Sell order successful: {r}')
                    clock.sleep(2)
            except Exception as e:
                logger.error(f'Error placing sell limit order in execution.py: {e}')
                completed = True
        logger.trace('Out of limit order loop')

        return success, price
                    

    def sell_market(self, order):
        """
        Emits a market sell order, for the given order.

        :param float order: an object containing information about the buy order we want to sell (e.g. we will sell the amount that was bought)
        :return: A tuple (success, price). If the operation was unsuccessful, success is False. If successful, success is True and price is as set in the sell order.
        """
        
        amount = np.round(order['volume'], decimals=8)
        logger.trace('Selling {}'.format(amount))

        completed = False
        success = False
        while not completed:
            try:
                r = self.exchange.sell_market(amount)
                s = 'Emitted SELL ORDER - {}'.format(amount)
                logger.info(s)
                if 'error' in r:
                    if len(r['error']) > 0:
                        completed = True
                        success = False
                    logger.error(f'ERROR placing market order in execution.py (inner): {r}')
                    if 'EOrder:Insufficient funds' in r['error']:
                        completed = True
                        success = False
                else:
                    completed = True
                    success = True
                    logger.info(f'Sell order successful: {r}')
                    clock.sleep(2)
            except Exception as e:
                logger.error(f'Error placing sell market order in execution.py (outer): {e}')
                completed = True
        logger.trace('Out of market order loop')

        ask, bid = self.book_monitor.get_ask_bid()
        price = bid
        
        return success, price
                    
    
