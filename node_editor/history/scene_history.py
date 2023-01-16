from node_editor.presentation.components import EdgeWidget, NodeWidget


class SceneHistory:

    def __init__(self, scene):
        self.scene = scene
        self.history_stack = []
        self.history_ptr = -1
        self.history_limit = 32

    def undo(self):
        if self.history_ptr > 0:
            self.history_ptr -= 1
            self.restore()

    def redo(self):
        if self.history_ptr + 1 < len(self.history_stack):
            self.history_ptr += 1
            self.restore()

    def restore(self):
        self.restoreStamp(self.history_stack[self.history_ptr])

    def store(self, description, modified=False):
        self.scene.modified = modified

        if self.history_ptr + 1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_ptr + 1]
        # remove first element from history, if history is out of bounds
        if self.history_ptr + 1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_ptr -= 1
        # store new history stamp
        stamp = self.createStamp(description)
        self.history_stack.append(stamp)
        self.history_ptr += 1

    def createStamp(self, description):
        # storing selected items
        selected = {
            'nodes': [],
            'edges': []
        }
        for item in self.scene.grScene.selectedItems():
            if isinstance(item, NodeWidget):
                selected['nodes'].append(item.node.id)
            elif isinstance(item, EdgeWidget):
                selected['edges'].append(item.edge.id)
        # returns stamp with scene state
        return {
            'description': description,
            'snapshot': self.scene.serialize(),
            'selected': selected
        }

    def restoreStamp(self, stamp):
        self.scene.deserialize(stamp['snapshot'])
        # restoring selected items
        for selected_id in stamp['selected']['edges']:
            for edge in self.scene.edges:
                edge.grEdge.selected = selected_id == edge.id
                break
        for selected_id in stamp['selected']['nodes']:
            for node in self.scene.nodes:
                node.grNode.selected = selected_id == node.id
                break