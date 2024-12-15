__all__ = ["LineItem", "ConnectionItem"]

import typing

from qtpy import QtWidgets, QtGui, QtCore

if typing.TYPE_CHECKING:
    from QtNodes.port import PortItem, OutputPort, InputPort


class LineItem(QtWidgets.QGraphicsLineItem):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        pen = QtGui.QPen(QtGui.QColor(16, 16, 16), 4, QtCore.Qt.PenStyle.SolidLine)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        self.setPen(pen)


class ConnectionItem(LineItem):
    def __init__(self, output_port: "OutputPort", input_port: "InputPort", parent=None):
        super().__init__(parent=parent)
        self.setAcceptHoverEvents(True)
        self.__output_port = output_port
        self.__input_port = input_port

        pen = QtGui.QPen(input_port.color().darker(125), 8)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)

        self.setPen(pen)
        self.attach()
        self.layout()

    def attach(self):
        self.__output_port.addConnection(self)
        self.__input_port.addConnection(self)

    def detache(self):
        self.__output_port.removeConnection(self)
        self.__input_port.removeConnection(self)

    def hoverEnterEvent(self, event):
        self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.CursorShape.LastCursor)
        super().hoverLeaveEvent(event)

    def outputPort(self):
        return self.__output_port

    def inputPort(self):
        return self.__input_port

    def layout(self):
        self.setLine(
            *self.__output_port.sceneBoundingRect().center().toTuple(),
            *self.__input_port.sceneBoundingRect().center().toTuple(),
        )
        self.update()
