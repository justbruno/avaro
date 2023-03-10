#!/usr/bin/env python3

"""
Kraken exchange interface.
"""

API_KEY_FILE = '/kk/ak.txt'
API_SECRET_FILE = '/kk/pk.txt'

import sys
import platform
import time
import base64
import hashlib
import hmac
import json
import numpy as np
from iotools import logger

from pathlib import Path
HOMEDIR = str(Path.home())

if int(platform.python_version_tuple()[0]) > 2:
    import urllib.request as urllib2
else:
    import urllib2

api_domain = "https://api.kraken.com"

def round_price(price):
    return np.around(price, decimals=1)

class ExchangeInterface:
    def sell_limit(self, volume, price):
        pass

    def buy_limit(self, volume, price):
        pass

    def sell_stop_limit(self, volume, price, stop):
        pass

    def buy_stop_limit(self, volume, price, stop):
        pass

    def sell_market(self, volume):
        pass

    def buy_market(self, volume):
        pass
        return order


    def get_open_orders(self):
        pass

    def get_closed_orders(self, count=1):
        pass
    
    def query_orders(self, txid):
        pass

    def order_is_closed(self, order):
        pass
                    
    def get_order_id_from_response(self, response):
        pass

    def get_order_from_id(self, txid):
        pass

    def cancel_order(self, order):
        pass
    
    def get_trade_balance(self, asset):
        pass
    
    def get_balance(self):
        pass
    
    def get_BTC_balance(self):
        pass
                
    def get_spread(self):
        pass
    def get_candles(self, granularity=1):
        pass

    def get_trades(self, since=0):
        pass
        
        
