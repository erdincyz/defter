# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '2/14/21'
__author__ = 'Erdinç Yılmaz'

# from PySide6.QtGui import
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal

from .spinBoxlar import DoubleSpinBox
from .slider import Slider


#######################################################################
class SliderDoubleWithDoubleSpinBox(QWidget):
    degerDegisti = Signal(float)

    # ---------------------------------------------------------------------
    def __init__(self, yerlesim=Qt.Orientation.Horizontal, parent=None):
        super(SliderDoubleWithDoubleSpinBox, self).__init__(parent)

        if yerlesim == Qt.Orientation.Horizontal:
            anaLay = QHBoxLayout()
        else:
            anaLay = QVBoxLayout()

        self.setLayout(anaLay)
        anaLay.setContentsMargins(0, 0, 0, 0)

        self.slider = Slider(self)
        self.slider.setOrientation(yerlesim)
        self.dSpinBox = DoubleSpinBox(self)

        anaLay.addWidget(self.slider)
        anaLay.addWidget(self.dSpinBox)
        # anaLay.addStretch()

        self.slider.valueChangedFromSliderGuiNotBySetValue.connect(lambda x: self.degerDegisti.emit(x / 10))
        self.dSpinBox.valueChangedFromDoubleSpinBoxGuiNotBySetValue.connect(lambda x: self.degerDegisti.emit(x))

        self.slider.valueChanged.connect(lambda x: self.dSpinBox.setValue(x / 10))
        self.dSpinBox.valueChanged.connect(lambda x: self.slider.setValue(x * 10))

        """
        self.cizgiKalinligiDSBox.setMinimum(0)
        self.cizgiKalinligiDSBox.setMaximum(100)
        self.cizgiKalinligiDSBox.setSingleStep(0.1)"""

    # # ---------------------------------------------------------------------
    # def act_deger_degisti(self, deger):
    #     self.degerDegisti.emit(deger)

    # ---------------------------------------------------------------------
    def setValue(self, deger):
        self.slider.setValue(deger * 10)
        self.dSpinBox.setValue(deger / 10)

    # ---------------------------------------------------------------------
    def setMinimum(self, deger):
        self.slider.setMinimum(deger)
        self.dSpinBox.setMinimum(deger)

    # ---------------------------------------------------------------------
    def setMaximum(self, deger):
        self.slider.setMaximum(deger * 10)
        self.dSpinBox.setMaximum(deger)

    # ---------------------------------------------------------------------
    def setRange(self, minimum, maximum):
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    # ---------------------------------------------------------------------
    def setSingleStep(self, deger):
        self.dSpinBox.setSingleStep(deger)
        # self.slider.setSingleStep(deger)
