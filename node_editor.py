from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import *
from node_graphics_scene import NodeGraphicsScene
from node_graphics_view import NodeGraphicsView


class NodeEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init()

    def init(self):
        # create layout
        self.setGeometry(200, 200, 800, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        # create graphics scene
        self.grScene = NodeGraphicsScene()
        # create graphics view
        self.view = NodeGraphicsView(self.grScene, self)
        self.layout.addWidget(self.view)
        # prepare window
        self.setWindowTitle("Node Editor")
        self.show()

        self.debug_content()

    def debug_content(self):
        # draw green rect
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)
        rect = self.grScene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        # draw text
        text = self.grScene.addText("Hello World text!", QFont("Ubuntu"))
        text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1, 1, 1, 1))
        # draw widget
        # button
        widget = QPushButton("Hello World")
        proxy = self.grScene.addWidget(widget)
        proxy.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        proxy.setPos(0, 30)
        # text input
        text_input = QTextEdit()
        proxy2 = self.grScene.addWidget(text_input)
        proxy2.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        proxy2.setPos(0, 60)
        # draw lines
        line = self.grScene.addLine(-200, -200, 400, -100, outlinePen)
        line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)