#!/usr/bin/env python3

"""
Simplistic interactive trader, for illustration purposes only.

Replace the exchange module to use it for actual trading.
"""

import threading
import time
import exchange.kraken_book as book
import exchange.dummy_exchange as exchange

def book_starter(book_monitor):
    print('Thread starting...')    
    book_monitor.start()

book_monitor = book.BookMonitor()

# Start background threads
book_thread = threading.Thread(target=book_starter, args=(book_monitor,))
book_thread.start() 

exchange_interface = exchange.ExchangeInterface()

assets = []

while True:
    ask,bid = book_monitor.get_ask_bid()
    print('Assets:')
    for a in assets:
        print(a)
    print()
    print(f'Bid: {bid}')
    print(f'Ask: {ask}')
    print('Enter b to buy at current ask, s to sell last acquired asset, anything else to refresh.')
    
    k = input()
    if k == 'b':
        order = exchange_interface.buy_limit(volume=0.0001, price=ask)
        assets.append(order)
    elif k == 's':
        order = assets[-1]
        exchange_interface.sell_limit(volume=0.0001, price=ask)
        assets = assets[:-1]


