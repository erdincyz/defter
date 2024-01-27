# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '26/1/22'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QButtonGroup, QRadioButton, QLabel
from ..renkSecici import RenkSeciciWidget
from ..renkSecmeDugmesi import RenkSecmeDugmesi
from ..sliderDoubleWithDoubleSpinBox import SliderDoubleWithDoubleSpinBox
from ..yw.yuzenWidget import YuzenWidget


#######################################################################
class NesneOzellikleriYW(YuzenWidget):
    arkaPlanRengiDegisti = Signal(QColor)
    yaziRengiDegisti = Signal(QColor)
    cizgiRengiDegisti = Signal(QColor)
    ekranRenkSeciciDugmesindenRenkDegisti = Signal(QColor, str)
    cizgiKalinligiDegisti = Signal(float)

    # ---------------------------------------------------------------------
    def __init__(self, arkaPlanRengi, yaziRengi, cizgiRengi, cizgiKalinligi, parent=None):
        super(NesneOzellikleriYW, self).__init__(kapatilabilir_mi=True, parent=parent)

        self.arkaPlanRengi = arkaPlanRengi.toHsv()
        self.yaziRengi = yaziRengi.toHsv()
        self.cizgiRengi = cizgiRengi.toHsv()
        self.cizgiKalinligi = cizgiKalinligi
        # self.nesneBoyutu = nesneBoyutu

        # ilk acilista arkaplan rengi geliyor, sonra da kapatilinca gizlendigi icin devamlilik var.
        self.renk = self.arkaPlanRengi

        self.aracIkonuEtiketi = QLabel(self)

        self.ekrandaRenkSecmeDugmesi = RenkSecmeDugmesi(self)
        self.ekrandaRenkSecmeDugmesi.renkDegisti.connect(self.ekranRenkSeciciDugmesindenRenkDegisti.emit)

        self.radioBtnGroup = QButtonGroup(self)

        self.radioArkaplan = QRadioButton(self.tr("Background"), self)
        self.radioArkaplan.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.radioYazi = QRadioButton(self.tr("Text"), self)
        self.radioYazi.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.radioCizgi = QRadioButton(self.tr("Line && Pen"), self)
        self.radioCizgi.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.radioBtnGroup.addButton(self.radioArkaplan)
        self.radioBtnGroup.addButton(self.radioYazi)
        self.radioBtnGroup.addButton(self.radioCizgi)

        radioLay = QHBoxLayout()

        radioLay.addSpacing(5)
        radioLay.addWidget(self.aracIkonuEtiketi)
        radioLay.addSpacing(3)
        radioLay.addWidget(self.ekrandaRenkSecmeDugmesi, 1)
        radioLay.addSpacing(5)
        radioLay.addWidget(self.radioArkaplan, 2)
        radioLay.addSpacing(5)
        radioLay.addWidget(self.radioYazi, 2)
        radioLay.addSpacing(5)
        radioLay.addWidget(self.radioCizgi, 2)

        self.radioArkaplan.setChecked(True)
        self.renk_tipi = "a"
        self.radioBtnGroup.buttonToggled.connect(self.act_radio_secim_degisti)

        self.cizgiKalinligiDSlider = SliderDoubleWithDoubleSpinBox(parent=self)
        # self.cizgiKalinligiDSlider.setMaximumWidth(150)
        self.cizgiKalinligiDSlider.setMinimum(0)
        self.cizgiKalinligiDSlider.setMaximum(100)
        self.cizgiKalinligiDSlider.setSingleStep(0.1)
        self.cizgiKalinligiDSlider.setValue(self.cizgiKalinligi * 10)
        self.cizgiKalinligiDSlider.degerDegisti.connect(lambda x: self.cizgiKalinligiDegisti.emit(x))
        self.cizgiKalinligiDSlider.hide()

        self.renkSecici = RenkSeciciWidget(self.renk, boyut=64, parent=self)
        self.renkSecici.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.renkSecici.renkDegisti.connect(self.renkGuncelle)

        temelW = QWidget(self)
        anaLay = QVBoxLayout(temelW)

        anaLay.addLayout(radioLay)
        anaLay.addWidget(self.renkSecici)
        anaLay.addSpacing(5)
        anaLay.addWidget(self.cizgiKalinligiDSlider)
        anaLay.addStretch()

        self.setMinimumWidth(100)
        self.setMinimumHeight(20)
        self.setMinimumSize(300, 190)
        # self.setMinimumSize(280, 165)
        temelW.setMinimumSize(280, 165)
        self.adjustSize()

        self.ekleWidget(temelW)

    # ---------------------------------------------------------------------
    def act_radio_secim_degisti(self, btn):
        if btn == self.radioArkaplan:
            # renk = self.arkaPlanRengi
            if self.parent().cScene.activeItem:
                renk = self.parent().cScene.activeItem.arkaPlanRengi
            else:
                renk = self.parent().cScene.aktifArac.arkaPlanRengi
            self.renk_tipi = "a"
            self.cizgiKalinligiDSlider.hide()
        elif btn == self.radioYazi:
            # renk = self.yaziRengi
            if self.parent().cScene.activeItem:
                renk = self.parent().cScene.activeItem.yaziRengi
            else:
                renk = self.parent().cScene.aktifArac.yaziRengi
            self.renk_tipi = "y"
            self.cizgiKalinligiDSlider.hide()

        elif btn == self.radioCizgi:
            # renk = self.cizgiRengi
            if self.parent().cScene.activeItem:
                renk = self.parent().cScene.activeItem.cizgiRengi
            else:
                renk = self.parent().cScene.aktifArac.cizgiRengi
            self.renk_tipi = "c"
            self.cizgiKalinligiDSlider.show()

        self.renkSecici.disardan_renk_gir(renk)

    # ---------------------------------------------------------------------
    def renkGuncelle(self, renk):
        if self.renk_tipi == "a":
            self.arkaPlanRengi = renk
            self.arkaPlanRengiDegisti.emit(renk)
        elif self.renk_tipi == "y":
            self.yaziRengi = renk
            self.yaziRengiDegisti.emit(renk)
        elif self.renk_tipi == "c":
            self.cizgiRengi = renk
            self.cizgiRengiDegisti.emit(renk)
