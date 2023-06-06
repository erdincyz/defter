# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

import os
from PySide6.QtWidgets import QTabBar, QToolButton, QSizePolicy
from PySide6.QtCore import Signal, Qt


#######################################################################
class TabBar(QTabBar):
    tabLeftMiniButtonClicked = Signal()
    filesDroppedToTabBar = Signal(list)

    def __init__(self, parent=None):

        super(TabBar, self).__init__(parent)

        self.setMovable(True)
        self.setTabsClosable(True)
        self.setSelectionBehaviorOnRemove(QTabBar.SelectionBehavior.SelectPreviousTab)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        # self.setElideMode(Qt.ElideNone)

        # self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        # self.setMinimumWidth(200)
        # self.setDrawBase(1)
        # self.setGeometry(QtCore.QRect(5, 5, 700, 370)) #(5, 5, 425, 451))
        # self.setIconSize(QtCore.QSize(20,20))
        # self.setTabTextColor()
        self.setAcceptDrops(True)

        # add buffer btn #
        self.createMiniButton()
        # self.setDrawBase(True)
        self._draggedDroppedFilePaths = []

    # ---------------------------------------------------------------------
    def createMiniButton(self):
        self.addTabButton = QToolButton(self)
        self.addTabButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.addTabButton.setGeometry(0, 0, 15, 15)
        # self.addTabButton.setGeometry(0, 0, 20, 33)
        # self.addTabButton.setMinimumSize(20, 33)
        # self.addTabButton.setMaximumSize(20, 33)

        self.addTabButton.setText("+")

        # addTabButton.clicked.connect(self.miniButtonClicked)
        self.addTabButton.clicked.connect(lambda: self.tabLeftMiniButtonClicked.emit())

        # self.parent().setCornerWidget(self.addTabButton, Qt.TopLeftCorner)
        # self.parent().setCornerWidget(addTabButton)
        # return addTabButton

        # self.moveAddButton()

    # # ---------------------------------------------------------------------
    # @pyqtSlot()
    # def miniButtonClicked(self):
    #     self.tabLeftMiniButtonClicked.emit()

    # def sizeHint(self):
    #     """ add minibutton's width to the tab bar"""
    #     sizeHint = QTabBar.sizeHint(self)
    #     width = sizeHint.width()
    #     height = sizeHint.height()
    #     return QSize(width + 20, height)
    #
    # def resizeEvent(self, event):
    #     super(TabBar, self).resizeEvent(event)
    #     self.moveAddButton()

    # def tabLayoutChange(self):

    #     super(TabBar, self).tabLayoutChange()
    #     self.moveAddButton()

    # def moveAddButton(self):
    #
    #     if self.elideMode() == Qt.ElideNone:
    #         # rect = self.tabRect(0)
    #         # pad = self.count() * rect.width()
    #         # self.addTabButton.setGeometry(pad, 0, 15, 15)
    #         pad = 0
    #         for i in range(self.count()):
    #             pad += self.tabRect(i).width()
    #
    #         h = self.geometry().top()
    #         w = self.width()
    #         # print(pad)
    #
    #         if pad >= w:
    #             self.addTabButton.move(w - 54, h)
    #         else:
    #             self.addTabButton.move(pad, h)
    #     else:
    #                     # rect = self.tabRect(0)
    #         # pad = self.count() * rect.width()
    #         # self.addTabButton.setGeometry(pad, 0, 15, 15)
    #         pad = 0
    #         for i in range(self.count()):
    #             pad += self.tabRect(i).width()
    #
    #         h = self.geometry().top()
    #         w = self.width()
    #
    #         if pad > w:
    #             self.addTabButton.move(w - 54, h)
    #         if pad == w:
    #             # self.addTabButton.move(w - 20, h)
    #             # self.addTabButton.setGeometry(0,0,20,31)
    #             self.parent().setCornerWidget(self.addTabButton)
    #         else:
    #             self.addTabButton.move(pad, h)

    # # ---------------------------------------------------------------------
    # def tabInserted(self, idx):
    #     super(TabBar, self).tabInserted(idx)
    #     # self.moveAddButton()
    #     print(self.width())
    #
    # # ---------------------------------------------------------------------
    # def tabRemoved(self, idx):
    #     super(TabBar, self).tabRemoved(idx)
    #     self.moveAddButton()

    # # ---------------------------------------------------------------------
    # def tabInserted(self, *args, **kwargs):
    #     """tabların left tab button kısmına yeni tab yarat buttonu ekler"""
    #
    #     self.setTabButton(args[0], QTabBar.LeftSide, self.createMiniButton())
    #
    #     super(TabBar, self).tabInserted(*args, **kwargs)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            index = self.tabAt(event.pos())
            if not index == -1:
                self.tabCloseRequested.emit(index)
                return
        # return QTabBar.mouseReleaseEvent(self, event)
        super(TabBar, self).mouseReleaseEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        super(TabBar, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        # if event.button() == Qt.RightButton:
        #     self.selectedTabForSplit.emit(self.tabAt(event.pos()), self)
        # if event.button() == Qt.LeftButton:
        #     self.parent().widget(self.currentIndex()).setFocus()

        # print self.tabButton(0,QTabBar.LeftSide)

        index = self.tabAt(event.pos())
        self.setCurrentIndex(index)
        self.parent().widget(self.currentIndex()).setFocus()
        super(TabBar, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def dragEnterEvent(self, event):

        # rect = self.tabRect(self.currentIndex())
        # drag = QDrag(self)
        # drag.setMimeData(event.mimeData())
        #
        # pixTabBackground = QPixmap(rect.width(), rect.height())
        # # pixTabBackground.fill(QColor(0, 100, 255))
        # pixTabBackground.fill(self.palette().color(QPalette.Button))
        #
        # painterTab = QPainter(pixTabBackground)
        #
        # # font = QFont("system", 9)
        # font = QFont("sans", 9)
        # painterTab.setFont(font)
        # painterTab.setPen(self.tabTextColor(self.currentIndex()))
        # pixFont = QPixmap(rect.width(), rect.height())
        # painterTab.drawText(pixFont.rect(), Qt.AlignCenter, self.tabText(self.currentIndex()))
        # painterTab.end()
        # # painter.setRenderHints(QPainter.TextAntialiasing)
        # drag.setHotSpot(QPoint(12, 12))
        # drag.setPixmap(pixTabBackground.scaled(128, 128, Qt.KeepAspectRatio))
        # drag.exec_()
        # print("asdasdasdasd")

        # self.parent().currentWidget().setFocus()
        self._draggedDroppedFilePaths = []
        if event.mimeData().hasUrls:
            for url in event.mimeData().urls():
                filePath = url.toLocalFile()
                if os.path.splitext(filePath)[1][1:].lower() == "def":
                    self._draggedDroppedFilePaths.append(filePath)

            if self._draggedDroppedFilePaths:
                event.accept()
            else:
                event.ignore()
        else:
            super(TabBar, self).dragEnterEvent(event)

    # ---------------------------------------------------------------------
    def dragMoveEvent(self, event):
        self.setCurrentIndex(self.tabAt(event.pos()))
        # event.accept()
        super(TabBar, self).dragMoveEvent(event)

    # ---------------------------------------------------------------------
    def dropEvent(self, event):
        if self._draggedDroppedFilePaths:
            self.filesDroppedToTabBar.emit(self._draggedDroppedFilePaths)
        super(TabBar, self).dropEvent(event)
