# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '15/2/23'
__author__ = 'E. Y.'

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, \
    QLabel, QCheckBox
from PySide6.QtCore import Qt, Slot, QSettings, Signal
from . import shared
from .spinBoxlar import SpinBox


########################################################################
class PdfyiResmeCevirPenceresi(QDialog):
    # genislik, yukseklik, ilk, son, sayfalar arasi bosluk
    donusturTiklandi = Signal(int, int, int, int, int)

    # ---------------------------------------------------------------------
    def __init__(self, boyut_point, pdf_sayfa_sayisi, parent=None):
        super(PdfyiResmeCevirPenceresi, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(self.tr("Defter: PDF to Image Settings"))
        self.setModal(True)
        layout = QVBoxLayout(self)

        genislik = boyut_point.width() if boyut_point.width() else 1
        yukseklik = boyut_point.height() if boyut_point.height() else 1
        self.oran = genislik / yukseklik

        lblOraniKoru = QLabel(self.tr("Keep aspect ratio"), self)
        self.oraniKoruCBox = QCheckBox(self)
        self.oraniKoruCBox.setChecked(True)
        layOraniKoru = QHBoxLayout()
        layOraniKoru.addWidget(lblOraniKoru)
        layOraniKoru.addWidget(self.oraniKoruCBox)

        lblGenislik = QLabel(self.tr("Width"), self)
        self.genislikSBox = SpinBox(self)
        self.genislikSBox.setMinimum(1)
        self.genislikSBox.setMaximum(9999)
        self.genislikSBox.setValue(genislik)
        self.genislikSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_genislik_degisti)
        layGenislik = QHBoxLayout()
        layGenislik.addWidget(lblGenislik)
        layGenislik.addWidget(self.genislikSBox)

        lblYukseklik = QLabel(self.tr("Height"), self)
        self.yukseklikSBox = SpinBox(self)
        self.yukseklikSBox.setMinimum(1)
        self.yukseklikSBox.setMaximum(9999)
        self.yukseklikSBox.setValue(yukseklik)
        self.yukseklikSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_yukseklik_degisti)
        layYukseklik = QHBoxLayout()
        layYukseklik.addWidget(lblYukseklik)
        layYukseklik.addWidget(self.yukseklikSBox)

        lblIlkSayfa = QLabel(self.tr("From page"), self)
        self.ilkSayfaSBox = SpinBox(self)
        self.ilkSayfaSBox.setMinimum(1)
        self.ilkSayfaSBox.setMaximum(pdf_sayfa_sayisi)
        self.ilkSayfaSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_ilk_sayfa_degisti)
        layIlkSayfa = QHBoxLayout()
        layIlkSayfa.addWidget(lblIlkSayfa)
        layIlkSayfa.addWidget(self.ilkSayfaSBox)

        lblSonSayfa = QLabel(self.tr("To page"), self)
        self.sonSayfaSBox = SpinBox(self)
        self.sonSayfaSBox.setMinimum(1)
        self.sonSayfaSBox.setMaximum(pdf_sayfa_sayisi)
        self.sonSayfaSBox.setValue(pdf_sayfa_sayisi)
        self.sonSayfaSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_son_sayfa_degisti)
        laySonSayfa = QHBoxLayout()
        laySonSayfa.addWidget(lblSonSayfa)
        laySonSayfa.addWidget(self.sonSayfaSBox)

        lblSayfaArasiBosluk = QLabel(self.tr("Gap bw. pages"), self)
        self.sayfaArasiBoslukSBox = SpinBox(self)
        self.sayfaArasiBoslukSBox.setMinimum(0)
        self.sayfaArasiBoslukSBox.setMaximum(1000)
        self.sayfaArasiBoslukSBox.setValue(10)
        laysayfaArasiBosluk = QHBoxLayout()
        laysayfaArasiBosluk.addWidget(lblSayfaArasiBosluk)
        laysayfaArasiBosluk.addWidget(self.sayfaArasiBoslukSBox)

        donusturBtn = QPushButton(self.tr("C&onvert"), self)
        donusturBtn.clicked.connect(self.act_donustur)
        kapatBtn = QPushButton(self.tr("&Close"), self)
        kapatBtn.setDefault(True)
        kapatBtn.clicked.connect(self.reject)
        layBtn = QHBoxLayout()
        layBtn.addWidget(donusturBtn)
        layBtn.addWidget(kapatBtn)

        layout.addLayout(layOraniKoru)
        layout.addLayout(layGenislik)
        layout.addLayout(layYukseklik)
        layout.addLayout(layIlkSayfa)
        layout.addLayout(laySonSayfa)
        layout.addLayout(laysayfaArasiBosluk)
        layout.addLayout(layBtn)

        self.olustur_ayarlar()
        self.oku_ayarlar()
        # commandDialog.accepted.connect()

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_ilk_sayfa_degisti(self, deger):
        self.sonSayfaSBox.setMinimum(deger)

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_son_sayfa_degisti(self, deger):
        self.ilkSayfaSBox.setMaximum(deger)

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_genislik_degisti(self, deger):
        if self.oraniKoruCBox.isChecked():
            self.yukseklikSBox.setValue(self.genislikSBox.value() / self.oran)

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_yukseklik_degisti(self, deger):
        if self.oraniKoruCBox.isChecked():
            self.genislikSBox.setValue(self.yukseklikSBox.value() * self.oran)

    # ---------------------------------------------------------------------
    @Slot()
    def act_donustur(self):
        self.donusturTiklandi.emit(self.genislikSBox.value(),
                                   self.yukseklikSBox.value(),
                                   self.ilkSayfaSBox.value()-1,
                                   self.sonSayfaSBox.value()-1,
                                   self.sayfaArasiBoslukSBox.value()
                                   )
        self.accept()

    # ---------------------------------------------------------------------
    def closeEvent(self, event):
        self.yaz_ayarlar()
        event.accept()

    # ---------------------------------------------------------------------
    def olustur_ayarlar(self):
        QApplication.setOrganizationName(shared.DEFTER_ORG_NAME)
        QApplication.setOrganizationDomain(shared.DEFTER_ORG_DOMAIN)
        QApplication.setApplicationName(shared.DEFTER_APP_NAME)
        self.settings = QSettings(shared.DEFTER_AYARLAR_DOSYA_ADRES, QSettings.Format.IniFormat)
        # self.settings.clear()

    # ---------------------------------------------------------------------
    def oku_ayarlar(self):
        self.settings.beginGroup("PdfyiResmeCevirPenceresi")
        if self.settings.contains("CWinGeometry"):
            self.restoreGeometry(self.settings.value("CWinGeometry"))
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    def yaz_ayarlar(self):
        self.settings.beginGroup("PdfyiResmeCevirPenceresi")
        self.settings.setValue("CWinGeometry", self.saveGeometry())
        self.settings.endGroup()
