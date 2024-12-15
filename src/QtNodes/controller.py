import typing

from qtpy import QtWidgets, QtCore, QtGui

from QtNodes.node import NodeItem
from QtNodes.connection import ConnectionItem
from QtNodes.port import PortItem, InputPort, OutputPort
from QtNodes.scene_events import ConnectionEventFilter, NodeEventFilter
from QtNodes.factory import NodeFactory
from QtNodes import commands


class NodeGraphController(QtCore.QObject):
    def __init__(
        self,
        scene: QtWidgets.QGraphicsScene = None,
        undo_stack: QtGui.QUndoStack = None,
        factory: "NodeFactory" = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.undo_stack = undo_stack or QtGui.QUndoStack()
        self.scene = scene or QtWidgets.QGraphicsScene()
        self.factory = factory or NodeFactory()
        self.scene.setSceneRect(-100000, -100000, 200000, 200000)

        self.connection_event_filter = ConnectionEventFilter()
        self.node_event_filter = NodeEventFilter()

        self.scene.installEventFilter(self.connection_event_filter)
        self.scene.installEventFilter(self.node_event_filter)

        self.connection_event_filter.requestCreateConnection.connect(
            self.createConnection
        )
        self.connection_event_filter.requestRemoveConnection.connect(
            self.removeConnection
        )

        self.node_event_filter.requestCloneNodes.connect(self.cloneNodes)
        self.node_event_filter.requestMoveNodes.connect(self.moveNodes)

    def createNode(self, type_name: str):
        node = self.factory.createNode(type_name)
        command = commands.AddItemToSceneCommand(self.scene, node)
        command.setText(f"Add: {node.name()}")
        self.undo_stack.push(command)

    def removeNode(self, node: NodeItem):
        command = commands.RemoveNodeCommand(self.scene, node)
        command.setText(f"Remove: {node.name()}")
        self.undo_stack.push(command)

    def removeNodes(self, nodes: typing.Iterable[NodeItem]):
        self.undo_stack.beginMacro("delete nodes")
        for node in nodes:
            self.removeNode(node)
        self.undo_stack.endMacro()

    def nodes(self):
        return [n for n in self.scene.items() if isinstance(n, NodeItem)]

    def selectedNodes(self):
        return [n for n in self.scene.selectedItems() if isinstance(n, NodeItem)]

    def createConnection(self, port_a: "PortItem", port_b: "PortItem"):
        if not port_a.canConnectTo(port_b):
            return

        if isinstance(port_a, InputPort) and isinstance(port_b, OutputPort):
            input_port = port_a
            output_port = port_b
        else:
            input_port = port_b
            output_port = port_a

        connection = ConnectionItem(output_port, input_port)
        cmd = commands.AddItemToSceneCommand(self.scene, connection)
        self.undo_stack.push(cmd)
        return connection

    def removeConnection(self, connection):
        cmd = commands.RemoveConnectionCommand(self.scene, connection)
        self.undo_stack.push(cmd)

    def cloneNodes(
        self,
        nodes: list[NodeItem],
        positions: list[QtCore.QPointF],
    ):
        self.undo_stack.beginMacro("clone nodes")

        old_to_new_inputs: dict[InputPort, InputPort] = {}
        old_to_new_outputs: dict[InputPort, InputPort] = {}
        new_connections = []
        for node, pos in zip(nodes, positions):
            new_node = node.clone()
            new_node.setPos(pos)

            cmd = commands.AddItemToSceneCommand(self.scene, new_node)
            self.undo_stack.push(cmd)

            for old, new in zip(node.iterInputs(), new_node.iterInputs()):
                old_to_new_inputs[old] = new

            for old, new in zip(node.iterOutputs(), new_node.iterOutputs()):
                old_to_new_outputs[old] = new

        # NOTE: port positions won't be correct unless an update is run. without this
        #       connection start/end points may have offsets.
        QtCore.QCoreApplication.processEvents()

        for old_output, new_output in old_to_new_outputs.items():
            for connection in old_output.connections():

                new_input = old_to_new_inputs.get(connection.inputPort())
                if not new_input:
                    continue

                new_connections.append(self.createConnection(new_output, new_input))

        self.undo_stack.endMacro()

    def moveNodes(
        self,
        nodes: list[NodeItem],
        delta: QtCore.QPointF,
        drag_id: str,
    ):
        command = commands.MoveItemsCommand(nodes, delta, drag_id)
        self.undo_stack.push(command)

    def createDeleteSelectedAction(self):
        action = QtGui.QAction("delete selected")
        action.setShortcut("Delete")
        action.triggered.connect(lambda: self.removeNodes(self.selectedNodes()))
        return action
