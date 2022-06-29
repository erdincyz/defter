# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '26/1/22'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy


#######################################################################
class YuzenWidget(QWidget):

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(YuzenWidget, self).__init__(parent)

        # self.setMinimumHeight(400)
        self.setAutoFillBackground(True)
        # self.setStyleSheet("QWidget {background-color: #ccc;}")
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setSizeGripEnabled(True)
        self.setStatusTip(self.tr("Move with left mouse button, resize with right mouse button."))
        # self.setToolTip(self.tr("Move with left mouse button, resize with right mouse button."))

        self.setFocusPolicy(Qt.WheelFocus)

        self.mPos = QPoint()
        self.sagClick = False
        self.solClick = False

        self.anaLay = QVBoxLayout(self)
        self.anaLay.setContentsMargins(1, 0, 1, 1)
        self.anaLay.setSpacing(1)
        # self.anaLay.setSizeConstraint(QVBoxLayout.SetFixedSize)
        baslikLay = QHBoxLayout()
        baslikLay.setContentsMargins(0, 0, 0, 0)
        baslikLay.setSpacing(0)

        # tasiWidget = QWidget(self)
        # tasiWidget.setMinimumHeight(30)
        # tasiWidget.setMinimumWidth(50)

        self.kapatBtn = QPushButton(self)
        self.kapatBtn.setFlat(True)
        self.kapatBtn.setText("X")
        self.kapatBtn.setStyleSheet("QPushButton {background-color: #ddd;}")
        # self.kapatBtn.setMinimumHeight(15)
        # self.kapatBtn.setMinimumWidth(30)
        self.kapatBtn.setMaximumWidth(30)
        # self.kapatBtn.clicked.connect(self.close)
        self.kapatBtn.clicked.connect(self.hide)

        self.baslikEtiket = QLabel(self)
        self.baslikEtiket.setStyleSheet("QLabel {background-color: #ddd;}")
        baslikLay.addWidget(self.baslikEtiket)
        # baslikLay.addStretch()
        # baslikLay.addWidget(tasiWidget)
        baslikLay.addWidget(self.kapatBtn)

        self.anaLay.addLayout(baslikLay)

        self.baslikEtiket.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
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

        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
            self.solClick = True
            self.setCursor(Qt.ClosedHandCursor)

        if event.button() == Qt.RightButton:
            self.sagDragx = event.x()
            self.sagDragy = event.y()
            self.enSagX = self.width()
            self.enAltY = self.height()
            self.sagClick = True
            self.setCursor(Qt.SizeAllCursor)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.LeftButton:
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
        self.setCursor(Qt.ArrowCursor)
