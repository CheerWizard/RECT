from PyQt5.QtWidgets import *

from node_editor.node_view import Mode


class NodeContentWidget(QWidget):

    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self._init()

    def _init(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.label = QLabel("Title")
        self.layout.addWidget(self.label)
        self.layout.addWidget(TextEditWidget(self, "foo"))

    def setMode(self, mode=Mode.NONE):
        self.node.setMode(mode)


class TextEditWidget(QTextEdit):

    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.content = content

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

    def focusInEvent(self, event):
        self.content.setMode(Mode.NODE_EDIT)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.content.setMode(Mode.NONE)
        super().focusOutEvent(event)
