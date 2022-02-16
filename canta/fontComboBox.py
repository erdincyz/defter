# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '18/Aug/2016'

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QFontComboBox
from PySide6.QtGui import QFont


#######################################################################
class FontComboBox(QFontComboBox):
    valueChangedFromFontComboBoxGuiNotByCode = Signal(QFont)

    # valueChangedWithSetValue = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(FontComboBox, self).__init__(parent)
        self.kodIleSetEdiliyor = False
        self.currentFontChanged.connect(self.on_current_font_changed)

    # ---------------------------------------------------------------------
    def setCurrentFont(self, font):
        self.kodIleSetEdiliyor = True
        # self.setValue(val)
        QFontComboBox.setCurrentFont(self, font)
        self.kodIleSetEdiliyor = False

    # ---------------------------------------------------------------------
    @Slot(QFont)
    def on_current_font_changed(self, font):
        if not self.kodIleSetEdiliyor:
            self.valueChangedFromFontComboBoxGuiNotByCode.emit(font)
        # else:
        #     self.valueChangedWithSetValue.emit(val)
