import json
from collections import OrderedDict

from src.core.logger import log
from src.node_editor.clipboard.scene_clipboard import SceneClipboard
from src.node_editor.history.scene_history import SceneHistory
from serialization.serializable import Serializable

from src.node_editor.presentation.components import *

# ---------------- Scene --------------- #


class Scene(Serializable):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        self.width, self.height = 64000, 64000
        self.mode = SceneMode.NONE
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self._modified = False
        self._modified_listeners = []

        self.grScene = None
        self.init()

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, is_modified):
        if not self._modified and is_modified:
            self._modified = is_modified
            for listener in self._modified_listeners:
                listener()

        self._modified = is_modified

    def observe(self, listener):
        self._modified_listeners.append(listener)

    def removeObserver(self, listener):
        self._modified_listeners.remove(listener)

    def removeObservers(self):
        self._modified_listeners.clear()

    def init(self):
        self.grScene = NodeGraphicsScene(self)
        self.grScene.setGrScene(self.width, self.height)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            log(self, "removeNode: can't remove node=%s" % node)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            log(self, "removeEdge: can't remove edge=%s" % edge)

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            log(self, "saveToFile %s succeeded!" % filename)
            self.modified = False

    def loadFrom(self, filename):
        with open(filename, "r") as file:
            scene_json = file.read()
            scene_data = json.loads(scene_json)
            self.deserialize(scene_data)
            self.modified = False

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

    def deserialize(self, data, hashmap={}, restore=True):
        self.clear()
        hashmap = {}
        if restore:
            self.id = data['id']
        # scene info
        self.width = data['width']
        self.height = data['height']
        # create nodes
        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap, restore)
        # create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap, restore)

    def clear(self):
        self.modified = False
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
                socket = Socket(node=self, index=counter, position=SocketPosType.LEFT_BOTTOM, widget_type=widget_type,
                                multi_edges=False)
                counter += 1
                self.inputs.append(socket)
        # create output sockets
        counter = 0
        if outputs is not None:
            for widget_type in outputs:
                socket = Socket(node=self, index=counter, position=SocketPosType.RIGHT_TOP, widget_type=widget_type,
                                multi_edges=True)
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
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        for socket in (self.inputs + self.outputs):
            for edge in socket.edges:
                edge.remove()

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

    def deserialize(self, data, hashmap={}, restore=True):
        # info
        if restore:
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
            new_socket = Socket(node=self, index=index, position=position, widget_type=socket_type,
                                multi_edges=False)
            new_socket.deserialize(data=socket_data, hashmap=hashmap, restore=restore)
            self.inputs.append(new_socket)

        for socket_data in outputs_data:
            index = socket_data['index']
            position = socket_data['position']
            socket_type = socket_data['socket_type']
            new_socket = Socket(node=self, index=index, position=position, widget_type=socket_type,
                                multi_edges=True)
            new_socket.deserialize(data=socket_data, hashmap=hashmap, restore=restore)
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

    def deserialize(self, data, hashmap={}, restore=True):
        return False


# ---------------- Socket --------------- #


class Socket(Serializable):

    def __init__(self, node, index=0, position=SocketPosType.LEFT_TOP, widget_type=SocketType.DEFAULT, multi_edges=True):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = widget_type
        self.multi_edges = multi_edges
        self.grSocket = SocketWidget(self, widget_type)
        self.grSocket.setPos(*self.node.getSocketPosition(index, position))
        self.edges = []

    def __str__(self):
        return "<Socket %s %s..%s>" % ("Multi-Edge" if self.multi_edges else "Single-Edge", hex(id(self))[2:5], hex(id(self))[-3:])

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            log(self, "removeEdge: can't remove edge=%s" % edge)

    def removeEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()

    def getPosition(self):
        return self.node.getSocketPosition(index=self.index, position=self.position)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('position', self.position),
            ('socket_type', self.socket_type),
            ('multi_edges', self.multi_edges)
        ])

    def deserialize(self, data, hashmap={}, restore=True):
        if restore:
            self.id = data['id']
        self.multi_edges = data['multi_edges']
        hashmap[data['id']] = self
        return True

# ---------------- Edge --------------- #


class Edge(Serializable):

    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EdgeType.Direct):
        super().__init__()

        self._start_socket = None
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
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)
        self._start_socket = value
        if self._start_socket is not None:
            self._start_socket.addEdge(self)

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)
        self._end_socket = value
        if self._end_socket is not None:
            self._end_socket.addEdge(self)

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

    def deserialize(self, data, hashmap={}, restore=True):
        if restore:
            self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']
