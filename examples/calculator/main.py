import sys

from PyQt5.QtWidgets import *

from calculator_window import CalculatorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = CalculatorWindow()
    wnd.show()
    sys.exit(app.exec_())
