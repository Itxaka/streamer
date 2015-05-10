from simpleapp import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainApp, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Test app")

if __name__ == "__main__":
    a = QtWidgets.QApplication(sys.argv)
    w = MainApp()
    w.show()
    sys.exit(a.exec_())