# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '20/12/21'

from PySide6.QtGui import (QBrush, QPainterPath, QPainterPathStroker)
from PySide6.QtWidgets import (QGraphicsItem)
from PySide6.QtCore import (QRectF, Qt)
from .. import shared


########################################################################
class YuvarlakFircaBoyutu(QGraphicsItem):
    Type = shared.YUVARLAK_FIRCA_BOYUTU_ITEM_TYPE

    # ---------------------------------------------------------------------
    def __init__(self, pos, rect, arkaPlanRengi, pen, parent=None):
        super(YuvarlakFircaBoyutu, self).__init__(parent)

        self._kim = shared.kim(kac_basamak=16)

        self.setPos(pos)
        self._rect = rect
        self._boundingRect = QRectF()

        self.secili_nesne_kalem_kalinligi = 0

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        self._pen = pen
        self._brush = QBrush()

        self.cizgiRengi = pen.color()
        self.setCizgiRengi(self.cizgiRengi)  # also sets self._pen
        self.setArkaPlanRengi(arkaPlanRengi)  # also sets self._brush

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return YuvarlakFircaBoyutu.Type

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):
        # Ola ki bu nesne aktif iken HTML olarak kaydet cagrilirsa diye
        # None dondurmeyelim stringe ekleniyor bu
        return ""

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):
        # shift ile firca boyutu degistirirken, altta cizilen nesneyi dondurebiliyordu
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            event.accept()
        # else:
        #     super(BaseItem, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):

        if not self._pen.width():
            painter.setPen(Qt.PenStyle.NoPen)
        else:
            painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawEllipse(self._rect)
        # painter.drawEllipse(self.boundingRect())

    # ---------------------------------------------------------------------
    def setRect(self, rect):
        if self._rect == rect:
            return
        self.prepareGeometryChange()
        self._rect = rect
        self._boundingRect = QRectF()
        self.update()

    # ---------------------------------------------------------------------
    def rect(self):
        return self._rect

    # ---------------------------------------------------------------------
    def setPen(self, pen):

        if self._pen == pen:
            return
        self.prepareGeometryChange()
        self._pen = pen
        self._boundingRect = QRectF()
        self.update(self.boundingRect())

    # ---------------------------------------------------------------------
    def pen(self):
        return self._pen

    # ---------------------------------------------------------------------
    def setBrush(self, brush):

        if self._brush == brush:
            return
        self._brush = brush
        self.update()

    # ---------------------------------------------------------------------
    def brush(self):
        return self._brush

    # ---------------------------------------------------------------------
    def setCizgiRengi(self, col):

        self._pen.setColor(col)
        self.cizgiRengi = col

        self.update()

    # ---------------------------------------------------------------------
    def setCizgiKalinligi(self, width):
        self._pen.setWidthF(width)
        self.update()

    # ---------------------------------------------------------------------
    def setArkaPlanRengi(self, col):
        self.arkaPlanRengi = col
        self.setBrush(QBrush(col))

    # ---------------------------------------------------------------------
    def shape(self):
        path = QPainterPath()
        if self._rect.isNull():
            return path
        # path = super(YuvarlakFircaBoyutu, self).shape()
        # path.addEllipse(self.boundingRect())

        path.addEllipse(self._rect)
        return self.qt_graphicsItem_shapeFromPath(path, self._pen)

    # ---------------------------------------------------------------------
    def boundingRect(self):
        self._boundingRect = QRectF(self.rect())
        return self._boundingRect

    # ---------------------------------------------------------------------
    def qt_graphicsItem_shapeFromPath(self, path, pen):

        # We unfortunately need this hack as QPainterPathStroker will set a width of 1.0
        # if we pass a value of 0.0 to QPainterPathStroker.setWidth()
        penWidthZero = 0.00000001
        if path == QPainterPath():
            return path
        ps = QPainterPathStroker()
        ps.setCapStyle(pen.capStyle())

        if pen.widthF() <= 0:
            ps.setWidth(penWidthZero)
        else:
            ps.setWidth(pen.widthF())
        ps.setJoinStyle(pen.joinStyle())
        ps.setMiterLimit(pen.miterLimit())
        p = ps.createStroke(path)  # return type: QPainterPath
        p.addPath(path)
        return p
