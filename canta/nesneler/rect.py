# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtCore import  QBuffer, QIODevice, QSize, QRectF
from PySide6.QtGui import QPainter
from PySide6.QtSvg import QSvgGenerator

from canta.nesneler.base import BaseItem
from canta import shared


########################################################################
class Rect(BaseItem):
    Type = shared.RECT_ITEM_TYPE

    # ---------------------------------------------------------------------
    def __init__(self, pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent=None):
        super(Rect, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return Rect.Type

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):

        # rect = self.mapRectToScene(self.boundingRect())
        rect = self.sceneBoundingRect()
        xr = rect.left()
        yr = rect.top()
        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = xr - xs
        y = yr - ys

        w = rect.width()
        h = rect.height()

        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)

        generator = QSvgGenerator()
        # generator.setFileName("dosya.svg")
        generator.setOutputDevice(buffer)
        # generator.setResolution(72)

        generator.setSize(QSize(w, h))
        generator.setViewBox(QRectF(-w / 2, -h / 2, w, h))
        generator.setTitle(self._kim)
        generator.setDescription("")
        # painter = QPainter(generator)
        painter = QPainter()
        painter.begin(generator)
        painter.save()
        
        diff = self.scenePos() - rect.center()
        cizilecekRect = QRectF(self._rect)
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        cizilecekRect.moveTo(diff)
        painter.translate(diff)
        painter.rotate(self.rotation())
        painter.translate(-diff)
        painter.drawRect(cizilecekRect)
        #painter.rotate(-self.rotation())
        painter.restore()
        if self._text:
            # painter.save()
            painter.setFont(self._font)
            # we recreate textPen from same exact color. otherwise, color's alpha is not working.
            painter.setPen(self.textPen)
            cizilecekTextRect = QRectF(self.painterTextRect)
            cizilecekTextRect.moveCenter(diff-cizilecekRect.topLeft())
            painter.scale(self.painterTextScale, self.painterTextScale)
            painter.drawText(cizilecekTextRect, self._text, self.painterTextOption)
            # painter.restore()
        painter.end()

        svg_string = buffer.data().data().decode("utf-8")

        # background: rgba{self.arkaPlanRengi.toTuple()};\n
        div_str = f"""
                    <div style="
                     position:absolute;
                     z-index:{int(self.zValue()*10)if self.zValue() else 0};
                     width:{w}px;
                     height:{h}px;
                     top:{y}px;
                     left:{x}px;" id="{self._kim}">{svg_string}</div>\n
            """
        # return svg_string
        return div_str
