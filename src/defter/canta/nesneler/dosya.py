# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '06/Nov/2018'
__author__ = 'Erdinç Yılmaz'
__license__ = 'GPLv3'

import os
import platform
import subprocess

from PySide6.QtCore import Qt, QSize, QFileInfo, QBuffer, QIODevice
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QStyle, QFileIconProvider

from .. import shared
from ..nesneler.base import BaseItem


########################################################################
class DosyaNesnesi(BaseItem):
    Type = shared.DOSYA_ITEM_TYPE

    # ---------------------------------------------------------------------
    # def __init__(self, filePath, pixmap, rect, arkaPlanRengi, cizgiRengi, parent=None, scene=None):
    def __init__(self, dosyaAdresi, pos, rect, yaziRengi, arkaPlanRengi, pen, font, pixmap=None, isEmbeded=False,
                 parent=None):
        super(DosyaNesnesi, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)

        if os.path.isfile(dosyaAdresi):
            iconProvider = QFileIconProvider()
            self.ikon = iconProvider.icon(QFileInfo(dosyaAdresi))
            self.ikonPixmap = self.ikon.pixmap(self._rect.toRect().size())
        else:
            self.ikonPixmap = QPixmap(':icons/warning.png')

        self.ikonBoyutu = QSize(32, 32)

        self.renk_yazi_alti_kutusu = QColor(255, 255, 255, 155)

        # ikon altinda bir pixmap daha cizmisiz ama niye? iptal edilme adayi...
        if not pixmap:
            self.pixmap = QPixmap()
        else:
            self.pixmap = pixmap
        self.setText(dosyaAdresi)

        self.isEmbeded = isEmbeded
        self.filePathForSave = dosyaAdresi
        if not isEmbeded:
            self.originalSourceFilePath = dosyaAdresi
        else:
            self.originalSourceFilePath = None

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return DosyaNesnesi.Type

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      "kim": self._kim,
                      "isEmbeded": self.isEmbeded,
                      "filePath": self.filePathForSave,
                      "originalSourceFilePath": self.originalSourceFilePath,
                      "rect": self._rect,
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "zValue": self.zValue(),
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "pen": self._pen,
                      "font": self._font,
                      # "imageOpacity": self.imageOpacity,
                      "yaziHiza": int(self.painterTextOption.alignment()),
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "command": self._command,
                      }
        return properties

    # ---------------------------------------------------------------------
    def setRect(self, rect):
        super(DosyaNesnesi, self).setRect(rect)
        if os.path.isfile(self.filePathForSave):
            self.ikonPixmap = self.ikon.pixmap(self._rect.toRect().size())
        else:
            self.ikonPixmap = QPixmap(':icons/warning.png')

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        sistem = platform.system()
        if sistem == "Darwin":
            subprocess.call(('open', self.filePathForSave))
        elif sistem == 'Windows':
            try:
                os.startfile(self.filePathForSave)
            except AttributeError:
                subprocess.call(['open', self.filePathForSave])

        elif sistem == "Linux":
            # subprocess.call(('xdg-open', norm))
            try:
                subprocess.Popen(('xdg-open', self.filePathForSave))
            except Exception as e:
                if subprocess.call(["which", "xdg-open"]) == 1:
                    self.log('---------------------------------------\nPlease install "xdg-open" from your '
                             'package manager. \nMore info at :\nhttps://wiki.archlinux.org/index.php/Xdg-open'
                             '\nor\nhttp://portland.freedesktop.org/xdg-utils-1.0/xdg-open.html\n'
                             '---------------------------------------', 0)
        self.scene().parent().log("File is opening in external editor.", 5000, toStatusBarOnly=True)

        super(BaseItem, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def contextMenuEvent(self, event):
        # TODO: bu alttaki iki satir aktif idi, ve de ctrl harici sag tiklayinca
        # (base - text - path -group nesnelerinin contextMenuEventinde var)
        # mesela birden fazla nesne secili ve de gruplayacagız diyelim sag menu ile
        # ctrl basılı degil ise tikladigimiz secili kaliyor digerleri siliniyordu
        # uygunsuz bir kullanıcı deneyimi, niye yaptık acaba boyleyi hatırlayana kadar kalsın burda :)
        # if not event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        #     self.scene().clearSelection()
        self.setSelected(True)

        # self.scene().parent().item_context_menu(self, event.screenPos())
        self.scene().parent().on_dosya_sag_menu_about_to_show(self)
        self.scene().parent().dosyaSagMenu.popup(event.screenPos())

        event.accept()

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):

        # painter.setClipRect(option.exposedRect)
        # painter.setClipRegion(QRegion(option.exposedRect.toRect()))

        painter.setFont(self._font)
        if not self._pen.width():
            painter.setPen(Qt.PenStyle.NoPen)
        else:
            painter.setPen(self._pen)
        # painter.setPen(QPen(self.cizgiRengi))
        painter.setBrush(self._brush)
        # !! eger kareyi burda cizersek, az sonra cizilen textin alphasinda problem oluyor.
        #   alphayi azalttikca yazi siyahlasiyor, en sonda 0 olunca kayboluyor.
        #   -- o yuzden texti cidikten sonra ciziyoruz bu kareyi deyip bunu iptal etmistik--
        #   ama self.cizgiRengini, QColor().fromrgb ile teker teker aynen yeniden olsuturunca
        #   ve bu yeni kopya renk ile pen olusturunca calısıyor. self.setCizgRengi nde bu islem,
        painter.drawRect(self._rect)
        painter.drawPixmap(self._rect.toRect(), self.pixmap)
        painter.drawPixmap(self._rect.toRect(), self.ikonPixmap)
        # painter.drawPixmap(0,0,self.ikonBoyutu.width(), self.ikonBoyutu.height(), self.ikon.pixmap(self.ikonBoyutu))

        # painter.setWorldMatrixEnabled(False)

        painter.setBrush(self.renk_yazi_alti_kutusu)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self._rect.toRect())

        painter.save()
        # we recreate textPen from same exact color. otherwise, color's alpha not working.
        painter.setPen(self.textPen)
        painter.translate(self._rect.center())
        painter.rotate(-self.rotation())
        painter.translate(-self._rect.center())
        painter.drawText(self.painterTextRect, self.filePathForSave, self.painterTextOption)
        painter.restore()
        # painter.setWorldMatrixEnabled(True)

        # if option.state & QStyle.State_MouseOver:
        if option.state & QStyle.StateFlag.State_Selected or self.cosmeticSelect:
            # painter.setPen(QPen(option.palette.windowText(), 0, Qt.DashLine))
            # painter.setPen(QPen(option.palette.highlight(), 0, Qt.DashLine))

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
            painter.drawRect(self._rect)

            # painter.setPen(self.selectionPenTop)
            # painter.drawRect(self._rect)

            ########################################################################
            # !!! simdilik iptal, gorsel fazlalik olusturmakta !!!
            ########################################################################
            # if not self.isPinned and self.isActiveItem:
            # painter.setPen(Qt.PenStyle.NoPen)
            # painter.setBrush(self.handleBrush)
            # painter.drawRect(self.topLeftHandle)
            # painter.drawRect(self.topRightHandle)
            # painter.drawRect(self.bottomRightHandle)
            # painter.drawRect(self.bottomLeftHandle)
            ########################################################################

        # if option.state & QStyle.StateFlag.State_MouseOver:
        #     painter.setBrush(Qt.BrushStyle.NoBrush)
        #     painter.setPen(self.selectionPenBottom)
        #     painter.drawRect(self._rect)

        # font = painter.font()
        # font.setPointSize(self.fontPointSize)
        # painter.setFont(font)

        # # karenin altina yazsin yaziyi amcli ama bounding bozu degistirmek lazim.
        # # klasin simdilik.
        # # metrics.size() # this is metrics.boundingRect() size.
        # rect = metrics.boundingRect(self.text)
        # rect.moveTop(brect.bottom())
        # painter.drawText(rect, Qt.AlignCenter, self.text)

        # # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self._rect, "{0:.2f},  {1:.2f}\n{2:.2f},  {3:.2f}".format(p.x(), p.y(), s.x(), s.y()))
        # # t = self.transformOriginPoint()
        # # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self._rect.topLeft())
        # painter.drawText(self._rect.x(), self._rect.y(), "{0:.2f}  {1:.2f}".format(mapped.x(), mapped.y()))
        # r = self.textItem.boundingRect()
        # r = self.mapRectFromItem(self.textItem, r)
        # painter.drawRect(r)
        # painter.drawText(self._rect.center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):

        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        self.ikonPixmap.save(buffer, "PNG")

        ikon_base64_buffer = buffer.data().toBase64()
        # ikon_base64_buffer = buffer.data().toBase64(QByteArray.Base64UrlEncoding)
        ikon_str = ikon_base64_buffer.data().decode("ascii")  # "utf-8" olmaz burda, binary.
        # print(ikon_str)

        # resim_adres= f'<img src="{item.filePathForSave}" style="object-fit: fill;"></img>'
        # img_str = f'<img src="{self.filePathForSave}" style="width:100%; height:100%;"></img>'

        dosya_adi = os.path.basename(self.filePathForSave)
        dosya_adres = self.filePathForSave
        if not html_klasor_kayit_adres:  # def dosyasi icine kaydet
            if self.isEmbeded:
                dosya_adres = os.path.join("files", dosya_adi)
        else:  # dosya html olarak baska bir yere kaydediliyor
            # kopyalanmazsa da, zaten embed olmayan dosya normal hddeki adresten yuklenecektir.
            if dosya_kopyalaniyor_mu:
                if not self.isEmbeded:  # embed ise zaten tmp klasorden hedef klasore baska metodta kopylanıyor hepsi.
                    dosya_adres = os.path.join(html_klasor_kayit_adres, "files", dosya_adi)

        a_str = f'<a href="{dosya_adres}">{dosya_adi}</a>'

        x = self.scenePos().x()
        y = self.scenePos().y()
        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = x - xs
        y = y - ys

        bicimSozluk = self.ver_karakter_bicimi()
        bold = "font-weight:bold;" if bicimSozluk["b"] else ""
        italic = "font-style:italic;" if bicimSozluk["i"] else ""
        underline = "underline" if bicimSozluk["u"] else ""
        strikeOut = "line-through" if bicimSozluk["s"] else ""
        overline = "overline" if bicimSozluk["o"] else ""
        bicimler1 = bold + italic
        if any((underline, strikeOut, overline)):
            bicimler2 = f"text-decoration: {underline} {strikeOut} {overline};"
        else:
            bicimler2 = ""

        renk_arkaPlan = f"({self.arkaPlanRengi.red()},{self.arkaPlanRengi.green()},{self.arkaPlanRengi.blue()},{self.arkaPlanRengi.alpha() / 255})"
        renk_yazi = f"({self.yaziRengi.red()},{self.yaziRengi.green()},{self.yaziRengi.blue()},{self.yaziRengi.alpha() / 255})"

        div_str = f"""
                    <div style="
                     background:rgba{renk_arkaPlan};
                     background-image:url('data:image/png;base64,{ikon_str}');
                     background-repeat:no-repeat;
                     background-position:center;
                     color:rgba{renk_yazi};
                     font-size:{self.fontPointSizeF()}pt; 
                     font-family:{self.font().family()};
                     {bicimler1}
                     {bicimler2}
                     position:absolute;
                     z-index:{int(self.zValue() * 10) if self.zValue() else 0};
                     width:{self.sceneWidth()}px;
                     height:{self.sceneHeight()}px;
                     top:{y}px;
                     left:{x}px;" id="{self._kim}">{a_str}</div>\n"""

        # /*background-image:url('{resim_adres}');*/
        return div_str
