"""
Tools to evaluate the performance of a strategy based on its trading log.
"""

FEE = 0.0016
import numpy as np
from iotools import io_handler

def evaluate(filename):
    profit = 0
    held = 0
    nbuys,nsells = 0,0
    unmatched = 0
    portfolio_values = []
    outstanding = []
    revenue = 0
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
                nbuys += 1
                outstanding.append((price, volume))
            elif s[0] == 'sell':
                profit += price*volume*(1-FEE)
                #print(price*volume*(1+FEE))
                unmatched -= 1
                held -= volume
                nsells += 1

                #print('Sold: ', volume)                
                # Match to buy to compute revenue
                matches = []
                for x in outstanding:
                    if x[1] == volume:
                        matches.append(x)
                #print(f'Outstanding: {outstanding}')
                #print(f'Matches: {matches}')
                match = matches[np.argmin([i[0] for i in matches])]
                revenue += price*volume*(1-FEE) - match[0]*match[1]*(1+FEE)
                outstanding = [i for i in outstanding if i[0] != match[0] or i[1] != match[1]]
                
            #print(profit, unmatched)
            #print()
            last_price = price
            # We attach the timestamp to each observed value to improve strategy performance comparison plots
            portfolio_values.append((ts, held*last_price*(1-FEE) + profit))

    return {'nbuys':nbuys, 'nsells':nsells, 'portfolio_values':portfolio_values, 'held':held, 'profit':profit, 'revenue':revenue}
    
