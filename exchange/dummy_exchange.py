#!/usr/bin/env python3

"""
Dummy exchange interface for simulation.
"""

class ExchangeInterface:
    def __init__(self):
        print('USING DUMMY EXCHANGE')
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
            
