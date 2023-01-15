import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from logger import log
from node_editor.core.edge import Edge
from node_editor.core.node import Node
from node_editor.core.scene import Scene
from node_editor.node_view import NodeGraphicsView
from node_editor.widget.edge_widget import EdgeWidget


class NodeEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.styleSheet_filename = "node_editor/qss/nodestyle.qss"
        self._load_stylesheet(self.styleSheet_filename)
        self._init()

    def _init(self):
        # create layout
        self.setGeometry(200, 200, 800, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        # create scene
        self.scene = Scene()
        self.addNodes()
        # create widget view
        self.view = NodeGraphicsView(self.scene, self)
        self.layout.addWidget(self.view)
        # prepare window
        self.setWindowTitle("Node Editor")
        self.show()

    def _load_stylesheet(self, filename):
        log(self, "_load_stylesheet()", filename)
        file = QFile(filename)
        opened = file.open(QFile.ReadOnly | QFile.Text)

        if opened:
            stylesheet = file.readAll()
            QApplication.instance().setStyleSheet(str(stylesheet, encoding="utf-8"))
        else:
            log(self, "Failed to open file", filename)

    def addNodes(self):
        nodes = []
        for i in range(0, 3):
            node = Node(
                self.scene,
                "TestNode_%s" % i,
                inputs=[i, i, i],
                outputs=[1]
            )
            node.setPos(random.randrange(-300, 300), random.randrange(-300, 300))
            nodes.append(node)
        # create edges
        edge1 = Edge(
            self.scene,
            nodes[0].outputs[0],
            nodes[1].inputs[0],
            widget_type=EdgeWidget.Type.Bezier
        )
        edge2 = Edge(
            self.scene,
            nodes[1].outputs[0],
            nodes[2].inputs[0],
            widget_type=EdgeWidget.Type.Bezier
        )
