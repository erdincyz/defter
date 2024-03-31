# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '12/03/24'
__author__ = 'E. Y.'

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QApplication,
                               QLabel, QCheckBox, QTimeEdit, QMessageBox)
from PySide6.QtCore import Qt, Slot, QSettings, Signal, QTime
from PySide6.QtGui import QColor
from . import shared
from .spinBoxlar import SpinBox


########################################################################
class VideoyuResmeCevirPenceresi(QDialog):
    donusturTiklandi = Signal(int, int, bool, int, int, int, int, int, int, int, int)
    iptalTiklandi = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, boyut_point, video_sure, altyazi_var_mi, altyazi_sayisi, parent=None):
        super(VideoyuResmeCevirPenceresi, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(self.tr("Defter: Video to Image Settings"))
        self.setModal(True)
        layout = QVBoxLayout(self)

        if boyut_point:
            genislik = boyut_point.width()
            yukseklik = boyut_point.height()
        else:
            genislik = 800
            yukseklik = 600

        self.oran = genislik / yukseklik

        # lblOraniKoru = QLabel(self.tr("Keep aspect ratio"), self)
        self.oraniKoruCBox = QCheckBox(self)
        self.oraniKoruCBox.setText(self.tr("Keep aspect ratio"))
        self.oraniKoruCBox.setChecked(True)

        lblGenislik = QLabel(self.tr("Width"), self)
        self.genislikSBox = SpinBox(self)
        self.genislikSBox.setSuffix(" px")
        self.genislikSBox.setMinimum(1)
        self.genislikSBox.setMaximum(9999)
        self.genislikSBox.setValue(genislik)
        self.genislikSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_genislik_degisti)
        layGenislik = QHBoxLayout()
        layGenislik.addWidget(lblGenislik)
        layGenislik.addWidget(self.genislikSBox)

        lblYukseklik = QLabel(self.tr("Height"), self)
        self.yukseklikSBox = SpinBox(self)
        self.yukseklikSBox.setSuffix(" px")
        self.yukseklikSBox.setMinimum(1)
        self.yukseklikSBox.setMaximum(9999)
        self.yukseklikSBox.setValue(yukseklik)
        self.yukseklikSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_yukseklik_degisti)

        layYukseklik = QHBoxLayout()
        layYukseklik.addWidget(lblYukseklik)
        layYukseklik.addWidget(self.yukseklikSBox)

        self.orjinalBoyutuKoru = QCheckBox(self)
        self.orjinalBoyutuKoru.setText(self.tr("Keep original size"))
        self.orjinalBoyutuKoru.setToolTip(self.tr("If selected, images are saved at the original size but added to the scene at the dimensions entered above."))
        self.orjinalBoyutuKoru.setChecked(False)

        lblResimArasiBosluk = QLabel(self.tr("Gap bw. images"), self)
        self.resimArasiDikeyBoslukSBox = SpinBox(self)
        self.resimArasiDikeyBoslukSBox.setMinimum(0)
        self.resimArasiDikeyBoslukSBox.setMaximum(1000)
        self.resimArasiDikeyBoslukSBox.setValue(10)
        layResimArasiBosluk = QHBoxLayout()
        layResimArasiBosluk.addWidget(lblResimArasiBosluk)
        layResimArasiBosluk.addWidget(self.resimArasiDikeyBoslukSBox)

        lblBaslangic = QLabel(self.tr("From"), self)
        self.baslangicTE = QTimeEdit(self)
        self.baslangicTE.setDisplayFormat("HH:mm:ss:zzz")
        self.baslangicTE.setMaximumTime(video_sure)
        # self.baslangicTE.setMinimum(1)
        # self.baslangicTE.setMaximum(altyazi_sayisi)
        self.baslangicTE.timeChanged.connect(self.act_resim_sayisi_hesapla)
        layBaslangic = QHBoxLayout()
        layBaslangic.addWidget(lblBaslangic)
        layBaslangic.addWidget(self.baslangicTE)

        lblBitis = QLabel(self.tr("To"), self)
        self.bitisTE = QTimeEdit(self)
        self.bitisTE.setDisplayFormat("HH:mm:ss:zzz")
        self.bitisTE.setTime(video_sure)
        self.bitisTE.setMaximumTime(video_sure)
        # self.bitisTE.setMinimum(1)
        # self.bitisTE.setMaximum(altyazi_sayisi)
        # self.bitisTE.setValue(altyazi_sayisi)
        self.bitisTE.timeChanged.connect(self.act_resim_sayisi_hesapla)
        layBitis = QHBoxLayout()
        layBitis.addWidget(lblBitis)
        layBitis.addWidget(self.bitisTE)

        lblZamanAraligi = QLabel(self.tr("Interval"), self)
        self.zamanAraligiTE = QTimeEdit(self)
        self.zamanAraligiTE.setDisplayFormat("HH:mm:ss:zzz")
        self.zamanAraligiTE.setMinimumTime(QTime(0, 0, 0, 1))
        self.zamanAraligiTE.setMaximumTime(video_sure)
        self.zamanAraligiTE.timeChanged.connect(self.act_resim_sayisi_hesapla)
        layZamanAraligi = QHBoxLayout()
        layZamanAraligi.addWidget(lblZamanAraligi)
        layZamanAraligi.addWidget(self.zamanAraligiTE)

        self.lblToplamResimSayisi = QLabel(self.tr("0 Image"), self)
        self.lblToplamResimSayisi.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblToplamResimSayisi.setAutoFillBackground(True)
        p = self.lblToplamResimSayisi.palette()
        p.setColor(self.lblToplamResimSayisi.foregroundRole(), QColor(255, 255, 255))
        p.setColor(self.lblToplamResimSayisi.backgroundRole(), QColor(140, 160, 170))
        self.lblToplamResimSayisi.setPalette(p)
        self.act_resim_sayisi_hesapla()

        self.altyaziCBox = QCheckBox(self.tr("With subtitles"), self)
        self.altyaziCBox.stateChanged.connect(self.act_altyaziCBox_degisti)
        layAltyazi = QHBoxLayout()
        layAltyazi.addWidget(self.altyaziCBox)

        lblOncekiAltyazi = QLabel(self.tr("Merge with prev. subtitle"), self)
        self.oncekiAltyaziSBox = SpinBox(self)
        self.oncekiAltyaziSBox.setValue(0)
        self.oncekiAltyaziSBox.setMinimum(0)
        self.oncekiAltyaziSBox.setMaximum(altyazi_sayisi)
        layOncekiAltyazi = QHBoxLayout()
        layOncekiAltyazi.addWidget(lblOncekiAltyazi)
        layOncekiAltyazi.addWidget(self.oncekiAltyaziSBox)

        lblSonrakiAltyazi = QLabel(self.tr("Merge with next subtitle"), self)
        self.sonrakiAltyaziSBox = SpinBox(self)
        self.sonrakiAltyaziSBox.setValue(0)
        self.sonrakiAltyaziSBox.setMinimum(0)
        self.sonrakiAltyaziSBox.setMaximum(altyazi_sayisi)
        laySonrakiAltyazi = QHBoxLayout()
        laySonrakiAltyazi.addWidget(lblSonrakiAltyazi)
        laySonrakiAltyazi.addWidget(self.sonrakiAltyaziSBox)

        if not altyazi_var_mi:
            self.altyaziCBox.setText(self.tr("No subtitles were added to the video"))
            self.altyaziCBox.setToolTip(self.tr("You can add subtitles to the video and try again."))
            self.altyaziCBox.setChecked(False)
            self.altyaziCBox.setDisabled(True)
            self.oncekiAltyaziSBox.setDisabled(True)
            self.sonrakiAltyaziSBox.setDisabled(True)
        else:
            self.altyaziCBox.setChecked(True)

        donusturBtn = QPushButton(self.tr("&Extract"), self)
        donusturBtn.clicked.connect(self.act_donustur)
        self.kapatBtn = QPushButton(self.tr("&Close"), self)
        self.kapatBtn.setDefault(True)
        self.kapatBtn.clicked.connect(self.kapat_yada_iptal_et)
        layBtn = QHBoxLayout()
        layBtn.addWidget(donusturBtn)
        layBtn.addWidget(self.kapatBtn)

        layout.addWidget(self.oraniKoruCBox)
        layout.addLayout(layGenislik)
        layout.addLayout(layYukseklik)
        layout.addLayout(layResimArasiBosluk)
        layout.addWidget(self.orjinalBoyutuKoru)
        layout.addLayout(layBaslangic)
        layout.addLayout(layBitis)
        layout.addLayout(layZamanAraligi)
        layout.addWidget(self.lblToplamResimSayisi)
        layout.addLayout(layAltyazi)
        layout.addLayout(layOncekiAltyazi)
        layout.addLayout(laySonrakiAltyazi)
        layout.addLayout(layBtn)

        self.olustur_ayarlar()
        self.oku_ayarlar()
        # commandDialog.accepted.connect()

    # ---------------------------------------------------------------------
    @Slot()
    def kapat_yada_iptal_et(self):

        if self.kapatBtn.text == "&Close":
            self.reject()
        else:
            self.iptalTiklandi.emit()
            self.reject()

    # ---------------------------------------------------------------------
    @Slot(QTime)
    def act_resim_sayisi_hesapla(self, lazim_degil=None):

        self.resimSayisi = ((self.bitisTE.time().msecsSinceStartOfDay()
                             - self.baslangicTE.time().msecsSinceStartOfDay())
                            // self.zamanAraligiTE.time().msecsSinceStartOfDay()) + 1
        self.lblToplamResimSayisi.setText(self.tr("%n image(s)", "", self.resimSayisi))

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_altyaziCBox_degisti(self, deger):
        self.oncekiAltyaziSBox.setDisabled(not deger)
        self.sonrakiAltyaziSBox.setDisabled(not deger)

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

        # ilk_ms = ((ilk.hour() * 3600 + ilk.minute()*60 +ilk.second()*1000) * 1000 ) + ilk.msec()
        # son_ms = ((son.hour() * 3600 + son.minute()*60 +son.second()*1000) * 1000 ) + son.msec()
        # zaman_araligi_ms = ((zaman_araligi.hour() * 3600 + zaman_araligi.minute()*60 +zaman_araligi.second()*1000) * 1000 ) + zaman_araligi.msec()

        if self.resimSayisi > 100:
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle(self.tr(f"Defter: There are {self.resimSayisi} images to extract!"))
            msgBox.setIcon(QMessageBox.Icon.Warning)
            msgBox.setText(self.tr(f"Do you want to extract {self.resimSayisi} images?"))
            msgBox.setInformativeText(self.tr("This may take time!"))

            extractButton = msgBox.addButton(self.tr("&Extract"), QMessageBox.ButtonRole.AcceptRole)
            cancelButton = msgBox.addButton(self.tr("&Cancel"), QMessageBox.ButtonRole.RejectRole)
            # msgBox.addButton(QMessageBox.Cancel)
            msgBox.setDefaultButton(extractButton)
            msgBox.setEscapeButton(cancelButton)

            msgBox.exec()
            if msgBox.clickedButton() == extractButton:
                devam = True
            else:
                devam = False
        else:
            devam = True

        if devam:
            # self.kapatBtn.setText(self.tr("&Cancel"))
            self.donusturTiklandi.emit(self.genislikSBox.value(),
                                       self.yukseklikSBox.value(),
                                       self.orjinalBoyutuKoru.isChecked(),
                                       self.baslangicTE.time().msecsSinceStartOfDay(),
                                       self.bitisTE.time().msecsSinceStartOfDay(),
                                       self.zamanAraligiTE.time().msecsSinceStartOfDay(),
                                       self.resimArasiDikeyBoslukSBox.value(),
                                       self.resimSayisi,
                                       self.altyaziCBox.isChecked(),
                                       self.oncekiAltyaziSBox.value(),
                                       self.sonrakiAltyaziSBox.value()
                                       )

            # self.lblToplamResimSayisi.setText(self.tr("Please wait..."))

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
        self.settings.beginGroup("VideoyuResmeCevirPenceresi")
        if self.settings.contains("CWinGeometry"):
            self.restoreGeometry(self.settings.value("CWinGeometry"))
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    def yaz_ayarlar(self):
        self.settings.beginGroup("VideoyuResmeCevirPenceresi")
        self.settings.setValue("CWinGeometry", self.saveGeometry())
        self.settings.endGroup()
