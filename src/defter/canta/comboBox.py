# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '5/5/16'

from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Signal, Slot


#######################################################################
class ComboBox(QComboBox):
    currentIndexChangedFromComboBoxGuiNotBySetCurrentIndex = Signal(int)

    # valueChangedWithSetValue = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(ComboBox, self).__init__(parent)
        self.kodIleSetEdiliyor = False
        self.currentIndexChanged.connect(self.on_current_index_changed)

    # ---------------------------------------------------------------------
    def setCurrentIndex(self, idx):
        self.kodIleSetEdiliyor = True
        # self.setValue(val)
        QComboBox.setCurrentIndex(self, idx)
        self.kodIleSetEdiliyor = False

    @Slot(int)
    def on_current_index_changed(self, idx):
        if not self.kodIleSetEdiliyor:
            self.currentIndexChangedFromComboBoxGuiNotBySetCurrentIndex.emit(idx)
        # else:
        #     self.valueChangedWithSetValue.emit(val)
