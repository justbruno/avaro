#!/usr/bin/env python3

"""
Implements functionalities for simulation, such as accelerated sleep
and synchronization.
"""

import time
import threading
from conf import config

def sleep(period):
    """
    Runs a sped-up sleep (faster by a factor of the SPEEDUP config parameter).
    Meant chiefly for accelerated simulations.
    """
    time.sleep(1/config.SPEEDUP * period)


class Clock:
    """
    This class offers some synchronization functions.
    They are meant to be used to synchronize the book monitor and
    the strats in simulation mode. Otherwise, the results are very inconsistent
    at different simulation speeds.    

    Using this class, the book can wait for the strats to iterate before making
    an update. 
    """

    cv = threading.Condition()

    buy_done = False
    sell_done = False


    def strats_done():
        return Clock.buy_done and Clock.sell_done
    
    def register_buy():
        """
        Registers a buy-strat iteration.
        """
        Clock.buy_done = True
        with Clock.cv:
            Clock.cv.notify()
    
    def register_sell():
        """
        Registers a sell-strat iteration.
        """
        Clock.sell_done = True
        with Clock.cv:
            Clock.cv.notify()
    
    def book_lock():
        """
        Locks the calling process until a condition holds.
        The condition is that two variables, indicating whether
        both buy and sell strats have iterated, are True.        
        """
        with Clock.cv:
            Clock.cv.wait_for(Clock.strats_done)
        Clock.buy_done = False
        Clock.sell_done = False

