# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '26/1/22'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QButtonGroup, QRadioButton
from canta.renkSecici import RenkSeciciWidget
from canta.sliderDoubleWithDoubleSpinBox import SliderDoubleWithDoubleSpinBox
from canta.yuzenWidget import YuzenWidget


#######################################################################
class NesneOzellikleriYuzenWidget(YuzenWidget):
    arkaPlanRengiDegisti = Signal(QColor)
    yaziRengiDegisti = Signal(QColor)
    cizgiRengiDegisti = Signal(QColor)
    cizgiKalinligiDegisti = Signal(float)

    # ---------------------------------------------------------------------
    def __init__(self, arkaPlanRengi, yaziRengi, cizgiRengi, cizgiKalinligi, parent=None):
        super(NesneOzellikleriYuzenWidget, self).__init__(parent)

        self.arkaPlanRengi = arkaPlanRengi.toHsv()
        self.yaziRengi = yaziRengi.toHsv()
        self.cizgiRengi = cizgiRengi.toHsv()
        self.cizgiKalinligi = cizgiKalinligi
        # self.nesneBoyutu = nesneBoyutu

        # ilk acilista arkaplan rengi geliyor, sonra da kapatilinca gizlendigi icin devamlilik var.
        self.renk = self.arkaPlanRengi

        self.olustur_radio()

        self.renkSecici = RenkSeciciWidget(self.renk, boyut=64, parent=self)
        self.renkSecici.renkDegisti.connect(self.renkGuncelle)

        self.ekleWidget(self.renkSecici)
        self.addStretchToLayout()

        self.olustur_cizgi_kalinligi_slider()

        self.radioArkaplan.setChecked(True)

        self.setMinimumWidth(250)
        self.setMinimumHeight(170)

    # ---------------------------------------------------------------------
    def olustur_radio(self):
        self.radioBtnGroup = QButtonGroup(self)

        self.radioArkaplan = QRadioButton(self.tr("Background"), self)
        self.radioYazi = QRadioButton(self.tr("Text"), self)
        self.radioCizgi = QRadioButton(self.tr("Line && Pen"), self)

        self.radioBtnGroup.addButton(self.radioArkaplan)
        self.radioBtnGroup.addButton(self.radioYazi)
        self.radioBtnGroup.addButton(self.radioCizgi)

        radioLay = QHBoxLayout()

        radioLay.addWidget(self.radioArkaplan)
        radioLay.addWidget(self.radioYazi)
        radioLay.addWidget(self.radioCizgi)

        self.anaLay.addLayout(radioLay)

        self.radioBtnGroup.buttonToggled.connect(self.act_radio_secim_degisti)

    # ---------------------------------------------------------------------
    def olustur_cizgi_kalinligi_slider(self):
        self.cizgiKalinligiDSlider = SliderDoubleWithDoubleSpinBox(parent=self)
        # self.cizgiKalinligiDSlider.setMaximumWidth(150)
        self.cizgiKalinligiDSlider.setMinimum(0)
        self.cizgiKalinligiDSlider.setMaximum(100)
        self.cizgiKalinligiDSlider.setSingleStep(0.1)
        self.cizgiKalinligiDSlider.setValue(self.cizgiKalinligi * 10)
        self.cizgiKalinligiDSlider.degerDegisti.connect(self.cizgiKalinligiDegisti.emit)

        # etiket = QLabel(self.tr("Line&&Pen"), self)
        # layH = QHBoxLayout()
        # layH.addWidget(etiket)
        # layH.addWidget(self.cizgiKalinligiDSlider)
        # self.anaLay.addLayout(layH)

        self.anaLay.addWidget(self.cizgiKalinligiDSlider)

    # ---------------------------------------------------------------------
    def act_radio_secim_degisti(self, btn):
        if btn == self.radioArkaplan:
            renk = self.arkaPlanRengi
            self.renk_tipi = "a"
            self.cizgiKalinligiDSlider.hide()
        elif btn == self.radioYazi:
            renk = self.yaziRengi
            self.renk_tipi = "y"
            self.cizgiKalinligiDSlider.hide()

        elif btn == self.radioCizgi:
            renk = self.cizgiRengi
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
