__all__ = ["NodeGraphView"]

from qtpy import QtWidgets, QtGui, QtCore, QtOpenGLWidgets


class NodeGraphView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.zoom_factor = 1.15
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(self.DragMode.NoDrag)
        self.setViewport(QtOpenGLWidgets.QOpenGLWidget())
        self.setMouseTracking(True)
        self.__clicked_item = None

    def wheelEvent(self, event):
        zoom_scale = (
            self.zoom_factor if event.angleDelta().y() > 0 else 1 / self.zoom_factor
        )
        self.scale(zoom_scale, zoom_scale)

    def mousePressEvent(self, event):
        scene_position = self.mapToScene(event.position().toPoint())
        x, y = scene_position.toTuple()
        self.__clicked_item = self.scene().itemAt(x, y, QtGui.QTransform())

        alt_mod = event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier

        if self.__clicked_item is None:

            if alt_mod:
                self.setDragMode(self.DragMode.ScrollHandDrag)
            else:
                self.setDragMode(self.DragMode.RubberBandDrag)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(self.DragMode.NoDrag)
        self.__clicked_item = None
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):

        super().mouseMoveEvent(event)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().brush(self.palette().ColorRole.Dark))
        painter.drawRect(rect)
        draw_grid(painter, rect, 25)


def draw_grid(painter, rect, grid_size):
    """
    Draw a grid in the given rect with the given grid size.
    """
    grid_lines = []

    left = int(rect.left()) - (int(rect.left()) % grid_size)
    top = int(rect.top()) - (int(rect.top()) % grid_size)

    x = left
    while x < rect.right():
        if x != 0:
            grid_lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
        x += grid_size

    y = top
    while y < rect.bottom():
        if y != 0:
            grid_lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
        y += grid_size

    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 25)))
    painter.drawLines(grid_lines)

    # draw x and y axis
    painter.setPen(QtGui.QPen(QtGui.QColor(0, 127, 0, 64), 2))
    painter.drawLine(0, rect.top(), 0, rect.bottom())
    painter.setPen(QtGui.QPen(QtGui.QColor(127, 0, 0, 64), 2))
    painter.drawLine(rect.left(), 0, rect.right(), 0)
