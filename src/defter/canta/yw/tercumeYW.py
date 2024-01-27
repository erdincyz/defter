# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '16/11/22'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QWidget, QVBoxLayout
from ..yw.yuzenWidget import YuzenWidget


#######################################################################
class TercumeYW(YuzenWidget):

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(TercumeYW, self).__init__(kapatilabilir_mi=True, parent=parent)

        self.okuBtn = QPushButton(self.tr("Oku"), self)
        self.girisYaziLE = QLineEdit(self)
        self.tercumeTrBtn = QPushButton(self.tr("Tr"), self)
        self.tercumeTrBtn.clicked.connect(self.yap_tr_tercume)
        self.tercumeEngBtn = QPushButton(self.tr("Eng"), self)
        self.tercumeEngBtn.clicked.connect(self.yap_eng_tercume)

        layTercumeBtn = QHBoxLayout()
        layTercumeBtn.addWidget(self.tercumeTrBtn)
        layTercumeBtn.addWidget(self.tercumeEngBtn)

        self.sonucTE = QTextEdit(self)
        self.ekleWidget(self.sonucTE)

        temelW = QWidget(self)
        anaLay = QVBoxLayout(temelW)
        anaLay.addWidget(self.okuBtn)
        anaLay.addWidget(self.girisYaziLE)
        anaLay.addLayout(layTercumeBtn)
        anaLay.addWidget(self.sonucTE)
        anaLay.addStretch()

        self.ekleWidget(temelW)

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
