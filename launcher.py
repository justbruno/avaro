#!/usr/bin/env python3

"""
Launcher script.
"""

import sys, os
import shutil
import argparse
import io_handler
import importlib

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf')
    args = parser.parse_args()

    print(f'Using configuration file: {args.conf}')

    shutil.copy(args.conf, 'conf/config.py')
    from conf import config
           
    from conf import constants
        
    import logger
    import orchestrator
        
    book = importlib.import_module(constants.EXCHANGE_DIR + '.' + config.BOOK)
    book_monitor = book.BookMonitor(**config.BOOK_PARAMS)
    exchange_interface = importlib.import_module(constants.EXCHANGE_DIR + '.' + config.EXCHANGE)

    buy_strat = importlib.import_module(constants.STRATS_DIR + '.' + config.BUY_STRAT)
    sell_strat = importlib.import_module(constants.STRATS_DIR + '.' + config.SELL_STRAT)
    
    logger.trace('Initialising trader')
    logger.trace(f'Buy strat: {config.BUY_STRAT}')
    logger.trace(f'Sell strat: {config.SELL_STRAT}')

    o = orchestrator.Orchestrator(exchange_interface=exchange_interface, book_monitor=book_monitor, buy_strat=buy_strat, sell_strat=sell_strat)
    o.run()


if __name__ == '__main__':
    main()
