0#!/usr/bin/env python3

"""
Reads data from an order book monitor and dumps it in a file.
"""

import sys
sys.path.append(r'conf')
import threading
from iotools import logger
import time
import exchange.kraken_book as book

from pathlib import Path
HOMEDIR = str(Path.home())

OUTPUT_FILE = HOMEDIR + '/data/btc/kraken_book_dump_15.txt'

def book_starter(book_monitor):
    logger.trace('Thread starting...')    
    book_monitor.start() # Pass channel='book' to this call to get the complete order book. By default, it's just best bid/ask.


def dump_message(s):
    if 'spread' not in s:
        return

    data = ','.join(s[1])
    with open (OUTPUT_FILE, 'a') as out:
        out.write(f'{data}\n')

book_monitor = book.BookMonitor()

book_monitor.add_callback(dump_message)

# Start background threads
book_thread = threading.Thread(target=book_starter, args=(book_monitor,))
book_thread.start() 


while True:
    time.sleep(1)
