import os.path
import random

from src.node_editor.core.components import *
from src.node_editor.node_view import NodeGraphicsView


class NodeEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = None
        self._init()

    def isFilenameSet(self):
        return self.filename is not None

    def getFilename(self):
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.scene.modified else "")

    def _init(self):
        # create layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        # create scene
        self.scene = Scene()
        self.addNodes()
        # create presentation view
        self.view = NodeGraphicsView(self.scene, self)
        self.layout.addWidget(self.view)

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
