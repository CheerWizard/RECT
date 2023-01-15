import json
from collections import OrderedDict

from logger import log
from serialization.serializable import Serializable

from node_editor.presentation.components import *

# ---------------- Scene --------------- #


class Scene(Serializable):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        self.width, self.height = 64000, 64000
        self.mode = SceneMode.NONE
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

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        log(self, "saveToFile %s succeeded!" % filename)

    def loadFrom(self, filename):
        with open(filename, "r") as file:
            scene_json = file.read()
            scene_data = json.loads(scene_json)
            self.deserialize(scene_data)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes:
            nodes.append(node.serialize())
        for edge in self.edges:
            edges.append(edge.serialize())

        return OrderedDict([
            ('id', self.id),
            ('width', self.width),
            ('height', self.height),
            ('nodes', nodes),
            ('edges', edges),
        ])

    def deserialize(self, data, hashmap={}):
        self.clear()
        hashmap = {}
        # scene info
        self.width = data['width']
        self.height = data['height']
        # create nodes
        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap)
        # create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap)

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()


# ---------------- Node --------------- #

class Node(Serializable):

    def __init__(self, scene, title="Undefined", inputs=None, outputs=None):
        super().__init__()

        self.scene = scene
        self._title = title
        # setup content
        self.content = NodeContent(self)
        # setup presentation
        self.grNode = NodeWidget(self)
        # associate to scene
        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)
        # setup sockets
        self.socket_spacing = 22
        self.inputs = []
        self.outputs = []
        self._init_sockets(inputs, outputs)

    def _init_sockets(self, inputs, outputs):
        # create input sockets
        counter = 0
        if inputs is not None:
            for widget_type in inputs:
                socket = Socket(node=self, index=counter, position=SocketPosType.LEFT_BOTTOM, widget_type=widget_type)
                counter += 1
                self.inputs.append(socket)
        # create output sockets
        counter = 0
        if outputs is not None:
            for widget_type in outputs:
                socket = Socket(node=self, index=counter, position=SocketPosType.RIGHT_TOP, widget_type=widget_type)
                counter += 1
                self.outputs.append(socket)

    def setMode(self, mode):
        self.scene.mode = mode

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = value

    @property
    def pos(self):
        return self.grNode.pos()

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    def getSocketPosition(self, index, position):
        x = 0 if (position in (SocketPosType.LEFT_TOP, SocketPosType.LEFT_BOTTOM)) else self.grNode.width

        if position in (SocketPosType.LEFT_BOTTOM, SocketPosType.RIGHT_BOTTOM):
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

    def serialize(self):
        inputs, outputs = [], []
        for socket_in in self.inputs:
            inputs.append(socket_in.serialize())
        for socket_out in self.outputs:
            outputs.append(socket_out.serialize())

        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.pos().x()),
            ('pos_y', self.grNode.pos().y()),
            ('content', self.content.serialize()),
            ('inputs', inputs),
            ('outputs', outputs)
        ])

    def deserialize(self, data, hashmap={}):
        # info
        self.id = data['id']
        hashmap[data['id']] = self
        self.title = data['title']
        self.setPos(data['pos_x'], data['pos_y'])
        # sockets
        self.inputs = []
        self.outputs = []
        inputs_data = data['inputs']
        outputs_data = data['outputs']
        inputs_data.sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        outputs_data.sort(key=lambda socket: socket['index'] + socket['position'] * 10000)

        for socket_data in inputs_data:
            index = socket_data['index']
            position = socket_data['position']
            socket_type = socket_data['socket_type']
            new_socket = Socket(node=self, index=index, position=position, widget_type=socket_type)
            new_socket.deserialize(data=socket_data, hashmap=hashmap)
            self.inputs.append(new_socket)

        for socket_data in outputs_data:
            index = socket_data['index']
            position = socket_data['position']
            socket_type = socket_data['socket_type']
            new_socket = Socket(node=self, index=index, position=position, widget_type=socket_type)
            new_socket.deserialize(data=socket_data, hashmap=hashmap)
            self.outputs.append(new_socket)

        return True

# ---------------- Node Content --------------- #


class NodeContent(Serializable):

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.grContent = NodeContentWidget(self)

    def setMode(self, mode):
        self.node.setMode(mode)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
        ])

    def deserialize(self, data, hashmap={}):
        return False


# ---------------- Socket --------------- #


class Socket(Serializable):

    def __init__(self, node, index=0, position=SocketPosType.LEFT_TOP, widget_type=SocketType.DEFAULT):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = widget_type
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

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data['id']
        hashmap[data['id']] = self
        return True

# ---------------- Edge --------------- #


class Edge(Serializable):

    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EdgeType.Direct):
        super().__init__()

        self._start_socket = None
        self._end_socket = None
        self._end_socket = None

        self.scene = scene
        self.grEdge = EdgeWidget(self)
        self.scene.grScene.addItem(self.grEdge)
        self.scene.addEdge(self)

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type

    @property
    def start_socket(self):
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        self._start_socket = value
        if self._start_socket is not None:
            self._start_socket.edge = self

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        self._end_socket = value
        if self._end_socket is not None:
            self._end_socket.edge = self

    @property
    def edge_type(self):
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        self._edge_type = value
        self.updatePositions()

    def __str__(self):
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    # update source and dest graphical positions
    def updatePositions(self):
        # update source position
        start = None
        if self.start_socket is not None:
            start = self.start_socket.getPosition()
            start[0] += self.start_socket.node.grNode.pos().x()
            start[1] += self.start_socket.node.grNode.pos().y()
            self.grEdge.setSource(*start)
        # update end position
        if self.end_socket is not None:
            end = self.end_socket.getPosition()
            end[0] += self.end_socket.node.grNode.pos().x()
            end[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDest(*end)
        else:
            if start is not None:
                self.grEdge.setDest(*start)
        # update edge
        log(self, "StartSocket: %s" % self.start_socket)
        log(self, "EndSocket: %s" % self.end_socket)
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

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('start', self.start_socket.id),
            ('end', self.end_socket.id),
            ('edge_type', self.edge_type),
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']
