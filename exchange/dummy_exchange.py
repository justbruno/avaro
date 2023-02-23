#!/usr/bin/env python3

"""
Dummy exchange interface for simulation.
"""

import sys
import platform
import time
import base64
import hashlib
import hmac
import json
import numpy as np
import logger

from pathlib import Path
HOMEDIR = str(Path.home())

if int(platform.python_version_tuple()[0]) > 2:
    import urllib.request as urllib2
else:
    import urllib2



    
DEBUG = 0
LOG = 0

api_domain = "https://api.kraken.com"

def round_price(price):
    return np.around(price, decimals=1)

class ExchangeInterface:
    def __init__(self):
        logger.trace('USING DUMMY EXCHANGE')
        self.nonce = 1
        self.handled_orders = 0
        self.orders = {}
        
    
    def sell_limit(self, volume, price):
        txid = self.handled_orders
        self.handled_orders += 1
        result = {'result': {'txid': [txid], 'descr': {'order': 'sell 0.00100000 XBTEUR @ limit 200000.0'}}, 'status':'closed', 'vol':volume, 'price':price}
        self.orders[txid] = result
        return result


    def buy_limit(self, volume, price):
        price = round_price(price)
        txid = self.handled_orders
        self.handled_orders += 1
        result = {'txid': txid, 'volume':volume, 'price':price}
        self.orders[txid] = result
        return result

    # We do not simulate market orders any differently, for simplicity
    def sell_market(self, volume):
        result = self.sell_limit(volume, 0)
               
    def buy_market(self, volume):
        result = self.buy_limit(volume, 0)
               

    def query_orders(self, txid):
        return self.orders
    

    def cancel_order(self, order):
        return self.orders[order['txid']]


    def get_balance(self):
        return {'error': [], 'result': {'ZEUR': '133.4307', 'XXBT': '0.0015374800'}}


    def get_BTC_balance(self):
        return 0.0015374800

    
    def order_is_closed(self, order):
        return True
            
