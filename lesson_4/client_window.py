from client_form import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, qApp
import sys


class ClientMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.show()