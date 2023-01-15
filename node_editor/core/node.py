from node_editor.core.socket import *
from node_editor.widget.node_content_widget import NodeContentWidget
from node_editor.widget.node_widget import NodeWidget


class Node:

    def __init__(self, scene, title="Undefined", inputs=None, outputs=None):
        self.scene = scene
        self.title = title
        # setup content
        self.content = NodeContentWidget(self)
        # setup widget
        self.grNode = NodeWidget(self)
        # associate to scene
        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)
        # setup sockets
        self.socket_spacing = 22
        self.inputs = []
        counter = 0
        for widget_type in inputs:
            socket = Socket(node=self, index=counter, position=Socket.PosType.LEFT_BOTTOM, widget_type=widget_type)
            counter += 1
            self.inputs.append(socket)

        self.outputs = []
        counter = 0
        for widget_type in outputs:
            socket = Socket(node=self, index=counter, position=Socket.PosType.RIGHT_TOP, widget_type=widget_type)
            counter += 1
            self.outputs.append(socket)

    def setMode(self, mode):
        self.scene.mode = mode

    @property
    def pos(self):
        return self.grNode.pos()

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    def getSocketPosition(self, index, position):
        x = 0 if (position in (Socket.PosType.LEFT_TOP, Socket.PosType.LEFT_BOTTOM)) else self.grNode.width

        if position in (Socket.PosType.LEFT_BOTTOM, Socket.PosType.RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - self.grNode.edge_size - self.grNode.padding - index * self.socket_spacing
        else:
            # start from top
            y = self.grNode.title_height + self.grNode.padding + self.grNode.edge_size + index * self.socket_spacing

        return [x, y]

    def updateEdges(self):
        for socket in self.inputs + self.outputs:
            if socket.hasEdge():
                socket.edge.updatePositions()

    def remove(self):
        for socket in (self.inputs + self.outputs):
            if socket.hasEdge():
                socket.edge.remove()
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        self.scene.removeNode(self)
