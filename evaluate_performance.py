"""
Quick script to evaluate the performance of a strategy based on its trading log.
"""

FEE = 0.0016
import numpy as np
profit = 0

held = 0
unmatched = 0
with open('dummy_logs/trades.log', 'r')  as f:
    for l in f:
        s = l.strip('\n').split(' ')[2].split(',')
        price = float(s[1])
        volume = float(s[2])
        if s[0] == 'buy':
            profit -= price*volume*(1+FEE)
            print(-price*volume*(1+FEE))
            unmatched += 1
            held += volume
        elif s[0] == 'sell':
            profit += price*volume*(1+FEE)
            print(price*volume*(1+FEE))
            unmatched -= 1
            held -= volume
        print(profit, unmatched)
        print()
        last_price = price
print(profit, unmatched)
print(held*last_price*(1-FEE))
print(held*last_price*(1-FEE) + profit)
