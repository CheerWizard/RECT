import sys

from PyQt5.QtWidgets import *

from src.node_editor.node_window import NodeWindow

from rdk.RdkModule import RdkModule
from rdk.PyTest import PyTest

if __name__ == "__main__":
    # rdk
    rdk_module = RdkModule()
    rdk_module.print()
    pytest = PyTest(1)
    print(pytest.add(5, 5))
    # rect
    app = QApplication(sys.argv)
    node_editor_wnd = NodeWindow() 
    sys.exit(app.exec_())
