import json
import os

from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel, QApplication, QMessageBox

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
        file_menu.addAction(self._init_action("&Exit", "Ctrl+Q", "Exit application", self.onClose))
        # edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self._init_action("&Undo", "Ctrl+Z", "Undo last operations", self.onUndo))
        edit_menu.addAction(self._init_action("&Redo", "Ctrl+Shift+Z", "Redo last operations", self.onRedo))
        edit_menu.addSeparator()
        edit_menu.addAction(self._init_action("&Cut", "Ctrl+X", "Cut to clipboard", self.onCut))
        edit_menu.addAction(self._init_action("&Copy", "Ctrl+C", "Copy to clipboard", self.onCopy))
        edit_menu.addAction(self._init_action("&Paste", "Ctrl+V", "Paste from clipboard", self.onPaste))
        edit_menu.addSeparator()
        edit_menu.addAction(self._init_action("&Delete", "Del", "Delete selected items", self.onDelete))

        # node editor
        node_editor = NodeEditor(self)
        node_editor.scene.observe(self._update_title)
        self.setCentralWidget(node_editor)
        # status bar
        self.statusBar().showMessage("")
        self.mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.mouse_pos)
        node_editor.view.scenePosChanged.connect(self.onScenePosChanged)
        # prepare window
        self.setGeometry(200, 200, 800, 600)
        self._update_title()
        self.show()

    def _update_title(self):
        title = "NodeEditor - "
        # append opened file name to title
        if self.filename is None:
            title += "New"
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().scene.modified:
            title += "*"

        self.setWindowTitle(title)

    def _init_action(self, name, shortcut, tooltip, callback):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        return action

    def onFileNew(self):
        print("onFileNew")
        if self.saveDialog():
            self.centralWidget().scene.clear()
            self.filename = None
            self._update_title()

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
            self._update_title()

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
        self._update_title()
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
        if not self._isModified():
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

    def _isModified(self):
        return self.centralWidget().scene.modified
