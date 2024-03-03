#!/usr/bin/env python3
import numpy as np
from iotools import logger
from conf import constants
from conf import config

ASSETS_FILE = config.ASSETS_FILE

class AssetManager():
    """
    This class holds and manages the list of assets we have bought, broken down by purchase price.
    """
    
    def __init__(self):

        logger.trace('Initiliasing AM')
        logger.trace(ASSETS_FILE)
        
        self.asset_list = []
                
        with open(ASSETS_FILE, 'r') as f:
            for l in f:
                s = l.strip('\n').split(',')
                self.asset_list.append({'volume':float(s[1]), 'price':float(s[0]), 'progress':float(s[2]), 'timestamp':float(s[3])})

        self.sort_asset_list()


    def dump_assets(self):
        with open(ASSETS_FILE, 'w') as f:
            for s in self.asset_list:
                f.write('{},{},{},{}\n'.format(s['price'], s['volume'], s['progress'], s['timestamp']))
        

    def get_assets(self):
        return self.asset_list
            

    def add_order(self, order):
        order['progress'] = 0
        self.asset_list.append(order)
        self.asset_list = sorted(self.asset_list, key=lambda x: x['price'])
        self.sort_asset_list()
        self.dump_assets()
        

    def queue_pop(self):
        if len(self.asset_list) > 0:
            order = self.asset_list[0]
            self.asset_list = self.asset_list[1:]            
            self.sort_asset_list()
            self.dump_assets()
            return order
        else:
            return None
        

    def add_progress(self, profit):        
        for k in range(len(self.asset_list)):
            self.asset_list[k]['progress'] += profit
            # When a high-progress expensive asset is sold, newer, low-progress cheap assets will
            # reflect the loss when the high-progress asset is sold. We are not interested in
            # registering negative progress (no need to make up for losses, as they were covered by past profits),
            # so we truncate to zero.
            self.asset_list[k]['progress'] = np.max([0, self.asset_list[k]['progress']])

        self.dump_assets()
                

    def get_first(self):
        if len(self.asset_list) > 0:
            return self.asset_list[0]
        else:
            return None


    def compute_order_gain(self, order, bid):
        gain = (bid*order['volume']*(1-constants.FEE) - order['price']*order['volume']*(1+constants.FEE))
        return gain

    
    def sort_asset_list(self):
        # Sort asset_list by descendingly by progress+gain (done ascending, by taking the negative of that)
        # The gain is estimated by taking a rough guess of where the bid should be at, as the formula is not
        # to sensitive to it.
        if len(self.asset_list) > 0:
            bid_placeholder = np.min([o['price'] for o in self.asset_list])        
            self.asset_list = sorted(self.asset_list, key=lambda order: -order['progress'] - self.compute_order_gain(order, bid_placeholder))
