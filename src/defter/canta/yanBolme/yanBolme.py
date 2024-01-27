# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '10/29/23'
__author__ = 'E. Y.'

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QSplitter, QFrame

from ..yanBolme.dikeyDugme import DikeyDugme
from ..yanBolme.kenarBoyut import KenarBoyutSol, KenarBoyutSag


# ########################################################################
# class Splitter(QSplitter):
#
#     # ---------------------------------------------------------------------
#     def __init__(self, orientation, parent=None):
#         super(Splitter, self).__init__(orientation, parent)
#
#         self.renkYazi = QColor(255, 255, 255)
#         self.renkArkaplan = QColor(200, 200, 200)
#
#     # ---------------------------------------------------------------------
#     def createHandle(self):
#         handle = super(Splitter, self).createHandle()
#         handle.setAutoFillBackground(True)
#
#         p = handle.palette()
#         p.setColor(handle.foregroundRole(), self.renkYazi)
#         p.setColor(handle.backgroundRole(), self.renkArkaplan)
#         handle.setPalette(p)
#
#         return handle


########################################################################
class YanBolme(QFrame):

    # ---------------------------------------------------------------------
    def __init__(self, solSag, parent=None):
        super(YanBolme, self).__init__(parent)

        self.setAcceptDrops(True)

        self.solSag = solSag

        self.setAutoFillBackground(True)

        p = self.palette()
        self.renkArkaplan = p.color(self.backgroundRole())
        self.renkArkaplanSurukleBirakBelirt = QColor(185, 255, 220)

        anaLay = QHBoxLayout(self)
        anaLay.setContentsMargins(0, 0, 0, 0)
        anaLay.setSpacing(0)

        self.dugmeLay = QVBoxLayout()
        self.dugmeLay.setContentsMargins(0, 0, 0, 0)
        self.dugmeLay.setSpacing(30)

        icerikLay = QHBoxLayout()
        icerikLay.setContentsMargins(0, 0, 0, 0)
        icerikLay.setSpacing(0)

        # -------
        self.icerikSplitter = QSplitter(Qt.Orientation.Vertical, self)
        self.icerikSplitter.setChildrenCollapsible(False)
        # self.icerikSplitter.setFixedWidth(genislik)
        # self.icerikSplitter.setFixedHeight(yukseklik-asagi_kayma)
        # self.icerikSplitter.splitterMoved.connect(self.splitter_boyut_degisti)

        if solSag == "sol":

            self.kenarBoyutWidget = KenarBoyutSol(splitterW=self.icerikSplitter,
                                                  ust_pencere_boyut=self.parent().size(),
                                                  renk=QColor(238, 238, 238), parent=self)
            self.kenarBoyutWidget.setMaximumWidth(5)
            self.kenarBoyutWidget.setMinimumWidth(5)
            self.kenarBoyutWidget.setMinimumHeight(50)
            # self.kenarBoyutWidget.hide()

            icerikLay.addWidget(self.icerikSplitter)
            icerikLay.addWidget(self.kenarBoyutWidget)

            anaLay.addLayout(self.dugmeLay)
            anaLay.addLayout(icerikLay)

        elif solSag == "sag":

            self.kenarBoyutWidget = KenarBoyutSag(splitterW=self.icerikSplitter,
                                                  ust_pencere_boyut=self.parent().size(),
                                                  renk=QColor(238, 238, 238), parent=self)
            self.kenarBoyutWidget.setMaximumWidth(5)
            self.kenarBoyutWidget.setMinimumWidth(5)
            self.kenarBoyutWidget.setMinimumHeight(50)
            # self.kenarBoyutWidget.hide()

            icerikLay.addWidget(self.kenarBoyutWidget)
            icerikLay.addWidget(self.icerikSplitter)

            anaLay.addLayout(icerikLay)
            anaLay.addLayout(self.dugmeLay)

    # # ---------------------------------------------------------------------
    # def splitter_boyut_degisti(self, pos, idx):
    #     print(pos, idx)

    # ---------------------------------------------------------------------
    def dugme_ve_yw_ekle(self, yazi, yw, yuklenirken_mi):

        # dugme = DikeyDugme(yazi, self, "yukari")
        dugme = DikeyDugme("", self, "yukari")
        # dugme.setToolTip(yazi)
        dugme.setStatusTip(yazi)
        dugme.setMaximumWidth(4)
        # dugme.setMaximumHeight(100)
        dugme.clicked.connect(self.ac_kapa)
        # dugme.btnYuzdur.clicked.connect(lambda: self.yw_yuzdur(dugme.yw))
        dugme.yw = yw
        yw.dugme = dugme
        self.dugmeLay.addWidget(dugme)

        if yuklenirken_mi:
            yw.cubuga_tasindi_yuklenirken(solSag=self.solSag)
            self.icerikSplitter.insertWidget(yw.sira, yw)
        else:
            yw.cubuga_tasindi(solSag=self.solSag)
            # self.icerikLay.addWidget(yw)
            yw.sira = self.icerikSplitter.count()
            self.icerikSplitter.addWidget(yw)
            yw.resize(yw.eskiSize)

        # self.kenarBoyutWidget.genislikleri_esitle()

        dugme.renk_degistir(acik_mi=not yw.kucuk_mu)

        # ywler hepsi yuzer haldeyken asagida kenarCubugu gizliyoruz
        # self.kenarBoyutWidget.show()

    # ---------------------------------------------------------------------
    def yw_yuzdur(self, yw):

        for i in range(self.dugmeLay.count()):
            dugme = self.dugmeLay.itemAt(i).widget()
            if dugme.yw is yw:
                self.dugmeLay.removeWidget(dugme)
                yw.dugme = None
                dugme.setParent(None)
                break
        yw.hide()
        yw.setParent(self.parent())
        yw.cubuktan_atildi()
        yw.show()
        # if not self.icerikSplitter.count():
        #     self.kenarBoyutWidget.hide()

        # idx = self.icerikSplitter.indexOf(yw)
        # yw2.setParent(self)

    # ---------------------------------------------------------------------
    def yw_cubuga_tasi_veya_kapat(self, yw, yuklenirken_mi):
        if yuklenirken_mi:
            self.dugme_ve_yw_ekle(yw.baslikEtiket.text(), yw, yuklenirken_mi)
        else:
            if yw.cubukta_mi:
                self.yw_yuzdur(yw)
            else:
                self.dugme_ve_yw_ekle(yw.baslikEtiket.text(), yw, yuklenirken_mi)

    # ---------------------------------------------------------------------
    def ac_kapa(self):
        dugme = self.sender()
        yw = dugme.yw
        if yw.isVisible():
            yw.kucult()
        else:
            yw.buyult()

    # ---------------------------------------------------------------------
    def renk_degistir(self, renkArkaplan=None):

        p = self.palette()
        # p.setColor(self.foregroundRole(), self.renkYazi)
        # ozellikle boyle yapildi, anlik widgeti baska renge boyayabiliyoruz
        # renk yoksa yine eski rengine don anlamında
        if renkArkaplan:
            p.setColor(self.backgroundRole(), renkArkaplan)
            self.kenarBoyutWidget.renk_degistir(renkArkaplan)
        else:
            # orjinal rengine don
            p.setColor(self.backgroundRole(), self.renkArkaplan)
            self.kenarBoyutWidget.renk_degistir()
        self.setPalette(p)

    # ---------------------------------------------------------------------
    def dragEnterEvent(self, e):
        e.accept()
        self.renk_degistir(self.renkArkaplanSurukleBirakBelirt)

    # ---------------------------------------------------------------------
    def dragLeaveEvent(self, e):
        e.accept()
        self.renk_degistir()

    # ---------------------------------------------------------------------
    def dropEvent(self, e):
        pos = e.pos()
        yw = e.source()
        dugme = yw.dugme

        dugmeAdet = self.dugmeLay.count()
        if not dugmeAdet:
            self.dugmeLay.addWidget(dugme)
            self.icerikSplitter.addWidget(yw)

        else:

            birak = False
            for n in range(dugmeAdet):
                w = self.dugmeLay.itemAt(n).widget()
                # birak = pos.y() < w.y() + w.size().height() // 2
                birak = pos.y() < w.y() + w.size().height()

                if birak:
                    if self.solSag == "sol":
                        yw.sola_yasla()
                    else:
                        yw.saga_yasla()

                    self.dugmeLay.insertWidget(n, dugme)
                    self.icerikSplitter.insertWidget(n, yw)
                    # self.dugmeTasindi.emit(dugme)
                    break

        e.accept()
        self.renk_degistir()

    # # ---------------------------------------------------------------------
    # def dropEventDugmeIcin(self, e):
    #     pos = e.pos()
    #     dugme = e.source()
    #     yw = dugme.yw
    #
    #     dugmeAdet = self.dugmeLay.count()
    #     if not dugmeAdet:
    #         self.dugmeLay.addWidget(dugme)
    #         self.icerikSplitter.addWidget(yw)
    #
    #     else:
    #
    #         birak = False
    #         for n in range(dugmeAdet):
    #             w = self.dugmeLay.itemAt(n).widget()
    #             birak = pos.y() < w.y() + w.size().height() // 2
    #
    #             if birak:
    #                 if self.solSag == "sol":
    #                     yw.sola_yasla()
    #                 else:
    #                     yw.saga_yasla()
    #
    #                 self.dugmeLay.insertWidget(n - 1, dugme)
    #                 self.icerikSplitter.insertWidget(n - 1, yw)
    #                 # self.dugmeTasindi.emit(dugme)
    #                 break
    #
    #     e.accept()
