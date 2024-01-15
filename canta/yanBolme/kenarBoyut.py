# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = "10/5/23"
__author__ = "E. Y."

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame


########################################################################
class KenarBoyutSol(QFrame):
    # ---------------------------------------------------------------------
    def __init__(self, splitterW, ust_pencere_boyut, renk=QColor(200, 210, 220), parent=None):
        super(KenarBoyutSol, self).__init__(parent)

        self.setAcceptDrops(True)

        # renkBordo = QColor(200, 150, 160)

        # self.renkYazi = QColor(255, 255, 255)
        self.setAutoFillBackground(True)
        self.renkArkaplan = renk
        self.renk_degistir()

        self.setContentsMargins(0, 0, 0, 0)

        # self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.splitterW = splitterW
        self.ust_pencere_boyut = ust_pencere_boyut
        self.min_height = 150
        self.min_width = 30
        self.mouse_start = None
        # self.height_start = self.splitterW.height()
        self.height_start = self.height()
        self.resizing = False
        self.setMouseTracking(True)

        # self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setCursor(Qt.CursorShape.SizeHorCursor)

        self.show()

    # ---------------------------------------------------------------------
    def renk_degistir(self, renkArkaplan=None):

        p = self.palette()
        # p.setColor(self.foregroundRole(), self.renkYazi)
        # ozellikle boyle yapildi, anlik widgeti baska renge boyayabiliyoruz
        # renk yoksa yine eski rengine don anlamında
        if renkArkaplan:
            p.setColor(self.backgroundRole(), renkArkaplan)
        else:
            p.setColor(self.backgroundRole(), self.renkArkaplan)
        self.setPalette(p)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        super(KenarBoyutSol, self).mousePressEvent(event)
        self.resizing = True
        self.width_start = self.splitterW.width()
        self.mouse_start = event.globalPos()

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        super(KenarBoyutSol, self).mouseMoveEvent(event)
        max_width = self.ust_pencere_boyut.width() // 2
        if self.resizing:
            delta = event.globalPos() - self.mouse_start
            width = self.width_start + delta.x()

            width = max(width, self.min_width)
            width = min(width, max_width)
            # self.splitterW.setFixedWidth(width)

            for i in range(self.splitterW.count()):
                self.splitterW.widget(i).setMinimumWidthVeEskiMinimumSize(width)

    # # ---------------------------------------------------------------------
    # def genislikleri_esitle(self):
    #     if self.splitterW.count() > 1:
    #         for i in range(self.splitterW.count()):
    #             self.splitterW.widget(i).setMinimumWidth(self.splitterW.width())

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(KenarBoyutSol, self).mouseReleaseEvent(event)
        self.resizing = False

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        super(KenarBoyutSol, self).mouseDoubleClickEvent(event)
        buyult = True
        for i in range(self.splitterW.count()):
            if not self.splitterW.widget(i).kucuk_mu:
                self.splitterW.widget(i).kucult()
                buyult = False
        if buyult:
            for i in range(self.splitterW.count()):
                if self.splitterW.widget(i).kucuk_mu:
                    self.splitterW.widget(i).buyult()

            # self.splitterW.widget(i).setVisible(not self.splitterW.widget(i).isVisible())

    # # ---------------------------------------------------------------------
    # def dragEnterEvent(self, e):
    #     e.accept()
    #
    # # ---------------------------------------------------------------------
    # def dropEvent(self, e):
    #     pos = e.pos()
    #     widget = e.source()
    #
    #     dugmeAdet = self.parent().dugmeLay.count()
    #     if not dugmeAdet:
    #         self.parent().dugmeLay.addWidget(widget)
    #         self.parent().icerikSplitter.addWidget(widget.yw)
    #
    #     else:
    #         birak = False
    #         for n in range(dugmeAdet):
    #             w = self.parent().dugmeLay.itemAt(n).widget()
    #             birak = pos.y() < w.y() + w.size().height() // 2
    #
    #             if birak:
    #                 self.parent().dugmeLay.insertWidget(n-1, widget)
    #                 self.parent().icerikSplitter.insertWidget(n-1, widget.yw)
    #                 # self.dugmeTasindi.emit(widget)
    #                 break
    #
    #     e.accept()


########################################################################
class KenarBoyutSag(KenarBoyutSol):
    # ---------------------------------------------------------------------
    def __init__(self, splitterW, ust_pencere_boyut, renk=QColor(200, 210, 220), parent=None):
        super(KenarBoyutSag, self).__init__(splitterW, ust_pencere_boyut, renk, parent)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        super(KenarBoyutSag, self).mouseMoveEvent(event)
        max_width = self.ust_pencere_boyut.width() // 2
        if self.resizing:
            delta = event.globalPos() - self.mouse_start
            width = self.width_start - delta.x()

            width = max(width, self.min_width)
            width = min(width, max_width)
            # self.splitterW.setFixedWidth(width)

            for i in range(self.splitterW.count()):
                self.splitterW.widget(i).setMinimumWidthVeEskiMinimumSize(width)
