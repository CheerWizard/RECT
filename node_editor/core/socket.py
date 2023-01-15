from node_editor.widget.socket_widget import SocketWidget


class Socket():

    class PosType:
        LEFT_TOP = 1
        LEFT_BOTTOM = 2
        RIGHT_TOP = 3
        RIGHT_BOTTOM = 4

    def __init__(self, node, index=0, position=PosType.LEFT_TOP, widget_type=SocketWidget.Type.DEFAULT):
        self.node = node
        self.index = index
        self.position = position
        self.widget_type = widget_type
        self.grSocket = SocketWidget(self, widget_type)
        self.grSocket.setPos(*self.node.getSocketPosition(index, position))
        self.edge = None

    def __str__(self):
        return "<Socket %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    def bindEdge(self, edge=None):
        self.edge = edge

    def getPosition(self):
        return self.node.getSocketPosition(index=self.index, position=self.position)

    def hasEdge(self):
        return self.edge is not None
