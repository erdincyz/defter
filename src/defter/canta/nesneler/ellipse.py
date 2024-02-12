# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QStyle
from ..nesneler.base import BaseItem
from .. import shared


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

    # ---------------------------------------------------------------------
    def boundingRect(self):
        return self.shape().controlPointRect()

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
            painter.setPen(Qt.PenStyle.NoPen)
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

        if option.state & QStyle.StateFlag.State_Selected or self.cosmeticSelect:

            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
                if not self.isPinned:

                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(self.handleBrush)
                    painter.drawRect(self.topLeftHandle)
                    painter.drawRect(self.topRightHandle)
                    painter.drawRect(self.bottomRightHandle)
                    painter.drawRect(self.bottomLeftHandle)
            else:
                selectionPenBottom = self.selectionPenBottom

            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.setPen(selectionPenBottom)
            painter.drawEllipse(self._rect)

            # painter.setPen(self.selectionPenTop)
            # painter.drawEllipse(self._rect)

            if not self.isPinned:
            #     # painter.drawRect(self.boundingRect())
                painter.drawRect(self._rect)
            #
            #     painter.setPen(Qt.PenStyle.NoPen)
            #     painter.setBrush(self.handleBrush)
            #     # painter.setPen(self.selectionPenTop)
            #     # painter.drawRect(self.boundingRect())
            #     # painter.drawRect(self._rect)
            #
            #     # draw handles
            #     painter.drawRect(self.topLeftHandle)
            #     painter.drawRect(self.topRightHandle)
            #     painter.drawRect(self.bottomRightHandle)
            #     painter.drawRect(self.bottomLeftHandle)

        # if option.state & QStyle.StateFlag.State_MouseOver:
        #     painter.setBrush(Qt.BrushStyle.NoBrush)
        #     painter.setPen(self.selectionPenBottom)
        #     painter.drawEllipse(self._rect)

        # # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self._rect,
        #                  "{0:.2f},  {1:.2f} pos \n{2:.2f},  {3:.2f} spos".format(p.x(), p.y(), s.x(), s.y()))
        # # # t = self.transformOriginPoint()
        # # # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self._rect.topLeft())
        # painter.drawText(self._rect.x(), self._rect.y(), "{0:.2f}  {1:.2f} map".format(mapped.x(), mapped.y()))
        # painter.drawEllipse(self.scenePos(), 10, 10)
        # painter.setPen(Qt.blue)
        # painter.drawEllipse(self.mapFromScene(self.pos()), 10, 10)
        # r = self.textItem.boundingRect()
        # r = self.mapRectFromItem(self.textItem, r)
        # painter.drawRect(r)
        # painter.drawText(self._rect.center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # painter.setPen(QPen(Qt.red,17))
        # painter.drawPoint(self._rect.center())
        # painter.setPen(QPen(Qt.green,12))
        # painter.drawPoint(self.mapFromScene(self.sceneBoundingRect().center()))
        # painter.setPen(QPen(Qt.blue,8))
        # painter.drawPoint(self.sceneBoundingRect().center())
        # painter.drawRect(self.sceneBoundingRect())
        # # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):

        arkaPlanRengi = self.arkaPlanRengi.toRgb()
        yaziRengi = self.yaziRengi.toRgb()
        cizgiRengi = self.cizgiRengi.toRgb()

        w = self._rect.width()
        h = self._rect.height()

        c = self.sceneBoundingRect().center()

        xr = c.x() - w / 2
        yr = c.y() - h / 2
        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = xr - xs
        y = yr - ys

        bicimSozluk = self.ver_karakter_bicimi()
        bold = 'font-weight="bold" ' if bicimSozluk["b"] else ''
        italic = ' font-style="italic"' if bicimSozluk["i"] else ''
        underline = "underline" if bicimSozluk["u"] else ''
        strikeOut = "line-through" if bicimSozluk["s"] else ''
        overline = "overline" if bicimSozluk["o"] else ''
        bicimler1 = bold + italic
        if any((underline, strikeOut, overline)):
            bicimler2 = f'text-decoration= "{underline} {strikeOut} {overline}"'
        else:
            bicimler2 = ''

        hiza = self.ver_yazi_hizasi()
        # if hiza == Qt.AlignmentFlag.AlignLeft or hiza == Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter:
        #     yazi_hiza = "left"
        if hiza == Qt.AlignmentFlag.AlignCenter or hiza == Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter:
            yazi_hiza = "center"
        elif hiza == Qt.AlignmentFlag.AlignRight or hiza == Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter:
            yazi_hiza = "right"
        elif hiza == Qt.AlignmentFlag.AlignJustify or hiza == Qt.AlignmentFlag.AlignJustify | Qt.AlignmentFlag.AlignVCenter:
            yazi_hiza = "justify"
        else:
            yazi_hiza = "left"

        if self.rotation():
            dondur_str_eksi = f"""
            transform-box: fill-box;
            transform-origin: center;
            transform: rotate({-self.rotation()}deg);
            """
        else:
            dondur_str_eksi = ''

        # x ="{self.painterTextRect.center().x()}" y="{self.painterTextRect.center().y()}"
        # x ="%50" y="%50" dominant-baseline="middle" text-anchor="middle"
        if self.text():
            yazi_str = f"""
            <text 
            style="{dondur_str_eksi}"
            fill="rgba{yaziRengi.toTuple()}"
            fill-opacity="{yaziRengi.alpha() / 255}"
            stroke="none" xml:space="preserve" 
            text-anchor="middle"
            alignment-baseline="middle"
            x="{w / 2}"
            y="{h / 2}"
            font-family={self.font().family()}
            font-size="{self.fontPointSizeF()}pt"
            {bicimler1}
            {bicimler2}
            text-align="{yazi_hiza}"
             >{self.text()}</text>
            """
        else:
            yazi_str = ""

        ellipse_str = f"""
                  <ellipse
                    style="fill:rgba{arkaPlanRengi.toTuple()};
                    fill-opacity:{arkaPlanRengi.alpha() / 255};
                    stroke:rgba{cizgiRengi.toTuple()};
                    stroke-opacity:{cizgiRengi.alpha() / 255};
                    stroke-width:{self._pen.widthF() * 2};
                    stroke-linecap:round;
                    stroke-dasharray:none;
                    stroke-linejoin:round;
                    paint-order:markers fill stroke;"
                    cx="{w / 2}" cy="{h / 2}" rx="{w / 2 - self._pen.widthF()}" ry="{h / 2 - self._pen.widthF()}"
                   />
        """

        svg_str = f"""
        <?xml version="1.0"?>
            <svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" 
             width="{w}" height="{h}" viewBox="0 0 {w} {h}" >
                {ellipse_str}
                {yazi_str}
              </svg>\n
        """

        div_str = f"""
                    <div style="
                     position:absolute;
                     z-index:{int(self.zValue() * 10) if self.zValue() else 0};
                     width:{w}px;
                     height:{h}px;
                     top:{y}px;
                     left:{x}px;
                     transform-box: fill-box;
                     transform-origin: center;
                     transform: rotate({self.rotation()}deg);"
                      id="{self._kim}">{svg_str}</div>\n
            """
        # return svg_str
        return div_str
