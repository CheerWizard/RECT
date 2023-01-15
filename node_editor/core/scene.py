from node_editor.widget.scene_widget import NodeGraphicsScene


class Mode:
    NONE = 0
    EDGE_DRAG = 1
    NODE_EDIT = 2
    EDGE_CUT = 3


class Scene:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.width, self.height = 64000, 64000
        self.mode = Mode.NONE
        self.init()

    def init(self):
        self.grScene = NodeGraphicsScene(self)
        self.grScene.setGrScene(self.width, self.height)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        self.nodes.remove(node)

    def removeEdge(self, edge):
        self.edges.remove(edge)