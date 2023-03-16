#!/usr/bin/env python3
from iotools import logger

def print_asset_list(asset_manager, book_monitor):
    """
    Prints a detailed report of the asset list, including estimated gain if sold now.
    """
    bid = book_monitor.get_bid()

    asset_list = asset_manager.get_assets()

    logger.trace('Asset list ({}):'.format(len(asset_list)))
    logger.trace('Price       size        ratio   progress  gain')
    for order in asset_list:
        gain = asset_manager.compute_order_gain(order, bid)
        logger.trace('{:.4f}, {:.8f}, {:.4f}, {:.2f}, {:.2f}'.format(order['price'], order['volume'], bid/order['price'], order['progress'], gain))

    
def print_balance(exchange_interface):
    """
    Prints a report of the available balance.
    """
    balance = exchange_interface.get_balance()
    eur_balance = balance['result']['ZEUR']
    btc_balance = balance['result']['XXBT']
    pv = exchange_interface.get_trade_balance('EUR')['result']['eb']
    logger.trace(f'Balance report: EUR:{eur_balance}. BTC:{btc_balance}. Portfolio value (EUR): {pv}')

    
