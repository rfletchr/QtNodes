import dataclasses
import typing
from qtpy import QtWidgets, QtGui, QtCore
from QtNodes.node import NodeItem
from QtNodes.port import PortItem, InputPort, OutputPort


@dataclasses.dataclass(frozen=True)
class PortType:
    datatype: str
    color: QtGui.QColor = None


@dataclasses.dataclass(frozen=True)
class NodeType:
    name: str
    category: str
    inputs: typing.Dict[str, str]
    outputs: typing.Dict[str, str]
    color: QtGui.QColor = None


class NodeFactory:
    def __init__(self):
        self.node_types: typing.Dict[str, NodeType] = {}
        self.port_types: typing.Dict[str, PortType] = {}

    def createNode(self, type_name: str):
        node_type = self.node_types[type_name]

        node = NodeItem(node_type.name)
        for name, port_type in node_type.inputs.items():
            node.addPort(self.createPort(name, port_type, node, True))

        for name, port_type in node_type.outputs.items():
            node.addPort(self.createPort(name, port_type, node, False))

        return node

    def createPort(self, name: str, port_type: str, node: NodeItem, is_input: bool):
        port_type = self.port_types[port_type]
        if is_input:
            instance = InputPort(name, port_type.datatype, node)
        else:
            instance = OutputPort(name, port_type.datatype, node)

        if isinstance(port_type.color, QtGui.QColor):
            instance.setColor(port_type.color)

        return instance
