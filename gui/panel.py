from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit

import time
import reports

class ControlPanel(QMainWindow):
    def __init__(self, book_monitor=None, dispatcher=None, asset_manager=None):
        super().__init__()        

        self.book_monitor = book_monitor
        self.dispatcher = dispatcher
        self.asset_manager = asset_manager

        self.locked = False
        
        # Buttons
        
        self.buy_limit_btn = QPushButton("1: Buy LIMIT")
        self.buy_market_btn = QPushButton("2: Buy MARKET")
        self.sell_limit_btn = QPushButton("3: Sell LIMIT")
        self.sell_market_btn = QPushButton("4: Sell MARKET")
        self.lock_btn = QPushButton("L: Lock/Unlock")

        self.buy_limit_btn.clicked.connect(self.buy_limit_event)
        self.buy_market_btn.clicked.connect(self.buy_market_event)
        self.sell_limit_btn.clicked.connect(self.sell_limit_event)
        self.sell_market_btn.clicked.connect(self.sell_market_event)
        self.lock_btn.clicked.connect(self.toggle_lock)

        btn_layout = QHBoxLayout()

        btn_layout.addWidget(self.buy_limit_btn)
        btn_layout.addWidget(self.buy_market_btn)
        btn_layout.addWidget(self.sell_limit_btn)
        btn_layout.addWidget(self.sell_market_btn)
        btn_layout.addWidget(self.lock_btn)

        #---

        # Custom order controls
        price_label = QLabel("Price")
        self.price_le = QLineEdit()
        expiry_label = QLabel("Expiry")
        self.expiry_le = QLineEdit()
        self.custom_order_btn = QPushButton("Buy LIMIT at custom price")
        self.custom_order_btn.clicked.connect(self.custom_buy_limit_event)

        custom_order_layout = QHBoxLayout()
        custom_order_layout.addWidget(price_label)
        custom_order_layout.addWidget(self.price_le)
        custom_order_layout.addWidget(expiry_label)
        custom_order_layout.addWidget(self.expiry_le)
        custom_order_layout.addWidget(self.custom_order_btn)
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
        self.timer.setInterval(250) # make it fire every 1000 msec
        self.timer.timeout.connect(self.update_info) # connect the timeout signal to self.setting_label
        self.timer.start()
        #---

        # Assets info
        self.assets_title_l = QLabel("Assets:")
        self.assets_l = QLabel("")
        assets_layout = QVBoxLayout()
        assets_layout.addWidget(self.assets_l)
        #---
        
        layout = QVBoxLayout()
        layout.addLayout(btn_layout)
        layout.addLayout(custom_order_layout)
        layout.addLayout(book_layout)
        layout.addLayout(assets_layout)

        
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
        
    def custom_buy_limit_event(self):
        self.dispatcher.emit_buy(order_type='limit', price=int(self.price_le.text()), expiry=int(self.expiry_le.text()), give_up_margin=2000)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_L:
            self.toggle_lock()
        if self.locked:
            return        

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
        msg = reports.build_asset_list(self.asset_manager, self.book_monitor)
        self.assets_l.setText(msg)
        
        
    def toggle_lock(self):
        self.buy_limit_btn.setEnabled(not self.buy_limit_btn.isEnabled())
        self.buy_market_btn.setEnabled(not self.buy_market_btn.isEnabled())
        self.sell_limit_btn.setEnabled(not self.sell_limit_btn.isEnabled())
        self.sell_market_btn.setEnabled(not self.sell_market_btn.isEnabled())
        self.locked = not self.locked
        
        
def initialize(book_monitor, dispatcher, asset_manager):
    app = QApplication([])
    control_panel = ControlPanel(book_monitor=book_monitor, dispatcher=dispatcher, asset_manager=asset_manager)
    control_panel.show()

    app.exec()

