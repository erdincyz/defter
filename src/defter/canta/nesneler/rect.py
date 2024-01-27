# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtCore import Qt
from ..nesneler.base import BaseItem
from .. import shared


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
        # if hiza == Qt.AlignLeft or hiza == Qt.AlignLeft | Qt.AlignVCenter:
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
            # dondur_str = f'transform="rotate({self.rotation()},{x+w/2},{y+h/2})"'
            dondur_str_eksi = f"""transform-box: fill-box;
                                  transform-origin: center;
                                  transform: rotate({-self.rotation()}deg);"""
            # dondur_str = f"""
            # transform-box: fill-box;
            # transform-origin: center;
            # transform: rotate({self.rotation()}deg);
            # """

        else:
            # dondur_str =''
            dondur_str_eksi = ''

        # x="{self.painterTextRect.center().x()}" y="{self.painterTextRect.center().y()}"
        # x="%50" y="%50" dominant-baseline="middle" text-anchor="middle" 
        if self.text():
            yazi_str = f"""
            <text style="{dondur_str_eksi}"
            fill="rgba{yaziRengi.toTuple()}" fill-opacity="{yaziRengi.alpha() / 255}"
            stroke="none" xml:space="preserve" 
            x="{w / 2}" y="{h / 2}" text-anchor="middle" alignment-baseline="middle"
            font-family={self.font().family()} font-size="{self.fontPointSizeF()}pt"
            {bicimler1} {bicimler2} text-align="{yazi_hiza}">{self.text()}</text>
            """
        else:
            yazi_str = ""

        rect_str = f"""
        <rect width="{w}" height="{h}" x="0" y="0"
                   style="fill:rgba{arkaPlanRengi.toTuple()};
                   fill-opacity:{arkaPlanRengi.alpha() / 255};
                   stroke:rgba{cizgiRengi.toTuple()};
                   stroke-opacity:{cizgiRengi.alpha() / 255};
                   stroke-width:{self._pen.widthF() * 2};
                   stroke-linecap:round; stroke-dasharray:none; stroke-linejoin:round;
                   paint-order:markers fill stroke;"/>
        """

        svg_str = f"""
        <?xml version="1.0"?>
        <svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" 
            width="{w}" height="{h}" viewBox="0 0 {w} {h}" >
        {rect_str}
        {yazi_str}
        </svg>\n
        """

        div_str = f"""
        <div id="{self._kim}"
            style="position:absolute;
                   z-index:{int(self.zValue() * 10) if self.zValue() else 0};
                   width:{w}px; height:{h}px; top:{y}px; left:{x}px; 
                   transform-box: fill-box; 
                   transform-origin: center; 
                   transform: rotate({self.rotation()}deg);">{svg_str}</div>\n
        """
        # return svg_str
        return div_str
