# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtCore import Qt
from .. import shared


########################################################################
class MirrorLine(QGraphicsLineItem):
    Type = shared.MIRRORLINE_TYPE

    # ---------------------------------------------------------------------
    def __init__(self, posFeedback, axis, parent=None):
        super(MirrorLine, self).__init__(parent)

        # self.setFlag(QGraphicsLineItem.ItemIgnoresTransformations, True)
        self._kim = shared.kim(kac_basamak=16)
        pen = QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.DashDotDotLine)
        self.setPen(pen)
        self.setZValue(10000)

        self.axis = axis
        self.textItem = QGraphicsTextItem()
        self.textItem.setParentItem(self)
        self.textItem.setPos(posFeedback)
        self.textItem.setDefaultTextColor(Qt.GlobalColor.blue)
        self.textItem.setPlainText("    {}: {}".format(self.axis, posFeedback.x()))

    # def setLine(self):
    # def paint(self, painter, option, widget=None):
    #     super(MirrorLine, self).paint(painter, option, widget)

    # ---------------------------------------------------------------------
    def updateScale(self):
        yeniOran = 1 / self.scene().views()[0].viewportTransform().m11()
        # init te pen kalinligi 1 dolayisi ile 1 / viewscale den gelen degeri direkt
        #  kalem kalinligina ve de textItem in scale ine uyguluyabiliyoruz.
        # ilk ve hep istenen deger baska olaydi, o degere bolmek gerekirdi o degeri cekip.
        pen = self.pen()
        pen.setWidthF(yeniOran)
        self.setPen(pen)
        self.textItem.setScale(yeniOran)

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return MirrorLine.Type

    # ---------------------------------------------------------------------
    def updatePosFeedBack(self, posFeedback):
        self.textItem.setPos(posFeedback)
        if self.axis == "x":
            pos = posFeedback.x()
        else:
            pos = posFeedback.y()
        self.textItem.setPlainText("    {}: {}".format(self.axis, pos))

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):
        # Ola ki bu nesne aktif iken HTML olarak kaydet cagrilirsa diye
        # None dondurmeyelim stringe ekleniyor bu
        return ""
