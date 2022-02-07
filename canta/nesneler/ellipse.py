# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '3/28/16'

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QStyle
from canta.nesneler.base import BaseItem
from canta import shared


########################################################################
class Ellipse(BaseItem):
    Type = shared.ELLIPSE_ITEM_TYPE

    # ---------------------------------------------------------------------
    def __init__(self, pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent=None):
        super(Ellipse, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return Ellipse.Type

    # ---------------------------------------------------------------------
    def shape(self):
        path = QPainterPath()
        if self._rect.isNull():
            return path
        # path = super(Ellipse, self).shape()
        # path.addEllipse(self.boundingRect())

        path.addEllipse(self._rect)
        # path.addRect(self._rect)
        if not self.isPinned:
            path.addRect(self.topLeftHandle)
            path.addRect(self.topRightHandle)
            path.addRect(self.bottomRightHandle)
            path.addRect(self.bottomLeftHandle)
        # return path
        return self.qt_graphicsItem_shapeFromPath(path, self._pen)

    # TODO: self.shape().controlPointRect() normalde calisiyordu, fakat resize ile ilgili
    # setPos ve moveTo(0,0) ile alakali bazi yeni durumlar ortaya cikti su an gerek yok. o yuzden
    # iptal edildi, basedei boundingRect methodu gayet yeterli burda da. 
    # # ---------------------------------------------------------------------
    # def boundingRect(self):
    #
    #     if self._boundingRect.isNull():
    #         # simdilik alttaki blok yerine bu alttaki satir
    #         self._boundingRect = self.shape().controlPointRect()
    #
    #         # pw = self.pen().widthF()
    #         # if not pw:
    #         #     # normalde self_rect yeterli, ama handlelar disarda kaliyor
    #         #     # ellipse handle sizedan kucuk olunca, shape() icine de handlelari
    #         #     # dahil ettigimizden, shape().controlPointRect() calisiyor.
    #         #     # self._boundingRect = self._rect
    #         #     self._boundingRect = self.shape().controlPointRect()
    #         # else:
    #         #     self._boundingRect = self.shape().controlPointRect()
    #         #     # self.shape().boundingRect() daha yavaş contolPointe gore.
    #         #     # self._boundingRect = self.shape().boundingRect()
    #
    #     return self._boundingRect

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):

        if not self._pen.width():
            painter.setPen(Qt.NoPen)
        else:
            painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawEllipse(self._rect)
        # painter.drawEllipse(self.boundingRect())

        if self.text():
            painter.save()
            painter.setFont(self._font)
            painter.translate(self._rect.center())
            painter.rotate(-self.rotation())

            painter.scale(self.painterTextScale, self.painterTextScale)
            painter.translate(-self._rect.center())

            # ---------------------------------------------------------------------
            # --  basla --  elided text cizmek icin --
            # ---------------------------------------------------------------------
            # metrics = painter.fontMetrics()
            # text = metrics.elidedText(self._text, Qt.ElideRight, self._rect.width() / self.painterTextScale)
            # painter.drawText(self._rect, Qt.AlignCenter, text)
            # ---------------------------------------------------------------------
            # ---  bitir --- elided text cizmek icin --
            # ---------------------------------------------------------------------
            painter.setPen(self.yaziRengi)
            painter.drawText(self.painterTextRect, self._text, self.painterTextOption)

            painter.restore()
        # painter.setWorldMatrixEnabled(True)

        if option.state & QStyle.State_Selected or self.cosmeticSelect:

            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
            else:
                selectionPenBottom = self.selectionPenBottom

            painter.setBrush(Qt.NoBrush)

            painter.setPen(selectionPenBottom)
            painter.drawEllipse(self.rect())

            # painter.setPen(self.selectionPenTop)
            # painter.drawEllipse(self.rect())

            if not self.isPinned:
                painter.setPen(selectionPenBottom)
                # painter.drawRect(self.boundingRect())
                painter.drawRect(self.rect())

                # painter.setPen(self.selectionPenTop)
                # painter.drawRect(self.boundingRect())
                # painter.drawRect(self.rect())

                # draw handles
                painter.drawRect(self.topLeftHandle)
                painter.drawRect(self.topRightHandle)
                painter.drawRect(self.bottomRightHandle)
                painter.drawRect(self.bottomLeftHandle)
