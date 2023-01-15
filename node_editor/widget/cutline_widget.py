from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class CutLineWidget(QGraphicsItem):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.line_points = []

        self._pen = QPen(Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self):
        return QRectF(0, 0, 1, 1)

    def paint(self, painter, options, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)