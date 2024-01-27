# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '8/1/15'

from PySide6.QtCore import (Qt, QRect, Signal, QSize)
from PySide6.QtGui import (QPainter, QPen)
from PySide6.QtWidgets import (QRubberBand, QWidget)


#######################################################################
class MyRubberBand(QRubberBand):

    # ---------------------------------------------------------------------
    def __init__(self, shape=QRubberBand.Rectangle, parent=None):
        super(MyRubberBand, self).__init__(shape, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # defaultFlags = self.windowFlags()
        # self.setWindowFlags(defaultFlags | Qt.ToolTip)
        # self.setWindowFlags(Qt.ToolTip)
        # self.setStyleSheet("selection-background-color: transparent")
        self._pen = QPen(Qt.GlobalColor.blue, 3, Qt.PenStyle.DotLine)

    # ---------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self._pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(event.rect().adjusted(0, 0, -1, -1))


#######################################################################
class TamEkranWidget_CM_On(QWidget):
    rubberBandReleased = Signal(QRect)
    esc_key_pressed = Signal()

    # ---------------------------------------------------------------------
    # def __init__(self, texts, parent=None):
    def __init__(self, is_compositing_manager_running=True, parent=None):

        super(TamEkranWidget_CM_On, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # self.setPalette(Qt.transparent)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.istek_mouse_releaseden_mi_geliyor = False
        self.rubberBand = None

        # self.setWindowOpacity(0.01)
        self.setWindowOpacity(0.7)
        # self.setStyleSheet("QWidget{background:transparent;}")
        # self.setStyleSheet("QWidget{background-color:none;}")
        self.showFullScreen()

    # ---------------------------------------------------------------------
    def closeEvent(self, event):
        if self.istek_mouse_releaseden_mi_geliyor:
            self.rubberBandReleased.emit(QRect(self.rubberBand.geometry()))
        event.accept()
        # super(TamEkranWidget_CM_Off, self).closeEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        self.origin = event.pos()

        if not self.rubberBand:
            # self.rubberBand = QRubberBand(QRubberBand.Rectangle)
            # self.rubberBand = MyRubberBand(QRubberBand.Rectangle)
            # TODO: bunu selfsiz de deneyelim compositor acık iken.
            self.rubberBand = MyRubberBand(QRubberBand.Shape.Rectangle, self)
            # self.rubberBand = MyRubberBand(QRubberBand.Rectangle)
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

        super(TamEkranWidget_CM_On, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        # self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

        # self.rubberBand.setGeometry(QRect(self.mapToGlobal(self.origin),
        #                                   self.mapToGlobal(event.pos())).normalized())

        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

        # self.rubberBand.setGeometry(QRect(self.mapToGlobal(QCursor.pos()),
        #                                   self.mapToGlobal(event.pos())).normalized())

        super(TamEkranWidget_CM_On, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        # self.rubberBand.close()
        # self.close()
        # self.setAttribute(Qt.WA_PaintOnScreen, False)
        # self.rubberBandReleased.emit(self.rubberBand.geometry())
        # super(TamEkranWidget_CM_On, self).mouseReleaseEvent(event)
        self.istek_mouse_releaseden_mi_geliyor = True
        self.close()
        self.deleteLater()

    # super(TamEkranWidget_CM_On, self).mouseReleaseEvent(event)
    # return QWidget.mouseReleaseEvent(event)

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Escape:
            self.esc_key_pressed.emit()
        super(TamEkranWidget_CM_On, self).keyPressEvent(event)
        self.close()
        self.deleteLater()
