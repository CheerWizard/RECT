from logger import log
from node_editor.widget.edge_widget import *


class Edge:

    def __init__(self, scene, start_socket, end_socket, widget_type=EdgeWidget.Type.Direct):
        self.scene = scene

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.start_socket.edge = self
        if self.end_socket is not None:
            self.end_socket.edge = self

        self.grEdge = EdgeWidget(self, widget_type)

        self.updatePositions()
        log(self, "Edge: %s -> %s" % (self.grEdge.posSource, self.grEdge.posDest))
        self.scene.grScene.addItem(self.grEdge)
        self.scene.addEdge(self)

    def __str__(self):
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    # update source and dest graphical positions
    def updatePositions(self):
        # update source position
        sourcePos = self.start_socket.getPosition()
        sourcePos[0] += self.start_socket.node.grNode.pos().x()
        sourcePos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*sourcePos)
        # update end position
        if self.end_socket is not None:
            endPos = self.end_socket.getPosition()
            endPos[0] += self.end_socket.node.grNode.pos().x()
            endPos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDest(*endPos)
        else:
            self.grEdge.setDest(*sourcePos)
        # update edge
        log(self, "StartSocket: %s" % self.start_socket)
        log(self, "EndSocket: %s" % self.start_socket)
        self.grEdge.update()

    # remove from all socket slots
    def unbindAll(self):
        if self.start_socket is not None:
            self.start_socket.edge = None
        if self.end_socket is not None:
            self.end_socket.edge = None
        self.start_socket = None
        self.end_socket = None

    # remove from scene
    def remove(self):
        self.unbindAll()
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
