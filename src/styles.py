from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication

from src.core.logger import *


def loadStyle(filename):
    logt("styles", "loadStyle()", filename)
    file = QFile(filename)
    opened = file.open(QFile.ReadOnly | QFile.Text)

    if opened:
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding="utf-8"))
    else:
        logt("styles", "Failed to open file %s" % filename)


def loadStyles(*args):
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet, encoding='utf-8')
    QApplication.instance().setStyleSheet(res)
