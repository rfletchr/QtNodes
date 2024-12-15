from qtpy import QtWidgets, QtGui

from QtNodes.view import NodeGraphView
from QtNodes.controller import NodeGraphController
from QtNodes.factory import NodeType, PortType


def main():
    app = QtWidgets.QApplication()

    format = QtGui.QSurfaceFormat()
    format.setSamples(4)  # Enable 4x multisampling for anti-aliasing
    QtGui.QSurfaceFormat.setDefaultFormat(format)

    controller = NodeGraphController()
    view = NodeGraphView()
    view.setScene(controller.scene)

    controller.factory.port_types["image"] = PortType(
        "image", color=QtGui.QColor(127, 32, 32)
    )
    controller.factory.node_types["merge"] = NodeType(
        "merge", "image", {"a": "image", "b": "image"}, {"out": "image"}
    )
    controller.factory.node_types["constant"] = NodeType(
        "constant", "image", {}, {"image": "image"}
    )

    controller.createNode("merge")
    controller.createNode("constant")

    undo_action = controller.undo_stack.createUndoAction(app)
    undo_action.setShortcut("ctrl+z")
    view.addAction(undo_action)

    redo_action = controller.undo_stack.createRedoAction(app)
    redo_action.setShortcut("ctrl+y")
    view.addAction(redo_action)

    delete_action = controller.createDeleteSelectedAction()
    view.addAction(delete_action)

    view.show()
    app.exec()


if __name__ == "__main__":
    main()
