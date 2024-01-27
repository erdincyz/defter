# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '15/2/23'
__author__ = 'E. Y.'

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QProgressBar, QLabel


#######################################################################
class LutfenBekleyin(QWidget):

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(LutfenBekleyin, self).__init__(parent)

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        layCubuk = QVBoxLayout()
        layCubuk.setContentsMargins(0, 4, 0, 0)
        self.setLayout(lay)
        self.yuzdeCubuk = QProgressBar(self)
        self.yuzdeCubuk.setMaximumWidth(200)
        self.yuzdeCubuk.setMaximumHeight(15)
        self.yuzdeCubuk.setMinimum(0)
        self.yuzdeCubuk.setMaximum(0)
        # font = self.yuzdeCubuk.font()
        # font.setPointSizeF(8)
        # self.yuzdeCubuk.setFont(font)

        etiket = QLabel(self.tr("Please wait"), self)
        # etiket.move(30, 0)
        lay.addStretch()
        lay.addWidget(etiket)
        layCubuk.addWidget(self.yuzdeCubuk)
        lay.addLayout(layCubuk)

    # ---------------------------------------------------------------------
    def yuzdeCubukEnCokDeger(self):
        return self.yuzdeCubuk.maximum()

    # ---------------------------------------------------------------------
    def belirsiz_yuzde_moduna_al(self):
        self.yuzdeCubuk.setMaximum(0)

    # ---------------------------------------------------------------------
    def belirli_yuzde_moduna_al(self, encok_deger: int):
        self.yuzdeCubuk.setValue(0)
        self.yuzdeCubuk.setMaximum(encok_deger)

    # ---------------------------------------------------------------------
    def simdiki_deger_gir(self, deger: int):
        self.yuzdeCubuk.setValue(deger)
