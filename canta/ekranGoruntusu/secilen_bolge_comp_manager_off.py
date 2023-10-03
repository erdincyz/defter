# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '8/1/15'

from PySide6.QtCore import (Qt, QRect, Signal, QSize, QTimer)
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QRubberBand, QApplication, QLabel)


#######################################################################
class MyRubberBand(QRubberBand):
    rubberBandHidden = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, shape=QRubberBand.Shape.Rectangle, parent=None):
        super(MyRubberBand, self).__init__(shape, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # defaultFlags = self.windowFlags()
        # self.setWindowFlags(defaultFlags | Qt.ToolTip)
        # self.setWindowFlags(Qt.ToolTip)
        # self.setStyleSheet("selection-background-color: transparent")

    # ---------------------------------------------------------------------
    def hideEvent(self, event):
        super(MyRubberBand, self).hideEvent(event)
        QApplication.processEvents()
        QTimer.singleShot(50, self.rubberBandHidden.emit)


#######################################################################
class TamEkranWidget_CM_Off(QLabel):
    rubberBandReleased = Signal(QRect)
    esc_key_pressed = Signal()

    # ---------------------------------------------------------------------
    # def __init__(self, texts, parent=None):
    def __init__(self, parent=None):

        super(TamEkranWidget_CM_Off, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        # self.setAttribute(Qt.WA_PaintOnScreen, True)
        self.setAutoFillBackground(True)
        # self.setStyleSheet("background-color:none;")
        # self.setAutoFillBackground(True)

        # self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        # self.rubberBand = MyRubberBand(QRubberBand.Rectangle, self)
        self.rubberBand = MyRubberBand(QRubberBand.Shape.Rectangle)
        self.rubberBand.rubberBandHidden.connect(self.act_rubberband_hidden)

        self.alan = QRect()

        self.screen = QApplication.primaryScreen()

        # self.setAutoFillBackground(True)

        # self.setWindowOpacity(0.01)
        # self.setWindowOpacity(0)
        # self.setStyleSheet("QWidget{background:transparent;}")
        # self.setStyleSheet("QWidget{background-color:none;}")

        self.showFullScreen()

    # ---------------------------------------------------------------------
    def act_rubberband_hidden(self):
        # QApplication.processEvents()
        QTimer.singleShot(0, lambda: self.rubberBandReleased.emit(self.alan))

    # ---------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.screen.grabWindow(0))
        # super(TamEkranWidget_CM_Off, self).paintEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        self.origin = event.pos()

        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

        super(TamEkranWidget_CM_Off, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

        # self.repaint()
        super(TamEkranWidget_CM_Off, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        self.alan = self.rubberBand.geometry()
        self.rubberBand.hide()

        # super(TamEkranWidget_CM_Off, self).mouseReleaseEvent(event)
        # return QWidget.mouseReleaseEvent(event)

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Escape:
            self.esc_key_pressed.emit()
        super(TamEkranWidget_CM_Off, self).keyPressEvent(event)
        self.close()
        self.deleteLater()
