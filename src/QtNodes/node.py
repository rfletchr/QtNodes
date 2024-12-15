import typing
from qtpy import QtWidgets, QtGui, QtCore

from QtNodes.base import SceneItemBase
from QtNodes.items import StaticTextItem, SceneSpaceShadowEffect
from QtNodes.port import InputPort, OutputPort, PortItem

Orientation = QtCore.Qt.Orientation


class TitleItem(StaticTextItem):
    def sizeHint(self, which, constraint=...):
        base = super().sizeHint(which, constraint=constraint)
        return QtCore.QSizeF(base.width() + 50, base.height() + 5)


class NodeItem(SceneItemBase):
    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self.__name = name
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(self.GraphicsItemFlag.ItemNegativeZStacksBehindParent)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)

        self.__inputs = {}
        self.__outputs = {}
        self.__title_item = TitleItem(name)
        self.__outer_layout = QtWidgets.QGraphicsLinearLayout(Orientation.Vertical)

        self.__grid_size = 16

        self.__grid_layout = QtWidgets.QGraphicsGridLayout()
        self.__grid_layout.addItem(self.__title_item, 0, 2)

        self.__outer_layout.addItem(self.__grid_layout)
        self.setLayout(self.__outer_layout)

    def name(self):
        return self.__name

    def toDict(self):
        return {
            "name": self.__name,
            "inputs": [p[1].toDict() for p in self.__inputs.values()],
            "outputs": [p[1].toDict() for p in self.__outputs.values()],
        }

    @classmethod
    def fromDict(cls, data: dict):
        node = cls(data["name"])
        for input_data in data["inputs"]:
            item = node.addInput(input_data["name"], input_data["datatype"])
            item.setColor(input_data["color"])

        for input_data in data["outputs"]:
            item = node.addOutput(input_data["name"], input_data["datatype"])
            item.setColor(input_data["color"])

        return node

    def clone(self):
        return self.fromDict(self.toDict())

    def addPort(self, port: PortItem):
        text_item = StaticTextItem(port.name())
        if isinstance(port, InputPort):
            collection = self.__inputs
            text_col = 1
            port_col = 0
        else:
            collection = self.__outputs
            text_col = 3
            port_col = 4

        row = len(collection) + 1
        collection[port.name()] = (text_item, port, row)
        self.__grid_layout.addItem(port, row, port_col)
        self.__grid_layout.addItem(text_item, row, text_col)

    def addInput(self, name: str, datatype: str):
        port_item = InputPort(name, datatype, self)
        self.addPort(port_item)
        return port_item

    def addOutput(self, name: str, datatype: str):
        port_item = OutputPort(name, datatype, self)
        self.addPort(port_item)
        return port_item

    def paint(self, painter, option, widget=...):
        painter.setPen(QtCore.Qt.PenStyle.NoPen)

        path = QtGui.QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        painter.setClipPath(path)

        painter.setBrush(self.palette().brush(self.palette().ColorRole.Midlight))
        painter.drawRoundedRect(self.rect(), 10, 10)
        painter.setBrush(self.palette().brush(self.palette().ColorRole.Accent))

        title_bottom = self.mapRectFromScene(
            self.__title_item.sceneBoundingRect()
        ).bottom()
        title_rect = QtCore.QRectF(self.rect())
        title_rect.setHeight(title_bottom)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRect(title_rect)

        if self.isSelected():
            painter.setOpacity(0.5)
            painter.setPen(
                QtGui.QPen(
                    self.palette().color(self.palette().ColorRole.BrightText),
                    2,
                    QtCore.Qt.PenStyle.DotLine,
                )
            )
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(self.rect(), 10, 10)
        else:
            pen = QtGui.QColor(0, 0, 0, 64)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(self.rect(), 10, 10)

    def iterInputs(self):
        for _, port, _ in self.__inputs.values():
            yield port

    def iterOutputs(self):
        for _, port, _ in self.__outputs.values():
            yield port
