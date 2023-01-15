import RDK


class PyTest:

    def __init__(self, id):
        self.cpp = RDK.PyTest(id)

    def add(self, a, b):
        return self.cpp.add(a, b)