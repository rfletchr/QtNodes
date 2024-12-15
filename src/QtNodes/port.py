__all__ = ["PortItem", "InputPort", "OutputPort"]

import typing
import weakref

from qtpy import QtGui, QtCore

from QtNodes.base import SceneItemBase
from QtNodes.connection import ConnectionItem

if typing.TYPE_CHECKING:
    from QtNodes.node import NodeItem


class PortItem(SceneItemBase):
    def __init__(self, name: str, datatype: str, node: "NodeItem", parent=None):
        super().__init__(parent=parent)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.__name = name
        self.__node = node
        self.__radius = 8.0
        self.__datatype = datatype
        self.__connections: weakref.WeakSet[ConnectionItem] = weakref.WeakSet()
        self.__size = QtCore.QSizeF(self.__radius * 2, self.__radius * 2)
        self.__pen = self.palette().color(self.palette().ColorRole.Dark)
        self.__color = self.palette().color(self.palette().ColorRole.Midlight)

    def setColor(self, color: QtGui.QColor):
        self.__color = color

    def color(self):
        return self.__color

    def name(self):
        return self.__name

    def datatype(self):
        return self.__datatype

    def default(self):
        return self.__default

    def addConnection(self, connection: "ConnectionItem"):
        self.__connections.add(connection)

    def removeConnection(self, connection: "ConnectionItem"):
        self.__connections.remove(connection)

    def connections(self):
        return tuple(self.__connections)

    def iterConnections(self):
        yield from self.__connections

    def numConnections(self):
        return len(self.__connections)

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemScenePositionHasChanged:
            for connection in self.__connections:
                connection.layout()
        return super().itemChange(change, value)

    def sizeHint(self, which, constraint=...):
        return self.__size

    def node(self):
        return self.__node

    def paint(self, painter, option, widget=...):
        painter.setPen(self.__color.lighter(150))
        painter.setBrush(self.__color)
        painter.drawEllipse(self.rect())

    def canConnectTo(self, port: "PortItem"):
        if port is self:
            return False

        elif port.datatype() != self.datatype():
            return False

        if self.node() == port.node():
            return False

        return True

    def toDict(self):
        return {
            "name": self.__name,
            "datatype": self.__datatype,
            "color": self.__color,
        }


class InputPort(PortItem):
    def canConnectTo(self, port: "PortItem"):
        if not super().canConnectTo(port):
            return False

        if not isinstance(port, OutputPort):
            return False

        return True


class OutputPort(PortItem):
    def canConnectTo(self, port: "PortItem"):
        if not super().canConnectTo(port):
            return False

        if not isinstance(port, InputPort):
            return False

        return True
