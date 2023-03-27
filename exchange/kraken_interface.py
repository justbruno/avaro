#!/usr/bin/env python3

"""
Kraken exchange interface.
"""

API_KEY_FILE = '/kk/ak.txt'
API_SECRET_FILE = '/kk/pk.txt'

ASSET_NAME_MAP = {'EUR':'ZEUR', 'BTC':'XXBT'}

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
    def __init__(self):
        self.nonce = 1
        self.api_rate_counter = 0
        
    def decrease_rate_counter(self):
        '''
        Resets the rate limit counter as per Kraken rules https://support.kraken.com/hc/en-us/articles/206548367-What-are-the-API-rate-limits-
        This is meant to be run in a thread, and will give a pessimistic estimate, because the decrease happens only when the 
        thread gets a CPU slice.
        '''
        while True:
            self.api_rate_counter -= .33
            self.api_rate_counter = np.max([self.api_rate_counter, 0])
            time.sleep(1)
        
    def increase_nonce(self):
        self.nonce += 1
        
    def private_request(self, api_method, api_data):
        api_path = "/0/private/"
        api_nonce = str(int(time.time()*self.nonce*1000))
        try:
            api_key = open(HOMEDIR + API_KEY_FILE).read().strip()
            api_secret = base64.b64decode(open(HOMEDIR + API_SECRET_FILE).read().strip())
        except:
            logger.exchange_trace("API public key and API private (secret) key must be in text files called API_Public_Key and API_Private_Key")
            sys.exit(1)
        api_postdata = api_data + "&nonce=" + api_nonce
        api_postdata = api_postdata.encode('utf-8')
        api_sha256 = hashlib.sha256(api_nonce.encode('utf-8') + api_postdata).digest()
        api_hmacsha512 = hmac.new(api_secret, api_path.encode('utf-8') + api_method.encode('utf-8') + api_sha256, hashlib.sha512)
        api_request = urllib2.Request(api_domain + api_path + api_method, api_postdata)
        api_request.add_header("API-Key", api_key)
        api_request.add_header("API-Sign", base64.b64encode(api_hmacsha512.digest()))
        api_request.add_header("User-Agent", "Kraken REST API - %s" % sys.argv[0])

        api_reply=None
        success = False
        while not success:
            try:
                api_reply = urllib2.urlopen(api_request).read().decode()
                success = True
            except Exception as error:
                logger.exchange_trace("API call failed (%s)" % error)
                success = False
                time.sleep(3)

        # TODO Certain requests increase by 2. Do we want to take them into account?
        self.api_rate_counter += 1
        return json.loads(api_reply)


    def public_request(self, api_method, api_data):
        logger.exchange_trace('Kraken interface public request')
        logger.exchange_trace('api_method: {}'.format(api_method))
        logger.exchange_trace('api_data: {}'.format(api_data))
        api_path = "/0/public/"
        api_request = urllib2.Request(api_domain + api_path + api_method + '?' + api_data)

        logger.exchange_trace('Made request')
        logger.exchange_trace('Opening url...')
        api_reply=None
        try:
            api_reply = urllib2.urlopen(api_request).read().decode()
        except Exception as error:
            logger.exchange_trace("API call failed (%s)" % error)

        logger.exchange_trace('Done')
        return json.loads(api_reply)


    
    def sell_limit(self, volume, price):
        price = round_price(price)
        logger.trace('SELL LIMIT: {}, {}'.format(volume, price))
        method="AddOrder"        
        data="pair=xxbtzeur&type=sell&ordertype=limit&volume={}&price={}".format(volume, price)
        r = self.private_request(method, data)
        if len(r['error']) > 0:
            raise Exception(f"The exchange returned an error after trying to place a limit sell order: {r['error']}")
        txid = r['result']['txid'][0]        
        order = {'volume':volume,
                  'price':price,
                 'txid':txid}
        return order


    def buy_limit(self, volume, price):
        price = round_price(price)
        logger.trace('BUY LIMIT: {}, {}'.format(volume, price))
        method="AddOrder"        
        data="pair=xxbtzeur&type=buy&ordertype=limit&volume={}&price={}".format(volume, price)
        r = self.private_request(method, data)
        if len(r['error']) > 0:
            raise Exception(f"The exchange returned an error after trying to place a limit buy order: {r['error']}")
        logger.trace("in buy_limit")
        logger.trace(r)
        txid = r['result']['txid'][0]        
        order = {'volume':volume,
                  'price':price,
                 'txid':txid}
        return order
              

    def sell_stop_limit(self, volume, price, stop):
        price = round_price(price)
        stop = round_price(stop)
        logger.trace('SELL STOP: {}, {}, {}'.format(volume, price, stop))
        method="AddOrder"        
        data="pair=xxbtzeur&type=sell&ordertype=stop-loss-limit&volume={}&price={}&price2={}".format(volume, stop, price)
        r = self.private_request(method, data)
        if len(r['error']) > 0:
            raise Exception(f"The exchange returned an error after trying to place a stop loss limit sell order: {r['error']}")
        txid = r['result']['txid'][0]        
        order = {'volume':volume,
                  'price':price,
                 'txid':txid}
        return order


    def buy_stop_limit(self, volume, price, stop):
        price = round_price(price)
        stop = round_price(stop)
        logger.trace('BUY STOP: {}, {}'.format(volume, price, stop))
        method="AddOrder"        
        data="pair=xxbtzeur&type=buy&ordertype=stop-loss-limit&volume={}&price={}&price2={}".format(volume, stop, price)
        r = self.private_request(method, data)
        if len(r['error']) > 0:
            raise Exception(f"The exchange returned an error after trying to place a stop loss limit buy order: {r['error']}")
        txid = r['result']['txid'][0]        
        order = {'volume':volume,
                  'price':price,
                 'txid':txid}
        return order
               

    def sell_market(self, volume):
        logger.trace('SELL MARKET: {}'.format(volume))
        method="AddOrder"        
        data="pair=xxbtzeur&type=sell&ordertype=market&volume={}".format(volume)
        r = self.private_request(method, data)
        if len(r['error']) > 0:
            raise Exception(f"The exchange returned an error after trying to place a market sell order: {r['error']}")
        txid = r['result']['txid'][0]        
        order = {'volume':volume,
                  'price':price,
                 'txid':txid}
        return order


    def buy_market(self, volume):
        logger.trace('BUY MARKET: {}'.format(volume))
        method="AddOrder"        
        data="pair=xxbtzeur&type=buy&ordertype=market&volume={}".format(volume)
        r = self.private_request(method, data)
        if len(r['error']) > 0:
            raise Exception(f"The exchange returned an error after trying to place a market buy order: {r['error']}")
        txid = r['result']['txid'][0]        
        order = {'volume':volume,
                  'price':price,
                 'txid':txid}

        return order


    def get_open_orders(self):
        method="OpenOrders"
        data="trades=True"
        r = self.private_request(method, data)
        return r['result']['open']
    

    def get_closed_orders(self, count=1):
        """
        Retrieves closed orders.
        count: how many batches to request. The Kraken API returns 50 trades per request.
        """
        method="TradesHistory"
        orders = {}
        for i in range(count):            
            data="trades=false&ofs={}".format(i)
            r = self.private_request(method, data)
            logger.trace(r)
            logger.trace(i)
            orders = dict(orders, **r['result']["trades"])
            time.sleep(10)
        return orders

    def query_orders(self, txid):
        method="QueryOrders"
        data="trades=true&txid={}".format(txid)
        r = self.private_request(method, data)
        return r['result']


    
    def order_is_closed(self, order):
        try:
            txid = order['txid']
            r = self.query_orders(txid)
            if r[txid]['status'] == 'closed':
                return True
        except Exception as e:
            logger.error(f'Error querying orders: {e}')
            return False
            
        

    def get_order_id_from_response(self, response):
        return response['result']['txid'][0]        


    def get_order_from_id(self, txid):
        r = self.query_orders(txid) 
        order = r[txid]
        result = {'volume':float(order['vol']),
                  'price':np.around(float(order['price']), decimals=1),
                  'txid':txid}                
        return result


    def cancel_order(self, order):
        txid = order['txid']
        logger.trace('CANCEL ORDER: {}'.format(txid))

        method="CancelOrder"
        data="txid={}".format(txid)
        r = self.private_request(method, data)
            
        return r

    
    def get_trade_balance(self, asset):
        method="TradeBalance"
        data="asset={}".format(asset)
        r = self.private_request(method, data)
        return r['result']['eb']

    
    def get_balance(self, asset):
        method="Balance"
        data=""
        r = self.private_request(method, data)['result']
        asset = ASSET_NAME_MAP[asset]
        if asset in r:
            return float(r[asset])
        return r

                
    def get_spread(self):
        method = "Spread"
        data="pair=XXBTZEUR"
        r = self.public_request(method, data)
        return r

    def get_candles(self, granularity=1):
        method = "OHLC"
        data="pair=XXBTZEUR&interval={}".format(granularity)
        r = self.public_request(method, data)
        return r
        

    def get_trades(self, since=0):
        method = "Trades"
        data="pair=XXBTZEUR&since={}".format(since)
        r = self.public_request(method, data)
        return r
        
        
        
