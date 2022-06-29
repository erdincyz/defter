# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
from PySide6.QtCore import Signal, Slot


#######################################################################
class DoubleSpinBox(QDoubleSpinBox):
    valueChangedFromDoubleSpinBoxGuiNotBySetValue = Signal(float)

    # valueChangedWithSetValue = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(DoubleSpinBox, self).__init__(parent)
        self.kodIleSetEdiliyor = False
        self.valueChanged.connect(self.on_value_changed)

    # ---------------------------------------------------------------------
    def setValue(self, val):
        self.kodIleSetEdiliyor = True
        # self.setValue(val)
        QDoubleSpinBox.setValue(self, val)
        self.kodIleSetEdiliyor = False

    @Slot(float)
    def on_value_changed(self, val):
        if not self.kodIleSetEdiliyor:
            self.valueChangedFromDoubleSpinBoxGuiNotBySetValue.emit(val)
        # else:
        #     self.valueChangedWithSetValue.emit(val)


#######################################################################
class SpinBox(QSpinBox):
    valueChangedFromSpinBoxGuiNotBySetValue = Signal(int)

    # valueChangedWithSetValue = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(SpinBox, self).__init__(parent)
        self.kodIleSetEdiliyor = False
        self.valueChanged.connect(self.on_value_changed)

    # ---------------------------------------------------------------------
    def setValue(self, val):
        self.kodIleSetEdiliyor = True
        # self.setValue(val)
        QSpinBox.setValue(self, val)
        self.kodIleSetEdiliyor = False

    @Slot(int)
    def on_value_changed(self, val):
        if not self.kodIleSetEdiliyor:
            self.valueChangedFromSpinBoxGuiNotBySetValue.emit(val)
        # else:
        #     self.valueChangedWithSetValue.emit(val)


#######################################################################
class SpinBoxForRotation(QSpinBox):
    valueChangedFromSpinBoxGuiNotBySetValue = Signal(int)

    # valueChangedWithSetValue = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(SpinBoxForRotation, self).__init__(parent)
        self.kodIleSetEdiliyor = False
        self.valueChanged.connect(self.on_value_changed)

    # ---------------------------------------------------------------------
    def setValue(self, val):
        self.kodIleSetEdiliyor = True
        # self.setValue(val)
        val %= 360
        if val < 0:
            val += 360
        QSpinBox.setValue(self, val)
        self.kodIleSetEdiliyor = False

    @Slot(int)
    def on_value_changed(self, val):
        val %= 360
        if val < 0:
            val += 360
        QSpinBox.setValue(self, val)
        if not self.kodIleSetEdiliyor:
            self.valueChangedFromSpinBoxGuiNotBySetValue.emit(val)
        # else:
        #     self.valueChangedWithSetValue.emit(val)
