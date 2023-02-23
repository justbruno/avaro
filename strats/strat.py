from iotools import logger

class Strat:
    """
    Base Strat.
    """
    
    def __init__(self):
        # When this object decides to sell, it will call the functions in this list
        self.callbacks = []
        
    def add_callback(self, f):
        self.callbacks.append(f)        

    def print_report(self):
        logger.trace('Base Strat report.')
