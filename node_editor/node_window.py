import os

from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel

from node_editor.node_editor import NodeEditor


class NodeWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.filename = None
        self._init()

    def _init(self):
        menubar = self.menuBar()
        # file menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self._init_action("&New", "Ctrl+N", "Create new graph", self.onFileNew))
        file_menu.addSeparator()
        file_menu.addAction(self._init_action("&Open", "Ctrl+O", "Open file", self.onFileOpen))
        file_menu.addAction(self._init_action("&Save", "Ctrl+S", "Save file", self.onFileSave))
        file_menu.addAction(self._init_action("Save &As...", "Ctrl+Shift+S", "Save file as...", self.onFileSaveAs))
        file_menu.addSeparator()
        file_menu.addAction(self._init_action("&Exit", "Ctrl+Q", "Exit application", self.onExitApplication))
        # edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self._init_action("&Undo", "Ctrl+Z", "Undo last operations", self.onUndo))
        edit_menu.addAction(self._init_action("&Redo", "Ctrl+Shift+Z", "Redo last operations", self.onRedo))
        edit_menu.addSeparator()
        edit_menu.addAction(self._init_action("&Delete", "Del", "Delete selected items", self.onDelete))
        # node editor
        node_editor = NodeEditor(self)
        self.setCentralWidget(node_editor)
        # status bar
        self.statusBar().showMessage("")
        self.mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.mouse_pos)
        node_editor.view.scenePosChanged.connect(self.onScenePosChanged)
        # prepare window
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Node Editor")
        self.show()

    def _init_action(self, name, shortcut, tooltip, callback):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        return action

    def onFileNew(self):
        print("onFileNew")
        self.centralWidget().scene.clear()

    def onFileOpen(self):
        print("onFileOpen")
        file_name, filter = QFileDialog.getOpenFileName(self, "Open graph file")

        if file_name == '':
            return

        if os.path.isfile(file_name):
            self.centralWidget().scene.loadFrom(file_name)

    def onFileSave(self):
        print("onFileSave")
        if self.filename is None:
            return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage("Graph has been saved into %s" % self.filename)


    def onFileSaveAs(self):
        print("onFileSaveAs")
        file_name, filter = QFileDialog.getSaveFileName(self, "Save graph into file")

        if file_name == '':
            return

        self.filename = file_name
        self.onFileSave()

    def onExitApplication(self):
        print("onExitApplication")

    def onUndo(self):
        print("onUndo")
        self.centralWidget().scene.history.undo()

    def onRedo(self):
        print("onRedo")
        self.centralWidget().scene.history.redo()

    def onDelete(self):
        print("onDelete")
        self.centralWidget().scene.grScene.views()[0].deleteSelected()

    def onScenePosChanged(self, x, y):
        self.mouse_pos.setText("Coordinates: [%d, %d]" % (x, y))
