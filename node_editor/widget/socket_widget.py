from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SocketWidget(QGraphicsItem):

    class Type:
        DEFAULT = 0

    def __init__(self, socket, widget_type=Type.DEFAULT):
        self.socket = socket
        super().__init__(socket.node.grNode)

        self.radius = 6
        self.outline_width = 1

        self._colors = [
            QColor("#FFFF7700"),
            QColor("#FF52e220"),
            QColor("#FF0056a6"),
            QColor("#FFa86db1"),
            QColor("#FFb54747"),
            QColor("#FFdbe220")
        ]
        self._color_background = self._colors[widget_type]
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

    def paint(self, painter, styles, widget=None):
        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self):
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )