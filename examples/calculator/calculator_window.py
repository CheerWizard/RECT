import os

from PyQt5.QtCore import *
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import *

from examples.calculator.calculator_sub_window import CalculatorSubWindow
from src.node_editor.node_window import NodeWindow
from src.styles import *

import res.node_editor.dark_resources


class CalculatorWindow(NodeWindow):

    def init(self):
        self.listWidget = None
        self.items = None
        self.company = 'RECT Studio'
        self.product = 'Calculator'

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "res/node_editor/style.qss")
        loadStyles(
            os.path.join(os.path.dirname(__file__), "res/node_editor/dark.qss"),
            self.stylesheet_filename
        )

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.createNodesDock()

        self.readSettings()

        self.setWindowTitle("Calculator NodeEditor Example")

    def createToolBars(self):
        pass

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createNodesDock(self):
        self.listWidget = QListWidget()
        self.listWidget.addItem("Add")
        self.listWidget.addItem("Subtract")
        self.listWidget.addItem("Multiply")
        self.listWidget.addItem("Divide")

        self.items = QDockWidget("Nodes")
        self.items.setWidget(self.listWidget)
        self.items.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.items)

    def updateMenus(self):
        pass

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def createActions(self):
        super().createActions()

        self.closeAct = QAction(
            "Cl&ose", self,
            statusTip="Close the active window",
            triggered=self.mdiArea.closeActiveSubWindow
        )

        self.closeAllAct = QAction(
            "Close &All", self,
            statusTip="Close all the windows",
            triggered=self.mdiArea.closeAllSubWindows
        )

        self.tileAct = QAction(
            "&Tile", self,
            statusTip="Tile the windows",
            triggered=self.mdiArea.tileSubWindows
        )

        self.cascadeAct = QAction(
            "&Cascade", self,
            statusTip="Cascade the windows",
            triggered=self.mdiArea.cascadeSubWindows
        )

        self.nextAct = QAction(
            "Ne&xt", self,
            shortcut=QKeySequence.NextChild,
            statusTip="Move the focus to the next window",
            triggered=self.mdiArea.activateNextSubWindow
        )

        self.previousAct = QAction(
            "Pre&vious", self,
            shortcut=QKeySequence.PreviousChild,
            statusTip="Move the focus to the previous window",
            triggered=self.mdiArea.activatePreviousSubWindow
        )

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QAction(
            "&About", self,
            statusTip="Show the application's About box",
            triggered=self.onAbout
        )

        self.aboutQtAct = QAction(
            "About &Qt", self,
            statusTip="Show the Qt library's About box",
            triggered=QApplication.instance().aboutQt
        )

    def createMenus(self):
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def onAbout(self):
        QMessageBox.about(self, "About Calculator",
                          "The <b>Calculator</b> example demonstrates how to make calculations using Node Graph ")

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def onFileNew(self):
        wnd = self.createMdiChild()
        wnd.show()

    def createMdiChild(self):
        node_editor = CalculatorSubWindow()
        sub_wnd = self.mdiArea.addSubWindow(node_editor)
        return sub_wnd

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None
