# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '5/4/16'

from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Signal, Slot


#######################################################################
class Slider(QSlider):
    valueChangedFromSliderGuiNotBySetValue = Signal(int)

    # valueChangedWithSetValue = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(Slider, self).__init__(parent)
        self.kodIleSetEdiliyor = False
        self.valueChanged.connect(self.on_value_changed)

    # ---------------------------------------------------------------------
    def setValue(self, val):
        self.kodIleSetEdiliyor = True
        # self.setValue(val)
        QSlider.setValue(self, val)
        self.kodIleSetEdiliyor = False

    @Slot(int)
    def on_value_changed(self, val):
        if not self.kodIleSetEdiliyor:
            self.valueChangedFromSliderGuiNotBySetValue.emit(val)
        # else:
        #     self.valueChangedWithSetValue.emit(val)
