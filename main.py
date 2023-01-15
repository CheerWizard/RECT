import sys

from PyQt5.QtWidgets import *

from node_editor.node_editor import NodeEditor

from rdk.RdkModule import RdkModule
from rdk.PyTest import PyTest

if __name__ == "__main__":
    app = QApplication(sys.argv)
    nodeEditor = NodeEditor()

    rdk_module = RdkModule()
    rdk_module.print()
    pytest = PyTest(1)
    print(pytest.add(5, 5))

    sys.exit(app.exec_())
