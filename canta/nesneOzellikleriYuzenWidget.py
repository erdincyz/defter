# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '26/1/22'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QHBoxLayout, QButtonGroup, QRadioButton, QLabel
from canta.renkSecici import RenkSeciciWidget
from canta.renkSecmeDugmesi import RenkSecmeDugmesi
from canta.sliderDoubleWithDoubleSpinBox import SliderDoubleWithDoubleSpinBox
from canta.yuzenWidget import YuzenWidget


#######################################################################
class NesneOzellikleriYuzenWidget(YuzenWidget):
    arkaPlanRengiDegisti = Signal(QColor)
    yaziRengiDegisti = Signal(QColor)
    cizgiRengiDegisti = Signal(QColor)
    ekranRenkSeciciDugmesindenRenkDegisti = Signal(QColor, str)
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
        self.renkSecici.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.renkSecici.renkDegisti.connect(self.renkGuncelle)

        self.ekleWidget(self.renkSecici)
        self.addStretchToLayout()

        self.olustur_cizgi_kalinligi_slider()

        self.radioArkaplan.setChecked(True)

        self.setMinimumWidth(250)
        self.setMinimumHeight(175)

    # ---------------------------------------------------------------------
    def olustur_radio(self):

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
        radioLay.addSpacing(5)
        radioLay.addWidget(self.ekrandaRenkSecmeDugmesi)
        radioLay.addSpacing(5)
        radioLay.addWidget(self.radioArkaplan)
        radioLay.addSpacing(5)
        radioLay.addWidget(self.radioYazi)
        radioLay.addSpacing(5)
        radioLay.addWidget(self.radioCizgi)

        self.anaLay.addSpacing(5)
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
        self.cizgiKalinligiDSlider.degerDegisti.connect(lambda x: self.cizgiKalinligiDegisti.emit(x))

        # etiket = QLabel(self.tr("Line&&Pen"), self)
        # layH = QHBoxLayout()
        # layH.addWidget(etiket)
        # layH.addWidget(self.cizgiKalinligiDSlider)
        # self.anaLay.addLayout(layH)

        self.anaLay.addWidget(self.cizgiKalinligiDSlider)

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
