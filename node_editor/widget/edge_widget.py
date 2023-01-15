import math

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from node_editor.core.socket import Socket


class EdgeWidget(QGraphicsPathItem):

    class Type:
        Direct = 1
        Bezier = 2

    def __init__(self, edge, type, parent=None):
        super().__init__(parent)

        self.edge = edge
        self.type = type
        self.edgeControlRoundness = 20

        self._posSource = [0,0]
        self._posDest = [200, 100]

        self._color = QColor("#001000")
        self._pen = QPen(self._color)
        self._pen.setWidthF(2.0)

        self._color_selected = QColor("#00ff00")
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)

        self._color_dragging = QColor("#ff0000")
        self._pen_dragging = QPen(self._color_dragging)
        self._pen_dragging.setWidthF(2.0)
        self._pen_dragging.setStyle(Qt.DashLine)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.setZValue(-1)

    def setSource(self, x, y):
        self._posSource = [x, y]

    def setDest(self, x, y):
        self._posDest = [x, y]

    @property
    def posSource(self):
        return self._posSource

    @property
    def posDest(self):
        return self._posDest

    def paint(self, painter, option, widget):
        self.setPath(self._getPath())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen_selected if self.isSelected() else self._pen)

        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def _getPath(self):
        s = self._posSource
        d = self._posDest
        path = QPainterPath(QPointF(s[0], s[1]))

        if self.type == EdgeWidget.Type.Direct:
            path.lineTo(d[0], d[1])

        elif self.type == EdgeWidget.Type.Bezier:

            distance = (d[0] - s[0]) * 0.5
            cpx_s = +distance
            cpx_d = -distance
            cpy_s = 0
            cpy_d = 0

            sspos = self.edge.start_socket.position
            if (s[0] > d[0] and sspos in (Socket.PosType.RIGHT_TOP, Socket.PosType.RIGHT_BOTTOM)) \
                    or (s[0] < d[0] and sspos in (Socket.PosType.LEFT_BOTTOM, Socket.PosType.LEFT_TOP)):

                cpx_d *= -1
                cpy_d = ((s[1] - d[1]) / math.fabs((s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001))
                cpy_d *= self.edgeControlRoundness

                cpx_s *= -1
                cpy_s = ((d[1] - s[1]) / math.fabs((d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001))
                cpy_s *= self.edgeControlRoundness

            path.cubicTo(
                s[0] + cpx_s,
                s[1] + cpy_s,
                d[0] + cpx_d,
                d[1] + cpy_d,
                d[0], d[1]
            )

        return path

    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self._getPath()
        return cutpath.intersects(path)
