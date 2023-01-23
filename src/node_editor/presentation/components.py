import math

from PyQt5.QtCore import QLine, Qt, QRectF, QPointF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# ----------------- Scene UI -------------------- #

class SceneMode:
    NONE = 0
    EDGE_DRAG = 1
    NODE_EDIT = 2
    EDGE_CUT = 3


class NodeGraphicsScene(QGraphicsScene):
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene

        self.gridSize = 20
        self.gridSquares = 5

        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)

    def setGrScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        # create grid view
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        bottom = int(math.ceil(rect.bottom()))
        top = int(math.floor(rect.top()))
        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)
        # eval lines
        lines_light, lines_dark = [], []
        cell = self.gridSize * self.gridSquares

        for x in range(first_left, right, self.gridSize):
            if x % cell != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):
            if y % cell != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))
        # draw lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)
        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        for node in self.scene.nodes:
            if node.grNode.isSelected():
                node.updateEdges()


# ----------------- Node UI -------------------- #

class NodeWidget(QGraphicsItem):

    def __init__(self, node, parent=None):
        super().__init__(parent)

        self.node = node

        self.title_item = QGraphicsTextItem(self)
        self.title = node.title
        self._title_color = Qt.GlobalColor.white
        self._title_font = QFont("Ubuntu", 10)

        self.width = 180
        self.height = 240
        self.edge_size = 10
        self.title_height = 24
        self.moved = False

        self._padding = 4.0

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self._init_title()
        self._init_content()
        self._init_sockets()

        self._init()

    @property
    def title(self): return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.moved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self.moved:
            self.moved = False
            self.node.scene.history.store("Node: has been moved", modified=True)

    def _init(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def _init_title(self):
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(
            self.width
            - 2 * self._padding
        )

    def _init_content(self):
        self.grContent = QGraphicsProxyWidget(self)
        content_widget = self.node.content.grContent
        content_widget.setGeometry(
            self.edge_size,
            self.title_height + self.edge_size,
            self.width - 2 * self.edge_size,
            self.height - 2 * self.edge_size - self.title_height,
        )
        self.grContent.setWidget(content_widget)

    def _init_sockets(self):
        pass

    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def paint(self, painter, options, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0,0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())
        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())
        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_outline.simplified())

    @property
    def padding(self):
        return self._padding

# ----------------- NodeContent UI -------------------- #

class NodeContentWidget(QWidget):

    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.content = content
        self._init()

    def _init(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.label = QLabel("Title")
        self.layout.addWidget(self.label)
        self.layout.addWidget(TextEditWidget(self.content, "foo"))


class TextEditWidget(QTextEdit):

    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.content = content

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

    def focusInEvent(self, event):
        self.content.setMode(SceneMode.NODE_EDIT)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.content.setMode(SceneMode.NONE)
        super().focusOutEvent(event)


# ----------------- Socket UI -------------------- #

class SocketPosType:
    LEFT_TOP = 1
    LEFT_BOTTOM = 2
    RIGHT_TOP = 3
    RIGHT_BOTTOM = 4


class SocketType:
    DEFAULT = 0


class SocketWidget(QGraphicsItem):

    def __init__(self, socket, widget_type=SocketType.DEFAULT):
        self.socket = socket
        super().__init__(socket.node.grNode)

        self.radius = 9
        self.outline_width = 2

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

# ----------------- Edge UI -------------------- #


class EdgeType:
    Direct = 1
    Bezier = 2


class EdgeWidget(QGraphicsPathItem):

    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge
        self.edgeControlRoundness = 20

        self._posSource = [0, 0]
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
        edge_type = self.edge.edge_type

        if edge_type == EdgeType.Direct:
            path.lineTo(d[0], d[1])

        elif edge_type == EdgeType.Bezier:

            distance = (d[0] - s[0]) * 0.5
            cpx_s = +distance
            cpx_d = -distance
            cpy_s = 0
            cpy_d = 0

            if self.edge.start_socket is not None:
                sspos = self.edge.start_socket.position

                if (s[0] > d[0] and sspos in (SocketPosType.RIGHT_TOP, SocketPosType.RIGHT_BOTTOM)) \
                        or (s[0] < d[0] and sspos in (SocketPosType.LEFT_BOTTOM, SocketPosType.LEFT_TOP)):
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

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self._getPath()

# ----------------- CutLine UI -------------------- #


class CutLineWidget(QGraphicsItem):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.line_points = []

        self._pen = QPen(Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        path = None
        poly = QPolygonF(self.line_points)

        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPointF(1, 1))

        return path

    def paint(self, painter, options, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)