import random

from PyQt5.QtCore import QFile

from node_editor.core.components import *
from node_editor.node_view import NodeGraphicsView
from node_editor.presentation.components import *


class NodeEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_stylesheet("res/node_editor/nodestyle.qss")
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
        # create presentation view
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
        Edge(
            self.scene,
            nodes[0].outputs[0],
            nodes[1].inputs[0],
            edge_type=EdgeType.Bezier
        )
        Edge(
            self.scene,
            nodes[1].outputs[0],
            nodes[2].inputs[0],
            edge_type=EdgeType.Bezier
        )
