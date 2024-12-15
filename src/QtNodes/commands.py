from __future__ import annotations
import typing
import uuid
from typing import no_type_check_decorator

from PySide6 import QtWidgets, QtCore, QtGui
from QtNodes.connection import ConnectionItem

if typing.TYPE_CHECKING:
    from QtNodes.node import NodeItem


class CommandIDs:
    MoveCommand = 1


class AddItemToSceneCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        scene: QtWidgets.QGraphicsScene,
        instance: QtWidgets.QGraphicsItem,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.scene = scene
        self.instance = instance

    def redo(self):
        self.scene.addItem(self.instance)

    def undo(self):
        self.scene.removeItem(self.instance)


class RemoveItemFromSceneCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        scene: QtWidgets.QGraphicsScene,
        instance: QtWidgets.QGraphicsItem,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.scene = scene
        self.instance = instance

    def redo(self):
        self.scene.removeItem(self.instance)

    def undo(self):
        self.scene.addItem(self.instance)


class MoveItemsCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        items: list[QtWidgets.QGraphicsItem],
        delta: QtCore.QPointF,
        drag_id: typing.Hashable = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.items = items
        self.drag_id = drag_id or uuid.uuid4().int
        self.delta = delta

    def id(self):
        return CommandIDs.MoveCommand

    def redo(self):
        x, y = self.delta.toTuple()
        for item in self.items:
            item.moveBy(x, y)

    def undo(self):
        x, y = self.delta.toTuple()
        for item in self.items:
            item.moveBy(-x, -y)

    def mergeWith(self, other):
        if not isinstance(other, MoveItemsCommand):
            return False
        if other.drag_id != self.drag_id:
            return False

        self.delta += other.delta
        return True


class RemoveNodeCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        scene: QtWidgets.QGraphicsScene,
        node: NodeItem,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.scene = scene
        self.node = node
        self.sub_commands = []

        for port in node.iterInputs():
            for connection in port.iterConnections():
                self.sub_commands.append(RemoveConnectionCommand(scene, connection))

        for port in node.iterOutputs():
            for connection in port.iterConnections():
                self.sub_commands.append(RemoveConnectionCommand(scene, connection))

        self.sub_commands.append(RemoveItemFromSceneCommand(scene, node))

    def redo(self):
        for command in self.sub_commands:
            command.redo()

    def undo(self):
        for command in reversed(self.sub_commands):
            command.undo()


class RemoveConnectionCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        scene: QtWidgets.QGraphicsScene,
        connection: ConnectionItem,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.scene = scene
        self.connection = connection

    def redo(self):
        self.connection.detache()
        self.scene.removeItem(self.connection)

    def undo(self):
        self.scene.addItem(self.connection)
        self.connection.attach()
