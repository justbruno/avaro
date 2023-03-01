"""
Tools to evaluate the performance of a strategy based on its trading log.
"""

FEE = 0.0016
import numpy as np
from iotools import io_handler

def evaluate(filename):
    profit = 0
    held = 0
    unmatched = 0
    portfolio_values = []
    with open(filename, 'r')  as f:
        for l in f:
            fields = l.strip('\n').split(' ')
            ts = io_handler.timestamp_to_epoch(' '.join(fields[:2]))
            s = fields[2].split(',')
            price = float(s[1])
            volume = float(s[2])
            if s[0] == 'buy':
                profit -= price*volume*(1+FEE)
                #print(-price*volume*(1+FEE))
                unmatched += 1
                held += volume
            elif s[0] == 'sell':
                profit += price*volume*(1+FEE)
                #print(price*volume*(1+FEE))
                unmatched -= 1
                held -= volume
            #print(profit, unmatched)
            #print()
            last_price = price
            # We attach the timestamp to each observed value to improve strategy performance comparison plots
            portfolio_values.append((ts, held*last_price*(1-FEE) + profit))

    return portfolio_values
    
