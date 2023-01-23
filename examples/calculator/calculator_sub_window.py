from PyQt5.QtCore import *

from src.node_editor.node_editor import NodeEditor


class CalculatorSubWindow(NodeEditor):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.scene.observe(self.updateTitle)
        self.updateTitle()

    def updateTitle(self):
        self.setWindowTitle(self.getFilename())
