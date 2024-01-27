# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '10/8/23'
__author__ = 'E. Y.'

import sys

from PySide6.QtCore import QCoreApplication, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QPushButton, QStylePainter, QStyle, QStyleOptionButton, QFrame, QHBoxLayout, QApplication, QSizePolicy


#######################################################################
class DikeyDugme(QPushButton):
    def __init__(self, text, parent, yon="asagi"):
        super(DikeyDugme, self).__init__(text, parent)
        self.yon = yon
        # if self.yon == "sag":
        #     self.dondurme_acisi = 270
        #     self.kayma = (-1 * self.height(), 0)
        # elif self.yon == "sol":
        #     self.dondurme_acisi = 90
        #     self.kayma = (0, -1 * self.width())

        self.ufakBoyut = QSize(16, 75)
        self.normalBoyut = QSize(16, 100)
        # self.setFixedSize(self.normalBoyut)
        self.icerikW = None
        # self.show()

        # self.btnYuzdur = QPushButton("~", self)
        # self.btnYuzdur.setFixedSize(20, 20)
        # self.btnYuzdur.setFlat(True)
        # self.btnYuzdur.setAutoFillBackground(True)

        self.setFlat(True)
        # self.setAutoFillBackground(True)
        self.setContentsMargins(0, 0, 0, 0)
        # self.setAutoFillBackground(True)

        # self.renk_degistir(acik_mi=True)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        font = self.font()
        font.setPointSizeF(7)
        self.setFont(font)

        # self.setCheckable(True)
        # self.setChecked(False)

    # ---------------------------------------------------------------------
    def renk_degistir(self, acik_mi=True):

        if acik_mi:
            stil = """
            QPushButton{
                color:#fff;
                background-color: #99aabb;
                background-color: #aabcee;
                border: 0;
                padding: 3px;
                border-radius: 3px;
            }
            QPushButton:hover{
                background-color: #a4b6c8;
            }

            QPushButton:checked{
                background-color: #ced5e1;

            }
            QPushButton:checked:hover{
                background-color: #ced5e1;
            }

            """
        else:
            stil = """
            QPushButton{
                color:#5b5b5b;
                background-color: #bcbcbc;
                background-color: #aaa;
                border: 0;
                padding: 3px;
                border-radius: 3px;
            }
            QPushButton:hover{
                background-color: #ababab;
            }

            """
            # QPushButton:pressed{
            # background-color: #afc3d6;
            # }

        self.setStyleSheet(stil)

    # ---------------------------------------------------------------------
    def renk_degistir_belki(self, acik_mi=True):

        if acik_mi:
            self.renkYazi = QColor(135, 135, 135)
            self.renkArkaplan = QColor(250, 250, 250)
        else:
            self.renkYazi = QColor(165, 165, 165)
            self.renkArkaplan = QColor(220, 220, 220)
            # self.renkArkaplan2 = QColor(138, 165, 195)

        self.renkYazi2 = QColor(125, 125, 125)
        self.renkArkaplan2 = QColor(158, 185, 215)
        self.renkArkaplan2 = QColor(255, 255, 255)

        p = self.palette()
        p.setColor(self.foregroundRole(), self.renkYazi)
        p.setColor(self.backgroundRole(), self.renkArkaplan)
        self.setPalette(p)
        # p.setColor(self.btnYuzdur.foregroundRole(), self.renkYazi2)
        # p.setColor(self.btnYuzdur.backgroundRole(), self.renkArkaplan2)
        # self.btnYuzdur.setPalette(p)

    # ---------------------------------------------------------------------
    def renk_degistir_ilk(self, acik_mi=True):

        if acik_mi:
            self.renkYazi = QColor(255, 255, 255)
            self.renkArkaplan = QColor(153, 170, 187)
        else:
            self.renkYazi = QColor(190, 190, 190)
            self.renkArkaplan = QColor(133, 150, 167)
            # self.renkArkaplan2 = QColor(138, 165, 195)

        self.renkYazi2 = QColor(255, 255, 255)
        self.renkArkaplan2 = QColor(158, 185, 215)

        p = self.palette()
        p.setColor(self.foregroundRole(), self.renkYazi)
        p.setColor(self.backgroundRole(), self.renkArkaplan)
        self.setPalette(p)
        # p.setColor(self.btnYuzdur.foregroundRole(), self.renkYazi2)
        # p.setColor(self.btnYuzdur.backgroundRole(), self.renkArkaplan2)
        # self.btnYuzdur.setPalette(p)

    # ---------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QStylePainter(self)
        if self.yon == "yukari":
            painter.rotate(270)
            painter.translate(-1 * self.height(), 0)
        if self.yon == "asagi":
            painter.rotate(90)
            painter.translate(0, -1 * self.width())
        painter.drawControl(QStyle.ControlElement.CE_PushButton, self.getSyleOptions())

    # ---------------------------------------------------------------------
    def minimumSizeHint(self):
        size = super(DikeyDugme, self).minimumSizeHint()
        size.transpose()
        return size

    # ---------------------------------------------------------------------
    def sizeHint(self):
        size = super(DikeyDugme, self).sizeHint()
        size.transpose()
        return size

    # ---------------------------------------------------------------------
    def getSyleOptions(self):
        options = QStyleOptionButton()
        options.initFrom(self)
        size = options.rect.size()
        size.transpose()
        options.rect.setSize(size)
        options.features = QStyleOptionButton.ButtonFeature.None_
        if self.isFlat():
            options.features |= QStyleOptionButton.Flat
        if self.menu():
            options.features |= QStyleOptionButton.HasMenu
        if self.autoDefault() or self.isDefault():
            options.features |= QStyleOptionButton.AutoDefaultButton
        if self.isDefault():
            options.features |= QStyleOptionButton.DefaultButton
        if self.isDown() or (self.menu() and self.menu().isVisible()):
            options.state |= QStyle.StateFlag.State_Sunken
        if self.isChecked():
            options.state |= QStyle.StateFlag.State_On
        if not self.isFlat() and not self.isDown():
            options.state |= QStyle.StateFlag.State_Raised

        options.text = self.text()
        options.icon = self.icon()
        options.iconSize = self.iconSize()
        return options

    # # ---------------------------------------------------------------------
    # def enterEvent(self, event):
    #     super(DikeyDugme, self).enterEvent(event)
    #     self.setMinimumWidth(20)
    #
    # # ---------------------------------------------------------------------
    # def leaveEvent(self, event):
    #     super(DikeyDugme, self).leaveEvent(event)
    #     self.setMinimumWidth(5)

    # # ---------------------------------------------------------------------
    # def mousePressEvent(self, event):
    #     super(DikeyDugme, self).mousePressEvent(event)
    #
    #     self._mousePressPosG = None
    #     self._mouseMovePosG = None
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self._mousePressPosG = event.globalPosition().toPoint()
    #         self._mouseMovePosG = self._mousePressPosG

    def mouseMoveEvent(self, event):
        super(DikeyDugme, self).mouseMoveEvent(event)

        # if event.buttons() == Qt.MouseButton.LeftButton:
        #     # adjust offset from clicked point to origin of widget
        #     eskiPos = self.pos()
        #     eskiPosMappedToGlobal = self.mapToGlobal(eskiPos)
        #     eskiPosGlobal = event.globalPosition().toPoint()
        #     fark = eskiPosGlobal - self._mouseMovePosG
        #     yeniPos = self.mapFromGlobal(eskiPosMappedToGlobal + fark)
        #     self.move(eskiPos.x(), yeniPos.y())
        #
        #     self._mouseMovePosG = eskiPosGlobal

        # if event.buttons() == Qt.MouseButton.RightButton:

        # if event.buttons() == Qt.MouseButton.LeftButton:
        #     drag = QDrag(self)
        #     mime = QMimeData()
        #     drag.setMimeData(mime)
        #
        #     pixmap = QPixmap(self.size())
        #     self.render(pixmap)
        #     drag.setPixmap(pixmap)
        #
        #     drag.exec(Qt.DropAction.MoveAction)


#######################################################################
class Main(QFrame):
    def __init__(self):
        QFrame.__init__(self)

        self.application = QCoreApplication.instance()
        self.layout = QHBoxLayout()
        self.button = DikeyDugme("Merhaba", self, yon="asagi")
        self.button2 = DikeyDugme("Merhaba", self, yon="yukari")
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button2)
        self.setLayout(self.layout)


# ---------------------------------------------------------------------
if __name__ == '__main__':
    application = QApplication(sys.argv)
    application.main = Main()
    application.main.show()
    sys.exit(application.exec())
