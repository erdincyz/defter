# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '2/14/21'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

from canta.sliderRenk import SliderRenk
from canta.spinBoxlar import SpinBox


#######################################################################
class RenkCubuguVeSayiKutusu(QWidget):
    degerDegisti = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, baslik, yerlesim=Qt.Horizontal, parent=None):
        super(RenkCubuguVeSayiKutusu, self).__init__(parent)

        if yerlesim == Qt.Horizontal:
            anaLay = QHBoxLayout()
        else:
            anaLay = QVBoxLayout()

        self.setLayout(anaLay)
        anaLay.setContentsMargins(0, 0, 0, 0)

        self.slider = SliderRenk(self)
        self.slider.setOrientation(yerlesim)
        if yerlesim == Qt.Horizontal:
            self.slider.setMinimumWidth(100)
        else:
            self.slider.setMinimumHeight(100)

        self.dSpinBox = SpinBox(self)
        self.baslikEtiket = QLabel(baslik, self)

        anaLay.addWidget(self.baslikEtiket)
        anaLay.addWidget(self.slider)
        anaLay.addWidget(self.dSpinBox)
        # anaLay.addStretch()

        self.slider.valueChangedFromSliderGuiNotBySetValue.connect(self.degerDegisti.emit)
        self.dSpinBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.degerDegisti.emit)

        self.slider.valueChanged.connect(self.dSpinBox.setValue)
        self.dSpinBox.valueChanged.connect(self.slider.setValue)

        """
        self.cizgiKalinligiDSBox.setMinimum(0)
        self.cizgiKalinligiDSBox.setMaximum(100)
        self.cizgiKalinligiDSBox.setSingleStep(0.1)"""

    # # ---------------------------------------------------------------------
    # def act_deger_degisti(self, deger):
    #     self.degerDegisti.emit(deger)

    # ---------------------------------------------------------------------
    def setBgGradient(self, bgGradient):
        self.slider.setBgGradient(bgGradient)

    # ---------------------------------------------------------------------
    def yazBaslik(self, yazi):
        self.baslikEtiket.setText(yazi)

    # ---------------------------------------------------------------------
    def setValue(self, deger):
        self.slider.setValue(deger)
        self.dSpinBox.setValue(deger)

    # ---------------------------------------------------------------------
    def setMinimum(self, deger):
        self.slider.setMinimum(deger)
        self.dSpinBox.setMinimum(deger)

    # ---------------------------------------------------------------------
    def setMaximum(self, deger):
        self.slider.setMaximum(deger)
        self.dSpinBox.setMaximum(deger)

    # ---------------------------------------------------------------------
    def setRange(self, minimum, maximum):
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    # ---------------------------------------------------------------------
    def setSingleStep(self, deger):
        self.dSpinBox.setSingleStep(deger)
        # self.slider.setSingleStep(deger)
