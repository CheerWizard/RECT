from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QPainter, QMouseEvent
from PyQt5.QtWidgets import QGraphicsView

from node_editor.core.components import *
from node_editor.presentation.components import *


class NodeGraphicsView(QGraphicsView):

    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, scene, parent=None):
        super().__init__(parent)
        # scene
        self.scene = scene
        self.init()
        self.setScene(scene.grScene)
        # zooming
        self.zoomInFactor = 1.25
        self.zoom = 10
        self.zoomClamp = False
        self.zoomStep = 1
        self.zoomRange = [0, 10]
        # edge dragging
        self.edgeDragThreshold = 10
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.rubberBandDragRect = False
        # cutting line
        self.cutLine = CutLineWidget()
        self.scene.grScene.addItem(self.cutLine)
        # mouse
        self.lastMousePos = None

    def __str__(self):
        return "<Node %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    def init(self):
        self.setRenderHints(
            QPainter.Antialiasing |
            QPainter.HighQualityAntialiasing |
            QPainter.TextAntialiasing |
            QPainter.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        print("middleMouseButtonPress")
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        print("middleMouseButtonRelease")
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & -Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def leftMouseButtonPress(self, event):
        item = self._pickItem(event)

        self.lastPressedItemPos = self.mapToScene(event.pos())

        if type(item) is SocketWidget:
            if self.scene.mode == SceneMode.NONE:
                self.scene.mode = SceneMode.EDGE_DRAG
                self._edgeDragStart(item)
                return

        if self.scene.mode == SceneMode.EDGE_DRAG:
            if self._edgeDragEnd(item): return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self._beginCutLine(event)
                return
            else:
                self.rubberBandDragRect = True
        super().mousePressEvent(event)

    def _beginCutLine(self, event):
        self.scene.mode = SceneMode.EDGE_CUT
        fake_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                 Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(fake_event)
        QApplication.setOverrideCursor(Qt.CrossCursor)

    def _pickItem(self, event):
        return self.itemAt(event.pos())

    def leftMouseButtonRelease(self, event):
        item = self._pickItem(event)

        if self.scene.mode == SceneMode.EDGE_DRAG:
            # measure if distance is too far between release and last press position
            new_left_release_scene_pos = self.mapToScene(event.pos())
            dist = new_left_release_scene_pos - self.lastPressedItemPos
            if (dist.x() * dist.x() + dist.y() * dist.y()) >= self.edgeDragThreshold:
                if self._edgeDragEnd(item):
                    return

        if self.scene.mode == SceneMode.EDGE_CUT:
            self._endCutLine()
            return

        if self.rubberBandDragRect:
            self.rubberBandDragRect = False
            self.scene.history.store("View: RubberBandDrag selection", modified=False)

        super().mouseReleaseEvent(event)

    def _endCutLine(self):
        self._cutIntersectingEdges()
        self.cutLine.line_points = []
        self.cutLine.update()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.scene.mode = SceneMode.NONE

    def _cutIntersectingEdges(self):
        for i in range(len(self.cutLine.line_points) - 1):
            p1 = self.cutLine.line_points[i]
            p2 = self.cutLine.line_points[i + 1]
            for edge in self.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.scene.history.store("View::_cutIntersectingEdges", modified=True)

    def _edgeDragStart(self, item):
        log(self, "Begin EDGE_DRAG")
        log(self, "Assign StartSocket")
        self.previousEdge = item.socket.edge
        self.previousStartSocket = item.socket
        self.dragEdge = Edge(self.scene, item.socket, None, EdgeType.Bezier)

    def _edgeDragEnd(self, item):
        self.scene.mode = SceneMode.NONE
        log(self, "End EDGE_DRAG")

        if type(item) is SocketWidget:
            if item.socket != self.previousStartSocket:
                log(self, "Assign EndSocket")
                # remove old edge
                if item.socket.hasEdge():
                    item.socket.edge.remove()
                if self.previousEdge is not None:
                    self.previousEdge.remove()
                # bind dragged edge to sockets and update edge position
                self.dragEdge.start_socket = self.previousStartSocket
                self.dragEdge.end_socket = item.socket
                self.dragEdge.start_socket.bindEdge(self.dragEdge)
                self.dragEdge.end_socket.bindEdge(self.dragEdge)
                self.dragEdge.updatePositions()

                self.scene.history.store("New edge created during drag in View::_edgeDragEnd", modified=True)

                return True

        self.dragEdge.remove()
        self.dragEdge = None

        if self.previousEdge is not None:
            self.previousEdge.start_socket.edge = self.previousEdge

        return False

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # eval zoom factor
        zoomOutFactor = 1 / self.zoomInFactor
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep
        # zoom clamping
        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

    def mouseMoveEvent(self, event):
        # edge dragging
        if self.scene.mode == SceneMode.EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDest(pos.x(), pos.y())
            self.dragEdge.grEdge.update()
        # edge cursor cutting
        if self.scene.mode == SceneMode.EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutLine.line_points.append(pos)
            self.cutLine.update()
        # notify scene pos changed
        self.lastMousePos = self.mapToScene(event.pos())
        self.scenePosChanged.emit(
            int(self.lastMousePos.x()),
            int(self.lastMousePos.y())
        )

        super().mouseMoveEvent(event)

    def deleteSelected(self):
        for item in self.scene.grScene.selectedItems():
            if type(item) == EdgeWidget:
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()

        self.scene.history.store("View::_deleteSelected", modified=True)
