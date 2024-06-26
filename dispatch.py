#!/usr/bin/env python3
from iotools import logger
from conf import constants
from conf import config

class OrderDispatcher:
    """
    This class listens to buy/sell orders by the strats, and requests the corresponding orders to be carried out
    by the Operator. Successful orders are sent to the AssetManager to be recorded.
    """

    def __init__(self, asset_manager, operator, op_filter):
        self.asset_manager = asset_manager
        self.operator = operator
        self.op_filter = op_filter
        

    def emit_buy(self, amount=config.DEFAULT_BUY_VOL_EUR, price=None, order_type='limit', expiry=9999, give_up_margin=None):
        logger.info("Dispatcher: emitting buy")
        conditions_met = self.op_filter.buy_filter()
        if not conditions_met:
            logger.info("Dispatcher: Conditions for buying not met. The buy is cancelled.")
            return

        if order_type == 'limit':
            success, result = self.operator.buy_limit(amount=amount, price=price, expiry=expiry, give_up_margin=give_up_margin)
        elif order_type == 'market':
            success, result = self.operator.buy_market(amount=amount)
        else:
            raise Exception(f'Unknown order type in dispatch: {order_type}')
            
        if success:
            result['progress'] = 0
            self.asset_manager.add_order(result)
            logger.info("Dispatcher: Buy successful")
            logger.trade(f"buy,{result['price']},{result['volume']}")
        else:
            logger.info("Dispatcher: Buy unsuccessful")


    
    def emit_sell(self, amount=None, price=None, order_type='limit'):
        logger.info("Dispatcher: emitting sell")
        order = self.asset_manager.get_first()        

        if order == None:
            logger.info("Dispatcher: A sell order was attempted, but no assets are currently held.")
            return
        
        if order_type == 'limit':
            success, price = self.operator.sell_limit(order, price=price)
        elif order_type == 'market':
            success, price = self.operator.sell_market(order)
        else:
            raise Exception(f'Unknown order type in dispatch: {order_type}')

        if success:
            self.asset_manager.queue_pop()
            profit = price*order['volume']*(1-constants.FEE) - order['price']*order['volume']*(1+constants.FEE)
            self.asset_manager.add_progress(profit)            
            logger.info("Dispatcher: Sell successful")
            logger.trade(f"sell,{price},{order['volume']}")
        else:
            logger.info("Dispatcher: Sell unsuccessful")

           

