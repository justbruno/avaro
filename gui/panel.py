from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

# Only needed for access to command line arguments
import sys

class ControlPanel:
    def __init__(self, book_monitor, dispatcher):
        super().__init__()
        
        app = QApplication(sys.argv)

        self.book_monitor = book_monitor
        self.dispatcher = dispatcher
        
        self.buy_limit_btn = QPushButton("Buy LIMIT")
        self.buy_market_btn = QPushButton("Buy MARKET")
        self.sell_limit_btn = QPushButton("Sell LIMIT")
        self.sell_market_btn = QPushButton("Sell MARKET")

        self.buy_limit_btn.setCheckable(True)
        self.buy_limit_btn.clicked.connect(self.the_button_was_clicked)

        window = QMainWindow()#QWidget()
        window.show()  # IMPORTANT!!!!! Windows are hidden by default.

        # Start the event loop.
        app.exec()

        
    def buy_limit(self):
        print("Buy LIMIT clicked!!!1")
        



ControlPanel()
