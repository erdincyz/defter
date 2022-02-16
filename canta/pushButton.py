# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '2/7/21'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal


########################################################################
class PushButton(QPushButton):
    sagTiklandi = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, yazi, genislik, yukseklik, renkArkaplan=None, parent=None):
        super(PushButton, self).__init__(yazi, parent)

        self.renkArkaplan = renkArkaplan
        if renkArkaplan:
            self.arkaplan_rengi_degistir(renkArkaplan)

        self.setFixedWidth(genislik)
        self.setFixedHeight(yukseklik)

    # ---------------------------------------------------------------------
    def arkaplan_rengi_degistir(self, renkArkaplan):
        self.setFlat(True)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), renkArkaplan)
        self.setPalette(p)
        self.renkArkaplan = renkArkaplan

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.sagTiklandi.emit()
            event.accept()

        super(PushButton, self).mousePressEvent(event)
