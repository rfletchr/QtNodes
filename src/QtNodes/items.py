from qtpy import QtWidgets, QtGui, QtCore


class StaticTextItem(QtWidgets.QGraphicsWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.__text = text
        self.__font_metrics = QtGui.QFontMetricsF(self.font())
        self.__alignment = (
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter
        )

    def sizeHint(self, which, constraint=...):
        return self.__font_metrics.boundingRect(self.__text).size()

    def contains(self, point):
        return False

    def paint(self, painter, option, widget=...):
        painter.setFont(self.font())
        painter.drawText(self.rect(), self.__text, self.__alignment)


from PySide6 import QtWidgets, QtCore


class SceneSpaceShadowEffect(QtWidgets.QGraphicsDropShadowEffect):
    """
    A drop shadow effect which takes the scene space size into account.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._blur_radius = super().blurRadius()
        self._offset = super().offset()
        self.setBlurRadius(0)
        self.setOffset(QtCore.QPointF(5, 5))
        self.setColor(QtGui.QColor(0, 0, 0, 32))

    def blurRadius(self):
        return self._blur_radius

    def offset(self):
        return self._offset

    def setBlurRadius(self, value: float):
        self._blur_radius = value

    def setOffset(self, value: QtCore.QPointF):
        self._offset = value

    def draw(self, painter):
        super().setOffset(self._offset * painter.transform().m11())
        super().setBlurRadius(self._blur_radius * painter.transform().m11())
        super().draw(painter)
