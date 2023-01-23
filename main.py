import inspect
import os.path
import sys

from PyQt5.QtWidgets import *

from src.node_editor.node_window import NodeWindow

from rdk.RdkModule import RdkModule
from rdk.PyTest import PyTest
from src.styles import loadStyle

if __name__ == "__main__":
    # rdk
    rdk_module = RdkModule()
    rdk_module.print()
    pytest = PyTest(1)
    print(pytest.add(5, 5))
    # rect
    app = QApplication(sys.argv)
    wnd = NodeWindow()
    module = os.path.dirname(inspect.getfile(wnd.__class__))
    loadStyle(os.path.join(module, "res/node_editor/style.qss"))
    sys.exit(app.exec_())
