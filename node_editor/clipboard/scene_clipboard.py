import json
from collections import OrderedDict

from node_editor.presentation.components import *


class SceneClipboard:

    def __init__(self, scene):
        super().__init__()
        self._scene = scene

    def _save(self):
        # store and sort selected items
        saved_nodes, edges, socket_map = [], [], {}
        for selected in self._scene.grScene.selectedItems():
            if isinstance(selected, NodeWidget):
                node = selected.node
                saved_nodes.append(node.serialize())
                for socket in (node.inputs + node.outputs):
                    socket_map[socket.id] = socket
            elif isinstance(selected, EdgeWidget):
                edges.append(selected.edge)
        # add only edge connected to both selected sockets
        saved_edges = []
        for edge in edges:
            if edge.start_socket.id in socket_map and edge.end_socket.id in socket_map:
                saved_edges.append(edge.serialize())

        return OrderedDict([
            ('nodes', saved_nodes),
            ('edges', saved_edges)
        ])

    def cut(self):
        data = self._save()
        # remove and store into history
        self._scene.grScene.view()[0].deleteSelected()
        self._scene.history.store("Cutting items into clipboard", modified=True)
        return json.dumps(data, indent=4)

    def copy(self):
        data = self._save()
        return json.dumps(data, indent=4)

    def paste(self, json_data):

        try:
            data = json.loads(json_data)
        except ValueError as e:
            print("onPaste error: JSON data is invalid", e)
            return False

        if 'nodes' not in data:
            print("onPaste error: JSON data does not contain 'nodes'")
            return False

        hashmap = {}

        # eval scene pos using mouse pos
        view = self._scene.grScene.views()[0]
        mouse_pos = view.lastMousePos
        # eval selected items bounds and center
        min_x, min_y, max_x, max_y = 0, 0, 0, 0
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
        bbox_center_x = (min_x + max_x) / 2
        bbox_center_y = (min_y + max_y) / 2
        # eval offset new items
        offset_x = mouse_pos.x() - bbox_center_x
        offset_y = mouse_pos.y() - bbox_center_y
        # create nodes
        for node_data in data['nodes']:
            from node_editor.core.components import Node
            node = Node(self._scene)
            node.deserialize(node_data, hashmap, restore=False)
            pos = node.pos
            node.setPos(pos.x() + offset_x, pos.y() + offset_y)
        # create edges
        for edge_data in data['edges']:
            from node_editor.core.components import Edge
            edge = Edge(self._scene)
            edge.deserialize(edge_data, hashmap, restore=False)
        # store history
        self._scene.history.store("Pasting items from clipboard", modified=True)
        return True
