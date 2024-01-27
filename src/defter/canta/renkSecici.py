# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '6/25/22'
__author__ = 'E. Y.'

import sys
from PySide6.QtCore import Signal, QPoint
from PySide6.QtGui import QIcon, Qt, QColor, QLinearGradient, QGradient, QPainter, QBrush, QPen
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from .renkCubuguVeSayiKutusu import RenkCubuguVeSayiKutusu
from .shared import kutulu_arkaplan_olustur


#######################################################################
class RenkSecilenKareW(QWidget):
    renkDegisti = Signal(QColor)

    # ---------------------------------------------------------------------
    def __init__(self, eskiRenk, parent=None):
        super(RenkSecilenKareW, self).__init__(parent)

        self.x_oran = self.width() / 255
        self.y_oran = self.height() / 255
        self.halkaKoordiant = QPoint()

        self.renkTon = eskiRenk.hsvHue()
        self.seffalik = eskiRenk.alpha()
        self.renkleriAyarla()
        self.halkayi_koordianata_tasi(eskiRenk.hsvSaturation(), eskiRenk.value())

    # ---------------------------------------------------------------------
    def resizeEvent(self, event):
        self.x_oran = self.width() / 255
        self.y_oran = self.height() / 255

        self.renkleriAyarla()
        # self.renkDegisimiBildir()
        # self.update()
        super(RenkSecilenKareW, self).resizeEvent(event)

    # ---------------------------------------------------------------------
    def renkleriAyarla(self):
        self.renkGrad = QLinearGradient(0, 0, 1, 0)
        self.renkGrad.setCoordinateMode(QLinearGradient.ObjectMode)
        self.renkGrad.setSpread(QGradient.PadSpread)
        self.renkGrad.setColorAt(0, QColor(255, 255, 255))
        self.renkGrad.setColorAt(1, QColor.fromHsv(self.renkTon, 255, 255))

        self.beyazlikGrad = QLinearGradient(0, 0, 0, 1)
        self.beyazlikGrad.setCoordinateMode(QLinearGradient.ObjectMode)
        self.beyazlikGrad.setSpread(QGradient.PadSpread)
        self.beyazlikGrad.setColorAt(0, QColor(0, 0, 0, 0))
        self.beyazlikGrad.setColorAt(1, QColor(0, 0, 0, 255))
        self.update()

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        self.halkaKoordiant = self.koordinat_normalize_et(event.position().x(), event.position().y())

        self.update()
        self.renkDegisimiBildir()

        super(RenkSecilenKareW, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        self.halkaKoordiant = self.koordinat_normalize_et(event.position().x(), event.position().y())

        self.update()
        self.renkDegisimiBildir()

    # ---------------------------------------------------------------------
    def halkayi_koordianata_tasi(self, doygunluk, beyazlik):
        x = self.x_oran * doygunluk
        y = self.width() - (beyazlik * self.y_oran)

        self.halkaKoordiant = self.koordinat_normalize_et(x, y)
        self.update()

    # ---------------------------------------------------------------------
    def koordinat_normalize_et(self, x, y):
        # self.halkaKoordiant = QPoint(0 if x < 0 else x if x < self.width() else self.width(),
        #                              0 if y < 0 else y if y < self.height() else self.height())

        x = min(max(x, 0), self.width())
        y = min(max(y, 0), self.height())

        return QPoint(x, y)

    # ---------------------------------------------------------------------
    def renk_normalize_et(self, doygunluk, beyazlik):
        doygunluk = min(max(doygunluk, 0), 255)
        beyazlik = min(max(beyazlik, 0), 255)

        renk = QColor.fromHsv(self.renkTon, doygunluk, beyazlik, self.seffalik)

        return renk

    # ---------------------------------------------------------------------
    def yazRenkTonDisardan(self, renkTon):
        self.renkTon = renkTon
        self.renkleriAyarla()

    # ---------------------------------------------------------------------
    def yazSeffaflikDisardan(self, alpha):
        self.seffalik = alpha

    # ---------------------------------------------------------------------
    def yazRenkTon(self, renkTon):
        """renkSecici ton cubugu hareketinden geliyor"""
        self.renkTon = renkTon
        self.renkleriAyarla()
        self.renkDegisimiBildir()

    # ---------------------------------------------------------------------
    def yazSeffaflik(self, alpha):
        """renkSecici seffaflik cubugu hareketinden geliyor"""
        self.seffalik = alpha
        self.renkDegisimiBildir()

    # ---------------------------------------------------------------------
    def renkDegisimiBildir(self):
        doygunluk = self.halkaKoordiant.x() / self.x_oran
        beyazlik = 255 - (self.halkaKoordiant.y() / self.y_oran)

        renk = self.renk_normalize_et(doygunluk, beyazlik)
        self.renkDegisti.emit(renk)

    # ---------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        # p.begin()
        p.fillRect(self.rect(), QBrush(self.renkGrad))
        p.fillRect(self.rect(), QBrush(self.beyazlikGrad))

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(Qt.GlobalColor.white, 1))
        p.drawEllipse(self.halkaKoordiant, 7, 7)

        p.end()


#######################################################################
class RenkGostergeW(QWidget):

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(RenkGostergeW, self).__init__(parent)

        self.renk = QColor(0, 0, 0, 0)

    # ---------------------------------------------------------------------
    def renkGuncelle(self, renk):
        self.renk = renk
        self.update()

    # ---------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        # p.begin()
        p.fillRect(self.rect(), QBrush(self.renk))
        p.end()


#######################################################################
class RenkSeciciWidget(QWidget):
    renkDegisti = Signal(QColor)

    # ---------------------------------------------------------------------
    def __init__(self, eskiRenk, boyut=256, parent=None):
        super(RenkSeciciWidget, self).__init__(parent)
        # self.setMinimumWidth(250)
        # self.setMinimumHeight(170)
        self.eskiRenk = eskiRenk.toHsv()

        # --------------------
        self.rTonVeSayiKutusu = RenkCubuguVeSayiKutusu(self.tr("H"), Qt.Orientation.Horizontal, self)
        # self.rTonVeSayiKutusu.setFixedWidth(150)
        self.rTonVeSayiKutusu.setRange(0, 359)

        # ########  TON ARKAPLAN  ################
        gradient = QLinearGradient(0, 0, 1, 0)
        gradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectMode)
        gradient.setColorAt(0, QColor.fromHsv(0, 255, 255))
        gradient.setColorAt(0.16105497, QColor.fromHsv(60, 255, 255))
        gradient.setColorAt(0.35173747, QColor.fromHsv(120, 255, 255))
        gradient.setColorAt(0.48789391, QColor.fromHsv(180, 255, 255))
        # gradient.setColorAt(0.48789391, renkHsv)
        gradient.setColorAt(0.70091939, QColor.fromHsv(240, 255, 255))
        gradient.setColorAt(0.83720928, QColor.fromHsv(300, 255, 255))
        gradient.setColorAt(1, QColor.fromHsv(359, 255, 255))
        self.rTonVeSayiKutusu.setBgGradient(gradient)
        self.rTonVeSayiKutusu.degerDegisti.connect(self.renk_ton_degisti_slider)

        # --------------------
        self.rSeffaflikVeSayiKutusu = RenkCubuguVeSayiKutusu(self.tr("A"), Qt.Orientation.Horizontal, self)
        # self.rSeffaflikVeSayiKutusu.setFixedWidth(150)
        self.rSeffaflikVeSayiKutusu.setRange(0, 255)
        kutulu_arkaplan_olustur(self.rSeffaflikVeSayiKutusu)
        self.rSeffaflikVeSayiKutusu.degerDegisti.connect(self.renk_seffaflik_degisti_slider)

        # --------------------
        self.renkSecmeKutusu = RenkSecilenKareW(self.eskiRenk, self)
        self.renkSecmeKutusu.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.renkSecmeKutusu.setFixedWidth(boyut)
        self.renkSecmeKutusu.setFixedHeight(boyut)
        self.renkSecmeKutusu.renkDegisti.connect(self.renk_degisimi_bildir)

        # --------------------
        self.anaLay = QVBoxLayout()
        self.setLayout(self.anaLay)
        vLay = QVBoxLayout()
        hLay = QHBoxLayout()
        vLay.addWidget(self.rTonVeSayiKutusu)
        vLay.addWidget(self.rSeffaflikVeSayiKutusu)
        hLay.addWidget(self.renkSecmeKutusu)
        hLay.addLayout(vLay)
        self.anaLay.addLayout(hLay)
        self.renk = eskiRenk

        self.disardan_renk_gir(self.eskiRenk)
        self.setFocus()

    # ---------------------------------------------------------------------
    def disardan_renk_gir(self, renk):
        # self.eskiRenk = renk.toHsv()
        self.eskiRenk = renk
        self.rTonVeSayiKutusu.setValue(self.eskiRenk.hsvHue())
        # self.seffalik_cubugu_arkaplan_degistir(self.eskiRenk.hsvHue())
        self.rSeffaflikVeSayiKutusu.setValue(self.eskiRenk.alpha())
        self.renk_ton_degisti_disardan(self.eskiRenk.hsvHue())
        self.renk_seffaflik_degisti_disardan(self.eskiRenk.alpha())
        self.renkSecmeKutusu.halkayi_koordianata_tasi(self.eskiRenk.saturation(), self.eskiRenk.value())

    # ---------------------------------------------------------------------
    def renk_degisimi_bildir(self, renk):
        self.renk = renk
        self.renkDegisti.emit(renk)

    # ---------------------------------------------------------------------
    def renk_ton_degisti_disardan(self, hue):
        self.renkSecmeKutusu.yazRenkTonDisardan(hue)
        self.seffalik_cubugu_arkaplan_degistir(hue)
        self.rTonVeSayiKutusu.blockSignals(True)
        self.rTonVeSayiKutusu.setValue(hue)
        self.rTonVeSayiKutusu.blockSignals(False)

    # ---------------------------------------------------------------------
    def renk_seffaflik_degisti_disardan(self, alpha):
        self.renkSecmeKutusu.yazSeffaflikDisardan(alpha)
        self.rSeffaflikVeSayiKutusu.blockSignals(True)
        self.rSeffaflikVeSayiKutusu.setValue(alpha)
        self.rSeffaflikVeSayiKutusu.blockSignals(False)

    # ---------------------------------------------------------------------
    def renk_ton_degisti_slider(self, hue):
        self.renkSecmeKutusu.yazRenkTon(hue)
        self.seffalik_cubugu_arkaplan_degistir(hue)

    # ---------------------------------------------------------------------
    def renk_seffaflik_degisti_slider(self, alpha):
        self.renkSecmeKutusu.yazSeffaflik(alpha)

    # ---------------------------------------------------------------------
    def seffalik_cubugu_arkaplan_degistir(self, renk_tonu):
        # ########  SEFFAFLIK ARKAPLAN  ################
        gradient = QLinearGradient(0, 0, 1, 0)
        gradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectMode)

        gradient.setColorAt(0, QColor.fromHsv(renk_tonu, 255, 255, 0))
        gradient.setColorAt(1, QColor.fromHsv(renk_tonu, 255, 255, 255))

        self.rSeffaflikVeSayiKutusu.setBgGradient(gradient)


# ---------------------------------------------------------------------
def calistir():
    prog = QApplication(sys.argv)
    prog.setWindowIcon(QIcon(":icons/defter.png"))
    prog.setStyle("fusion")

    pencere = RenkSeciciWidget(QColor(100, 150, 120, 128),
                               )
    pencere.show()

    sys.exit(prog.exec())


# ---------------------------------------------------------------------
if __name__ == "__main__":
    calistir()
