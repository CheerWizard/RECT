import os

from PyQt5.QtCore import QSettings, QPoint, QSize
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel, QApplication, QMessageBox

from src.node_editor.node_editor import NodeEditor


class NodeWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.company = "RECT Studio"
        self.product = "Node Editor"
        self.init()

    def init(self):
        self.createActions()
        self.createMenus()
        self.createNodeEditor()
        self.createStatusBar()
        # prepare window
        self.setGeometry(200, 200, 800, 600)
        self.updateTitle()
        self.show()

    def updateTitle(self):
        title = "NodeEditor - "
        title += self.getCurrentWidget().getFilename()
        self.setWindowTitle(title)

    def createActions(self):
        self.action_new = QAction("&New", self, shortcut="Ctrl+N", statusTip="Create new graph", triggered=self.onFileNew)
        self.action_open = QAction("&Open", self, shortcut="Ctrl+O", statusTip="Open file", triggered=self.onFileOpen)
        self.action_save = QAction("&Save", self, shortcut="Ctrl+S", statusTip="Save file", triggered=self.onFileSave)
        self.action_save_as = QAction("Save &As...", self, shortcut="Ctrl+Shift+S", statusTip="Save file as...", triggered=self.onFileSaveAs)
        self.action_exit = QAction("E&xit", self, shortcut="Ctrl+Q", statusTip="Exit application", triggered=self.onClose)

        self.action_undo = QAction("&Undo", self, shortcut="Ctrl+Z", statusTip="Undo last operations", triggered=self.onUndo)
        self.action_redo = QAction("&Redo", self, shortcut="Ctrl+Shift+Z", statusTip="Redo last operations", triggered=self.onRedo)
        self.action_cut = QAction("Cu&t", self, shortcut="Ctrl+X", statusTip="Cut to clipboard", triggered=self.onCut)
        self.action_copy = QAction("&Copy", self, shortcut="Ctrl+C", statusTip="Copy to clipboard", triggered=self.onCopy)
        self.action_paste = QAction("&Paste", self, shortcut="Ctrl+V", statusTip="Paste from clipboard", triggered=self.onPaste)
        self.action_delete = QAction("&Delete", self, shortcut="Del", statusTip="Delete selected items", triggered=self.onDelete)

    def createMenus(self):
        menubar = self.menuBar()
        # file menu
        self.file_menu = menubar.addMenu("&File")
        self.file_menu.addAction(self.action_new)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_save_as)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)
        # edit menu
        self.edit_menu = menubar.addMenu("&Edit")
        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addAction(self.action_redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_cut)
        self.edit_menu.addAction(self.action_copy)
        self.edit_menu.addAction(self.action_paste)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_delete)

    def createNodeEditor(self):
        self.node_editor = NodeEditor(self)
        self.node_editor.scene.observe(self.updateTitle)
        self.setCentralWidget(self.node_editor)

    def createStatusBar(self):
        self.statusBar().showMessage("")
        self.mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.mouse_pos)
        self.node_editor.view.scenePosChanged.connect(self.onScenePosChanged)

    def onFileNew(self):
        print("onFileNew")
        if self.saveDialog():
            self.centralWidget().scene.clear()
            self.filename = None
            self.updateTitle()

    def onFileOpen(self):
        print("onFileOpen")

        if not self.saveDialog():
            return

        file_name, filter = QFileDialog.getOpenFileName(self, "Open graph file")

        if file_name == '':
            return

        if os.path.isfile(file_name):
            self.centralWidget().scene.loadFrom(file_name)
            self.filename = file_name
            self.updateTitle()

    def onFileSave(self):
        print("onFileSave")
        if self.filename is None:
            return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage("Graph has been saved into %s" % self.filename)
        return True

    def onFileSaveAs(self):
        print("onFileSaveAs")
        file_name, filter = QFileDialog.getSaveFileName(self, "Save graph into file")
        if file_name == '':
            return False
        self.filename = file_name
        self.updateTitle()
        return self.onFileSave()

    def onClose(self):
        print("onClose")

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

    def onCut(self):
        data = self.centralWidget().scene.clipboard.cutItems()
        QApplication.instance().clipboard().setText(data)

    def onCopy(self):
        data = self.centralWidget().scene.clipboard.copy()
        QApplication.instance().clipboard().setText(data)

    def onPaste(self):
        json_data = QApplication.instance().clipboard().text()
        self.centralWidget().scene.clipboard.paste(json_data)

    def closeEvent(self, event):
        if self.saveDialog():
            event.accept()
        else:
            event.ignore()

    def saveDialog(self):
        if not self.isModified():
            return True
        result = QMessageBox.warning(
            self,
            "Are you sure?",
            "Unsaved changes will be lost. Continue?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )

        if result == QMessageBox.Save:
            return self.onFileSave()

        return result == QMessageBox.Discard

    def isModified(self):
        return self.getCurrentWidget().scene.modified

    def getCurrentWidget(self):
        return self.centralWidget()

    def readSettings(self):
        settings = QSettings(self.company, self.product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.company, self.product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
