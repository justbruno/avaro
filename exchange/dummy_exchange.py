#!/usr/bin/env python3

"""
Dummy exchange interface for simulation.
"""

from exchange import master_exchange

class ExchangeInterface(master_exchange.MasterExchange):
    def __init__(self, conf=None):
        super(ExchangeInterface, self).__init__()
        print('USING DUMMY EXCHANGE')
        self.nonce = 1
        self.handled_orders = 0
        self.orders = {}
        self.eur_balance=1000.0
        self.btc_balance=1.0
        
    def decrease_rate_counter(self):
        pass
        
    
    def sell_limit(self, volume, price):
        txid = self.handled_orders
        self.handled_orders += 1
        result = {'result': {'txid': [txid], 'descr': {'order': 'sell 0.00100000 XBTEUR @ limit 200000.0'}}, 'status':'closed', 'vol':volume, 'price':price}
        self.orders[txid] = result
        return result


    def buy_limit(self, volume, price):
        txid = self.handled_orders
        self.handled_orders += 1
        result = {'txid': txid, 'volume':volume, 'price':price}
        self.orders[txid] = result
        return result

    # We do not simulate market orders any differently, for simplicity
    def sell_market(self, volume):
        result = self.sell_limit(volume, 0)
        return result
        
    def buy_market(self, volume):
        # TODO Can we cleanly get the current price from the book?
        result = self.buy_limit(volume, 0)
        return result

    def query_orders(self, txid):
        return self.orders
    

    def cancel_order(self, order):
        return self.orders[order['txid']]


    def get_trade_balance(self, asset):
        r = {'EUR': self.eur_balance, 'BTC': self.btc_balance}
        if asset in r:
            return float(r[asset])
        return None

    def get_balance(self, asset='EUR'):
        r = {'EUR': self.eur_balance, 'BTC': self.btc_balance}
        if asset in r:
            return float(r[asset])
        return None


    def get_BTC_balance(self):
        return 0.0015374800

    
    def order_is_closed(self, order):
        return True
            
