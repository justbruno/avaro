from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel

import time

class ControlPanel(QMainWindow):
    def __init__(self, book_monitor=None, dispatcher=None):
        super().__init__()        

        self.book_monitor = book_monitor
        self.dispatcher = dispatcher


        # Buttons
        
        self.buy_limit_btn = QPushButton("1: Buy LIMIT")
        self.buy_market_btn = QPushButton("2: Buy MARKET")
        self.sell_limit_btn = QPushButton("3: Sell LIMIT")
        self.sell_market_btn = QPushButton("4: Sell MARKET")

        self.buy_limit_btn.clicked.connect(self.buy_limit_event)
        self.buy_market_btn.clicked.connect(self.buy_market_event)
        self.sell_limit_btn.clicked.connect(self.sell_limit_event)
        self.sell_market_btn.clicked.connect(self.sell_market_event)

        btn_layout = QHBoxLayout()

        btn_layout.addWidget(self.buy_limit_btn)
        btn_layout.addWidget(self.buy_market_btn)
        btn_layout.addWidget(self.sell_limit_btn)
        btn_layout.addWidget(self.sell_market_btn)

        #---

        # Book info
        self.ask_l = QLabel("")
        self.spread_l = QLabel("")
        self.bid_l = QLabel("")
        
        book_layout = QVBoxLayout()
        book_layout.addWidget(self.ask_l)
        book_layout.addWidget(self.spread_l)
        book_layout.addWidget(self.bid_l)

        self.timer = QTimer()        # create a new QTimer instance
        self.timer.setInterval(1000) # make it fire every 1000 msec
        self.timer.timeout.connect(self.update_info) # connect the timeout signal to self.setting_label
        self.timer.start()
        #---
        
        layout = QVBoxLayout()
        layout.addLayout(btn_layout)
        layout.addLayout(book_layout)
        
        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)

        
    def buy_limit_event(self):
        self.dispatcher.emit_buy(order_type='limit')
        
    def buy_market_event(self):
        self.dispatcher.emit_buy(order_type='market')
        
    def sell_limit_event(self):
        self.dispatcher.emit_sell(order_type='limit')
        
    def sell_market_event(self):
        self.dispatcher.emit_sell(order_type='market')
        

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.buy_limit_event()
        elif e.key() == Qt.Key_2:
            self.buy_market_event()
        elif e.key() == Qt.Key_3:
            self.sell_limit_event()
        elif e.key() == Qt.Key_4:
            self.sell_market_event()

    def update_info(self):
        ask, bid = self.book_monitor.get_ask_bid()
        self.ask_l.setText(f"Ask: {ask}")
        self.spread_l.setText(f"Spr: {ask-bid:.2}")
        self.bid_l.setText(f"Bid:  {bid}")
            
def initialize(book_monitor, dispatcher):
    app = QApplication([])
    control_panel = ControlPanel(book_monitor=book_monitor, dispatcher=dispatcher)
    control_panel.show()

    app.exec()

