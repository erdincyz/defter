# -*- coding: utf-8 -*-
# .


__project_name__ = 'Defter'
__date__ = '06/Nov/2018'
__author__ = 'argekod'

import os
import subprocess
import sys

from PySide6.QtCore import Qt, QSize, QFileInfo
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QStyle, QFileIconProvider

from canta import shared
from canta.nesneler.base import BaseItem


########################################################################
class DosyaNesnesi(BaseItem):
    Type = shared.DOSYA_ITEM_TYPE

    # ---------------------------------------------------------------------
    # def __init__(self, filePath, pixmap, rect, arkaPlanRengi, cizgiRengi, parent=None, scene=None):
    def __init__(self, dosyaAdresi, pos, rect, yaziRengi, arkaPlanRengi, pen, font, pixmap=None, isEmbeded=False,
                 parent=None):
        super(DosyaNesnesi, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)

        iconProvider = QFileIconProvider()
        self.ikon = iconProvider.icon(QFileInfo(dosyaAdresi))
        self.ikonBoyutu = QSize(32, 32)

        self.renk_yazi_alti_kutusu = QColor(255, 255, 255, 155)

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
                      "rect": self.rect(),
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "scale": self.scale(),
                      "zValue": self.zValue(),
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "pen": self._pen,
                      "font": self._font,
                      # "imageOpacity": self.imageOpacity,
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "command": self._command,
                      }
        return properties

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        if sys.platform == 'darwin':
            subprocess.call(('open', self.filePathForSave))
        elif sys.platform == 'nt' or sys.platform == "win32":
            try:
                os.startfile(self.filePathForSave)
            except AttributeError:
                subprocess.call(['open', self.filePathForSave])

        # elif sys.platform == 'posix' or 'linux2':
        elif sys.platform.startswith('linux'):
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
        # if not event.modifiers() & Qt.ControlModifier:
        #     self.scene().clearSelection()
        self.setSelected(True)

        # self.scene().parent().item_context_menu(self, event.screenPos())
        self.scene().parent().on_item_context_menu_about_to_show(self)
        self.scene().parent().itemContextMenu.popup(event.screenPos())

        event.accept()

    # ---------------------------------------------------------------------
    def onizle(self):

        hedefBoyut = QSize(30, 40)

        pixmap = QPixmap('/path/to/image.png')

        # resize pixmap
        pixmap = pixmap.scaled(hedefBoyut, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # crop pixmap - the following assumes the image aspect is always wider than the button.  if that's not the case
        # you'll need to compare your image/button aspects and crop vertically/horizontally as necessary
        cropOffsetX = (pixmap.width() - hedefBoyut.width()) / 2
        pixmap = pixmap.copy(cropOffsetX, 0, QSize(30, 40).width(), QSize(30, 40).height())

        # icon = QIcon(pixmap)

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):

        # painter.setClipRect(option.exposedRect)
        # painter.setClipRegion(QRegion(option.exposedRect.toRect()))

        painter.setFont(self._font)
        if not self._pen.width():
            painter.setPen(Qt.NoPen)
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
        painter.drawPixmap(self._rect.toRect(), self.ikon.pixmap(self._rect.toRect().size()))
        # painter.drawPixmap(0,0,self.ikonBoyutu.width(), self.ikonBoyutu.height(), self.ikon.pixmap(self.ikonBoyutu))

        # painter.setWorldMatrixEnabled(False)
        painter.save()
        # we recreate textPen from same exact color. otherwise, color's alpha not working.
        painter.setPen(self.textPen)
        painter.translate(self._rect.center())
        painter.rotate(-self.rotation())

        painter.scale(self.painterTextScale, self.painterTextScale)
        painter.translate(-self._rect.center())

        # ---------------------------------------------------------------------
        # --  basla --  elided text cizmek icin --
        # ---------------------------------------------------------------------
        # metrics = painter.fontMetrics()
        # txt = metrics.elidedText(self._text, Qt.ElideRight, self._rect.width() / scale)
        # # Qt.AlignCenter hem AlignVCenter hem de AlignHCenter icin yeterli
        # # ayrica en fazla iki tane kullanilabiliyormus, ve AlignCenter 2 tane sayiliyormus.
        # # painter.drawText(self._rect, Qt.AlignCenter | Qt.AlignVCenter, txt)
        # painter.drawText(self._rect, Qt.AlignCenter, txt)
        # ---------------------------------------------------------------------
        # ---  bitir --- elided text cizmek icin --
        # ---------------------------------------------------------------------

        # painter.drawRect(r)
        # painter.drawText(self._rect, self._text, self.painterTextOption)
        # painter.drawText(self.painterTextRect, self._text, self.painterTextOption)

        painter.save()
        painter.setBrush(self.renk_yazi_alti_kutusu)
        painter.setPen(Qt.NoPen)

        # metrics = painter.fontMetrics()
        # r = QRectF(metrics.boundingRect(self._rect.toRect(), Qt.TextWrapAnywhere, self._text))
        # r.moveCenter(self._rect.center())
        # # draw text background rect
        # painter.drawRect(r.intersected(self._rect))

        painter.drawRect(self._rect.toRect())
        painter.restore()

        painter.drawText(self.painterTextRect, self.filePathForSave, self.painterTextOption)

        # painter.drawText(10,10, txt)
        painter.restore()
        # painter.setWorldMatrixEnabled(True)

        # if option.state & QStyle.State_MouseOver:
        if option.state & QStyle.State_Selected or self.cosmeticSelect:
            # painter.setPen(QPen(option.palette.windowText(), 0, Qt.DashLine))
            # painter.setPen(QPen(option.palette.highlight(), 0, Qt.DashLine))

            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
            else:
                selectionPenBottom = self.selectionPenBottom

            painter.setBrush(Qt.NoBrush)

            painter.setPen(selectionPenBottom)
            painter.drawRect(self.rect())

            # painter.setPen(self.selectionPenTop)
            # painter.drawRect(self.rect())

            ########################################################################
            # !!! simdilik iptal, gorsel fazlalik olusturmakta !!!
            ########################################################################
            # if not self.isPinned and self.isActiveItem:
            #     # painter.setPen(self.handlePen)
            #     painter.drawRect(self.topLeftHandle)
            #     painter.drawRect(self.topRightHandle)
            #     painter.drawRect(self.bottomRightHandle)
            #     painter.drawRect(self.bottomLeftHandle)
            ########################################################################

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
        # painter.drawText(self.rect(), "{0:.2f},  {1:.2f}\n{2:.2f},  {3:.2f}".format(p.x(), p.y(), s.x(), s.y()))
        # # t = self.transformOriginPoint()
        # # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self.rect().topLeft())
        # painter.drawText(self.rect().x(), self.rect().y(), "{0:.2f}  {1:.2f}".format(mapped.x(), mapped.y()))
        # r = self.textItem.boundingRect()
        # r = self.mapRectFromItem(self.textItem, r)
        # painter.drawRect(r)
        # painter.drawText(self.rect().center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # # # # # # debug end - pos() # # # # #
