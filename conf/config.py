ORCHESTRATOR_SLEEP=10
SIMULATION=False
EXCHANGE='coinbase_interface'
BOOK='coinbase_book'
BOOK_PARAMS={}
LOGS_DIR='logs/cb'
ASSETS_FILE='assets_cb.txt'
BUY_STRAT='dip_chaser'
BUY_CONF='conf/dip_chaser_cb.conf'
SELL_STRAT='rally_chaser'
SELL_CONF='conf/rally_chaser_cb.conf'
FILTER_CONF='conf/filter_cb.conf'
LOGGER_LEVEL=500
SPEEDUP=1
GIVE_UP_MARGIN=15
DEFAULT_BUY_VOL_EUR=5
MAX_BOOK_UNRESPONSIVE=30 # When the book monitor is unresponsive for this many iterations in a row, we exit the program
TRIGGER_FILE='trigger_cb.txt'