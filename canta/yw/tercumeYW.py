# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '16/11/22'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTextEdit
from canta.yw.yuzenWidget import YuzenWidget


#######################################################################
class TercumeYW(YuzenWidget):
    # arkaPlanRengiDegisti = Signal(QColor)
    # yaziRengiDegisti = Signal(QColor)
    # cizgiRengiDegisti = Signal(QColor)
    # cizgiKalinligiDegisti = Signal(float)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(TercumeYW, self).__init__(kapatilabilir_mi=True, parent=parent)

        self.okuBtn = QPushButton(self.tr("Oku"), self)
        self.girisYaziLE = QLineEdit(self)
        self.tercumeTrBtn = QPushButton(self.tr("Tr"), self)
        self.tercumeTrBtn.clicked.connect(self.yap_tr_tercume)
        self.tercumeEngBtn = QPushButton(self.tr("Eng"), self)
        self.tercumeEngBtn.clicked.connect(self.yap_eng_tercume)

        self.ekleWidget(self.okuBtn)
        self.ekleWidget(self.girisYaziLE)
        layTercumeBtn = QHBoxLayout()
        layTercumeBtn.addWidget(self.tercumeTrBtn)
        layTercumeBtn.addWidget(self.tercumeEngBtn)
        self.anaLay.addLayout(layTercumeBtn)
        # self.olustur_radio()

        self.sonucTE = QTextEdit(self)
        self.ekleWidget(self.sonucTE)

        self.addStretchToLayout()

        # self.olustur_cizgi_kalinligi_slider()

        self.setMinimumWidth(250)
        self.setMinimumHeight(170)

    # ---------------------------------------------------------------------
    def yap_tr_tercume(self):
        sonuc = "tr"
        self.sonucTE.setText(sonuc)

    # ---------------------------------------------------------------------
    def yap_eng_tercume(self):
        sonuc = "eng"
        self.sonucTE.setText(sonuc)

    # # ---------------------------------------------------------------------
    # def olustur_radio(self):
    #
    #
    #     self.anaLay.addLayout(radioLay)
