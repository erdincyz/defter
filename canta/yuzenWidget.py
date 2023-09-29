# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '26/1/22'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy


#######################################################################
class YuzenWidget(QWidget):

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(YuzenWidget, self).__init__(parent)

        self.renkYazi = QColor(255, 255, 255)
        # self.renkArkaplan = QColor(200, 205, 210)
        self.renkArkaplan = QColor(153, 170, 187)

        # self.setMinimumHeight(400)
        self.setAutoFillBackground(True)
        # self.setStyleSheet("QWidget {background-color: #ccc;}")
        self.setContentsMargins(0, 0, 0, 0)
        # ~ self.setWindowFlags(Qt.FramelessWindowHint|Qt.NoDropShadowWindowHint| Qt.Tool)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        # self.setSizeGripEnabled(True)
        self.setStatusTip(self.tr("Move with left mouse button, resize with right mouse button."))
        # self.setToolTip(self.tr("Move with left mouse button, resize with right mouse button."))

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.mPos = QPoint()
        self.sagClick = False
        self.solClick = False

        self.anaLay = QVBoxLayout(self)
        self.anaLay.setContentsMargins(1, 0, 1, 1)
        self.anaLay.setSpacing(1)
        # self.anaLay.setSizeConstraint(QVBoxLayout.SetFixedSize)

        self.baslikWidget = QWidget(self)
        self.baslikWidget.setFixedHeight(20)
        self.baslikWidget.setContentsMargins(0, 0, 0, 0)
        self.baslikWidget.setAutoFillBackground(True)

        p = self.baslikWidget.palette()
        p.setColor(self.baslikWidget.foregroundRole(), self.renkYazi)
        p.setColor(self.baslikWidget.backgroundRole(), self.renkArkaplan)
        self.baslikWidget.setPalette(p)

        self.baslikEtiket = QLabel(self.baslikWidget)
        self.baslikEtiket.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QHBoxLayout(self.baslikWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        btnKapat = QPushButton("x", self.baslikWidget)
        btnKapat.setFixedWidth(20)
        btnKapat.setFlat(True)
        btnKapat.setAutoFillBackground(True)
        btnKapat.clicked.connect(self.hide)

        p = btnKapat.palette()
        p.setColor(btnKapat.foregroundRole(), self.renkYazi)
        p.setColor(btnKapat.backgroundRole(), self.renkArkaplan)
        btnKapat.setPalette(p)

        # lay.addStretch()
        lay.addSpacing(36)
        lay.addWidget(self.baslikEtiket)
        lay.addWidget(btnKapat)

        self.anaLay.addWidget(self.baslikWidget)

        self.icerikToplamMinWidth = 0
        self.icerikToplamMinHeight = 0

    # ---------------------------------------------------------------------
    def yazBaslik(self, yazi):
        self.baslikEtiket.setText(yazi)

    # ---------------------------------------------------------------------
    def ekleWidget(self, widget):
        # self.resize(widget.size())

        # gripper = QSizeGrip(widget)
        # l = QHBoxLayout(widget)
        #
        # l.setContentsMargins(0, 0, 0, 0)
        # l.addWidget(gripper, 0, Qt.AlignRight | Qt.AlignBottom)

        self.icerikToplamMinWidth += widget.minimumWidth()
        self.icerikToplamMinHeight += widget.minimumHeight()
        self.anaLay.addWidget(widget)
        # self.baslikEtiket.setMinimumWidth(self.icerikToplamMinWidth - self.kapatBtn.maximumWidth())
        self.adjustSize()

    # ---------------------------------------------------------------------
    def addStretchToLayout(self):
        self.anaLay.addStretch()

    # ---------------------------------------------------------------------
    # def sizeHint(self):
    #     return QSize()

    # def resizeEvent(self, event):
    #     super(YuzenWidget, self).resizeEvent(event)

    # ---------------------------------------------------------------------
    # QtGui.QMouseEvent
    def mousePressEvent(self, event) -> None:

        super(YuzenWidget, self).mousePressEvent(event)

        if event.button() == Qt.MouseButton.LeftButton:
            self.mPos = event.pos()
            self.solClick = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

        if event.button() == Qt.MouseButton.RightButton:
            self.sagDragx = event.x()
            self.sagDragy = event.y()
            self.enSagX = self.width()
            self.enAltY = self.height()
            self.sagClick = True
            self.setCursor(Qt.CursorShape.SizeAllCursor)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            fark = event.pos() - self.mPos
            yeniPos = self.pos() + fark
            self.move(yeniPos)

        super(YuzenWidget, self).mousePressEvent(event)

        if self.sagClick:
            x = max(self.icerikToplamMinWidth,
                    self.enSagX + event.x() - self.sagDragx)
            y = max(self.icerikToplamMinHeight,
                    self.enAltY + event.y() - self.sagDragy)
            self.resize(x, y)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(YuzenWidget, self).mouseReleaseEvent(event)
        self.sagClick = False
        self.solClick = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
