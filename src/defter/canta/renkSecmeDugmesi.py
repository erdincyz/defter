# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '8/3/23'

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import QApplication, QPushButton
from . import icons_rc


#######################################################################
class RenkSecmeDugmesi(QPushButton):
    renkDegisti = Signal(QColor, str)
    # renk_secildi = Signal(QColor)
    esc_key_pressed = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(RenkSecmeDugmesi, self).__init__(parent)
        # self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFlat(True)
        self.setIcon(QIcon(":icons/renk-sec.png"))

        self.setFixedWidth(16)
        self.setFixedHeight(16)
        self.setToolTip(self.tr("Click and drag to select color from screen"))
        self.setStatusTip(self.tr("Click and drag to select color from screen"))

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
        super(RenkSecmeDugmesi, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        pos = self.mapToGlobal(event.pos())
        ekran = QApplication.screenAt(pos)
        if not ekran:
            ekran = QApplication.primaryScreen()
        rect = ekran.geometry()
        pix = ekran.grabWindow(0, pos.x() - rect.x(), pos.y() - rect.y(), 1, 1)
        i = pix.toImage()
        col = i.pixelColor(0, 0)
        # bilgi = f"X: {pos.x()}  Y: {pos.y()}  -  R: {col.red()}  G: {col.green()}  B: {col.blue()}"
        bilgi = f"xy = ({pos.x()}, {pos.y()})    rgb=({col.red()}, {col.green()}, {col.blue()})"
        self.renkDegisti.emit(col, bilgi)

        super(RenkSecmeDugmesi, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        pos = self.mapToGlobal(event.pos())
        ekran = QApplication.screenAt(pos)
        if not ekran:
            ekran = QApplication.primaryScreen()
        rect = ekran.geometry()
        pix = ekran.grabWindow(0, pos.x() - rect.x(), pos.y() - rect.y(), 1, 1)
        i = pix.toImage()
        col = i.pixelColor(0, 0)
        bilgi = f"xy = ({pos.x()}, {pos.y()})    rgb=({col.red()}, {col.green()}, {col.blue()})"
        self.renkDegisti.emit(col, bilgi)

        super(RenkSecmeDugmesi, self).mouseReleaseEvent(event)

    # # ---------------------------------------------------------------------
    # def keyPressEvent(self, event):
    #
    #     if event.key() == Qt.Key.Key_Escape:
    #         # self.esc_key_pressed.emit()
    #         self.renkDegisti.emit(self.eski_renk)
    #     super(RenkSecmeDugmesi, self).keyPressEvent(event)
    #     self.close()
    #     self.deleteLater()
