import enum
import typing
import uuid

from qtpy import QtCore, QtWidgets, QtGui

from QtNodes.connection import ConnectionItem, LineItem
from QtNodes.port import PortItem
from QtNodes.node import NodeItem, TitleItem


class SceneEventFilter(QtCore.QObject):
    def eventFilter(
        self,
        watched: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneEvent,
    ):
        EventTypes = QtWidgets.QGraphicsSceneMouseEvent.Type
        if not isinstance(event, QtWidgets.QGraphicsSceneMouseEvent):
            return False

        if event.type() == EventTypes.GraphicsSceneMousePress:
            return self.mousePress(watched, event)
        elif event.type() == EventTypes.GraphicsSceneMouseMove:
            return self.mouseMove(watched, event)
        elif event.type() == EventTypes.GraphicsSceneMouseRelease:
            return self.mouseRelease(watched, event)

        return False

    def mousePress(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):

        return False

    def mouseMove(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):

        return False

    def mouseRelease(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):

        return False


class NodeEventFilter(SceneEventFilter):
    requestMoveNodes = QtCore.Signal(list, QtCore.QPointF, str)
    requestCloneNodes = QtCore.Signal(list, list)

    class Mode(enum.Enum):
        Idle = enum.auto()
        AwaitingDrag = enum.auto()
        Cloning = enum.auto()
        Moving = enum.auto()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mode = self.Mode.Idle
        self.operation_id: str | None = None
        self.clicked_item: NodeItem | None = None
        self.nodes: set[NodeItem] = set()
        self.preview_items: list[QtWidgets.QGraphicsPixmapItem] = []

    def snapshotNode(self, node: NodeItem, oversample: float = 1.0):
        bounds = node.mapRectToScene(
            node.boundingRect().united(node.childrenBoundingRect())
        )
        pixmap = QtGui.QPixmap(bounds.size().toSize() * oversample)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        painter.setRenderHint(painter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(painter.RenderHint.SmoothPixmapTransform, True)

        node.scene().render(painter, QtCore.QRectF(pixmap.rect()), bounds)
        painter.end()
        return pixmap

    def reset(self):
        for item in self.preview_items:
            if not item.scene():
                continue
            item.scene().removeItem(item)

        self.preview_items.clear()

        self.mode = self.Mode.Idle
        self.nodes.clear()

    def mousePress(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):
        self.reset()

        item = scene.itemAt(event.scenePos(), QtGui.QTransform())
        if not isinstance(item, NodeItem):
            return False

        self.clicked_item = item
        self.mode = self.Mode.AwaitingDrag
        self.operation_id = uuid.uuid4().hex

        item.setSelected(True)
        selected_items = [n for n in scene.selectedItems() if isinstance(n, NodeItem)]

        if event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
            self.nodes = selected_items
        else:
            for node in selected_items:
                if node is item:
                    continue
                node.setSelected(False)
            self.nodes = [item]

        return True

    def mouseMove(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):
        if self.mode == self.Mode.Idle:
            return False

        elif self.mode == self.Mode.AwaitingDrag:
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                self.mode = self.Mode.Cloning
                for node in self.nodes:
                    item = QtWidgets.QGraphicsPixmapItem(self.snapshotNode(node))
                    item.setPos(node.scenePos())
                    self.preview_items.append(item)
                    scene.addItem(item)
            else:
                self.mode = self.Mode.Moving

        delta = event.scenePos() - event.lastScenePos()

        if self.mode == self.Mode.Moving:
            self.requestMoveNodes.emit(self.nodes, delta, self.operation_id)
            return True
        elif self.mode == self.Mode.Cloning:
            for item in self.preview_items:
                item.moveBy(*delta.toTuple())

        return False

    def mouseRelease(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):
        result = False

        if self.mode == self.Mode.AwaitingDrag:
            for item in scene.selectedItems():
                if item is self.clicked_item:
                    continue
                item.setSelected(False)

            result = True
        elif self.mode == self.Mode.Cloning:
            self.requestCloneNodes.emit(
                self.nodes.copy(), [i.scenePos() for i in self.preview_items]
            )
            result = True

        elif self.mode == self.Mode.Moving:
            result = True

        self.reset()

        return result


class ConnectionEventFilter(SceneEventFilter):
    requestCreateConnection = QtCore.Signal(PortItem, PortItem)
    requestRemoveConnection = QtCore.Signal(ConnectionItem)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__preview_line = LineItem()
        self.__active_port: typing.Optional[PortItem] = None
        self.__active_connection: typing.Optional[ConnectionItem] = None

    def mousePress(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):
        item = scene.itemAt(event.scenePos(), QtGui.QTransform())
        if isinstance(item, PortItem):
            self.__active_port = item

        elif isinstance(item, ConnectionItem):
            self.__active_connection = item
            d1 = (
                event.scenePos() - item.outputPort().sceneBoundingRect().center()
            ).manhattanLength()
            d2 = (
                event.scenePos() - item.inputPort().sceneBoundingRect().center()
            ).manhattanLength()

            if d1 > d2:
                self.__active_port = item.outputPort()
            else:
                self.__active_port = item.inputPort()

        else:
            return False

        scene.addItem(self.__preview_line)

        self.__preview_line.setLine(
            *self.__active_port.sceneBoundingRect().center().toTuple(),
            *event.scenePos().toTuple()
        )

        return True

    def mouseMove(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):
        if not self.__active_port:
            return False

        if self.__active_connection:
            self.requestRemoveConnection.emit(self.__active_connection)
            self.__active_connection = None

        self.__preview_line.setLine(
            *self.__active_port.sceneBoundingRect().center().toTuple(),
            *event.scenePos().toTuple()
        )

        return False

    def mouseRelease(
        self,
        scene: QtWidgets.QGraphicsScene,
        event: QtWidgets.QGraphicsSceneMouseEvent,
    ):

        if self.__preview_line.scene() is scene:
            scene.removeItem(self.__preview_line)

        if not self.__active_port:
            return False

        port_b = scene.itemAt(event.scenePos(), QtGui.QTransform())

        if isinstance(port_b, PortItem):
            self.requestCreateConnection.emit(self.__active_port, port_b)

        self.__active_port = None

        return True
