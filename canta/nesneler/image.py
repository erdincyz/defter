# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

import os
from PySide6.QtCore import Qt, QRectF, QPointF, QSizeF
from PySide6.QtGui import QColor, QPixmap, QTransform, QPixmapCache, QPainter, QPen
from PySide6.QtWidgets import QStyle
from canta.nesneler.base import BaseItem
from canta import shared
from canta.nesneler.text import Text


########################################################################
class Image(BaseItem):
    Type = shared.IMAGE_ITEM_TYPE

    # ---------------------------------------------------------------------
    # def __init__(self, filePath, pixmap, rect, arkaPlanRengi, cizgiRengi, parent=None, scene=None):
    def __init__(self, filePath, pos, rect, yaziRengi, arkaPlanRengi, pen, font, isEmbeded=False, parent=None):
        super(Image, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)

        self.setCacheMode(Image.DeviceCoordinateCache)
        self.isEmbeded = isEmbeded
        self.filePathForSave = filePath
        if not isEmbeded:
            self.originalSourceFilePath = filePath
        else:
            self.originalSourceFilePath = None
        #     #bu zaten embeded ise, file open veya importtan cagriliyor demek, dolayisi ile, ordan direkt set edilsin.

        # isembededi init paramtresine none diye tasınabilir
        # ve eger embeded degilse sourceFilePath de set edilir.

        if os.path.isfile(filePath):
            self.filePathForDraw = filePath
        else:
            self.filePathForDraw = ':icons/warning.png'

        # # self.pixmap = pixmap
        # self.pixmap = QPixmap()
        # if not QPixmapCache.find(self.filePathForDraw, self.pixmap):
        #     self.pixmap = QPixmap(self.filePathForDraw)
        #     QPixmapCache.insert(self.filePathForDraw, self.pixmap)
        #
        # # self.pixmap = QPixmap(self.filePathForDraw)

        # self.pixmap = pixmap
        # self.pixmap = QPixmap()
        # print(QPixmapCache.cacheLimit())
        # self.pixmap = QPixmapCache.find(self.filePathForDraw, self.pixmap)
        self.pixmap = QPixmapCache.find(self.filePathForDraw)
        if not self.pixmap:
            # print("asdasd")
            self.pixmap = QPixmap(self.filePathForDraw)
            QPixmapCache.insert(self.filePathForDraw, self.pixmap)

        # self.pixmap = QPixmap(self.filePathForDraw)

        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable)

        self.imageOpacity = 1.0
        self.isMirrorX = False
        self.isMirrorY = False

        # self.ItemClipsToShape()
        # self.opaqueArea()

        self._isCropping = False
        self.crop_first_point = QPointF()
        self.cropRectF = QRectF()

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return Image.Type

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
                      "imageOpacity": self.imageOpacity,
                      "yaziHiza": int(self.painterTextOption.alignment()),
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "isMirrorX": self.isMirrorX,
                      "isMirrorY": self.isMirrorY,
                      "command": self._command,
                      }
        return properties

    # ---------------------------------------------------------------------
    def mirror(self, x, y):
        if x:
            self.isMirrorX = not self.isMirrorX
        if y:
            self.isMirrorY = not self.isMirrorY
        self.reload_image_after_scale()

    # ---------------------------------------------------------------------
    def flipHorizontal(self, mposx):
        self.mirror(x=True, y=False)
        super(Image, self).flipHorizontal(mposx)

    # ---------------------------------------------------------------------
    def flipVertical(self, mposy):
        self.mirror(x=False, y=True)
        super(Image, self).flipVertical(mposy)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            textItem = Text(event.scenePos(), self.yaziRengi, self.arkaPlanRengi, self.pen(), self.font())
            textItem.set_document_url(self.scene().tempDirPath)
            textItem.textItemFocusedOut.connect(self.scene().is_text_item_empty)
            self.scene().parent().increase_zvalue(textItem)
            # textItem.textItemSelectedChanged.connect(self.textItemSelected)
            # self.addItem(textItem)
            self.scene().undoRedo.undoableAddItem(self.scene().undoStack, description=self.scene().tr("add text"),
                                                  scene=self.scene(),
                                                  item=textItem)
            textItem.setFocus()
            yeniPos = self.mapFromScene(textItem.scenePos())
            self.scene().undoRedo.undoableParent(self.scene().undoStack, self.scene().tr("_parent"), textItem, self,
                                                 yeniPos)

        # super(Image, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        if self._isCropping:
            self.crop_first_point = event.pos()
        super(Image, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        # print("move")
        # if event.button() == Qt.MiddleButton:
        #     print("middle")

        if self._isCropping:
            self.cropRectF = QRectF(self.crop_first_point, event.pos()).normalized()
            self.update(self.cropRectF)
            # self.update(self.cropRectF.adjusted(-10, -10, 10, 10))
            # super(Image, self).mouseMoveEvent(event)

            # print(QRectF(self.crop_first_point, self.crop_release_point))
            return

        if self._resizing:
            # cunku px=1 , py=1 olarak basliyor cizmeye. burda sifirliyoruz eger ilk sahneye ekleme cizimi ise.
            if not self._eskiRectBeforeResize.size() == QSizeF(1, 1):
                px = self._fixedResizePoint.x()
                py = self._fixedResizePoint.y()
            else:
                px = py = 0
            # mx = event.scenePos().x()
            # my = event.scenePos().y()
            mx = event.pos().x()
            my = event.pos().y()
            topLeft = QPointF(min(px, mx), min(py, my))  # top-left corner (x,y)
            bottomRight = QPointF(max(px, mx), max(py, my))  # bottom-right corner (x,y)
            # size = QSizeF(fabs(mx - px), fabs(my - py))
            # rect = QRectF(topLeft, size)

            rect = QRectF(topLeft, bottomRight)

            c = self.rect().center()

            # Alt Key - to resize around center.
            if event.modifiers() & Qt.AltModifier:
                rect.moveCenter(c)

            # ---------------------------------------------------------------------
            #  Ctrl Key - to keep aspect ratio while resizing.
            if event.modifiers() & Qt.ControlModifier:
                tl = self.rect().topLeft()
                tr = self.rect().topRight()
                br = self.rect().bottomRight()
                bl = self.rect().bottomLeft()
                c = self.rect().center()

                yeniSize = rect.size()
                # eskiSize = self.rect().size()
                pixMapOriginalSize = self.pixmap.rect().size()
                # eskiSize.scale(yeniSize, Qt.KeepAspectRatio)
                pixMapOriginalSize.scale(yeniSize.height(), yeniSize.height(), Qt.KeepAspectRatioByExpanding)
                # eskiSize.scale(yeniSize.height(), yeniSize.height(), Qt.KeepAspectRatio)

                # if not eskiSize.isNull():
                if not pixMapOriginalSize.isEmpty():
                    self.yedekSize = QSizeF(pixMapOriginalSize)

                else:
                    pixMapOriginalSize = QSizeF(self.yedekSize)

                rect.setSize(QSizeF(pixMapOriginalSize))
                h = rect.height()
                w = rect.width()

                if self._resizingFrom == 1:
                    rect.moveTopLeft(QPointF(br.x() - w, br.y() - h))

                if self._resizingFrom == 2:
                    rect.moveTopRight(QPointF(bl.x() + w, bl.y() - h))

                if self._resizingFrom == 3:
                    rect.moveBottomRight(QPointF(tl.x() + w, tl.y() + h))

                elif self._resizingFrom == 4:
                    rect.moveBottomLeft(QPointF(tr.x() - w, tr.y() + h))

                # Alt Key - to resize around center
                if event.modifiers() & Qt.AltModifier:
                    rect.moveCenter(c)

            # ---------------------------------------------------------------------
            # Shift Key - to make square (equals width and height)
            if event.modifiers() & Qt.ShiftModifier:
                height = my - py
                if self._resizingFrom == 1:
                    rect.setCoords(px + height, py + height, px, py)
                    rect = rect.normalized()

                elif self._resizingFrom == 2:
                    rect.setCoords(px, py + height, px - height, py)
                    rect = rect.normalized()

                elif self._resizingFrom == 3:
                    rect.setCoords(px, py, px + height, py + height)
                    rect = rect.normalized()

                elif self._resizingFrom == 4:
                    rect.setCoords(px - height, py, px, py + height)
                    rect = rect.normalized()

                # Alt Key - to resize around center
                if event.modifiers() & Qt.AltModifier:
                    rect.moveCenter(c)

            self.setRect(self.mapRectFromItem(self, rect))  # mouse release eventten gonderiyoruz undoya
            self.update_resize_handles()
            self.scene().parent().change_transform_box_values(self)
            # self.setPos(x, y)
            # self.update_painter_text_rect()

        # event.accept()
        else:
            super(Image, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def reload_image_after_scale(self):
        # self.setTransformOriginPoint(self.boundingRect().center())
        if not os.path.isfile(self.filePathForSave):
            self.filePathForDraw = ':icons/warning.png'
        else:
            self.filePathForDraw = self.filePathForSave

        pixmap = QPixmapCache.find(self.filePathForDraw)
        if not pixmap:
            pixmap = QPixmap(self.filePathForDraw)
            QPixmapCache.insert(self.filePathForDraw, pixmap)

        self.pixmap = pixmap.scaled(self.rect().size().toSize(), Qt.KeepAspectRatio)

        if self.isMirrorX:
            self.pixmap = self.pixmap.transformed(QTransform().scale(-1, 1))
        if self.isMirrorY:
            self.pixmap = self.pixmap.transformed(QTransform().scale(1, -1))

    # ---------------------------------------------------------------------
    def finish_crop(self):
        rectf = self.cropRectF
        # croppedPixmap = self.pixmap.copy(rect)
        # secim disari tasarsa
        rectf = rectf.intersected(self._rect)
        if not rectf.isEmpty():
            srectf = self.mapRectToScene(rectf)
            pixmap = QPixmap(srectf.size().toSize())
            # son bir update, yoksa bazen crop rect cizgisi kaliyor render icinde
            self.update(rectf)
            painter = QPainter()

            if not painter.begin(pixmap):
                # print("hata")
                self._isCropping = False
                self.cropRectF = QRectF()
                return

            painter.setRenderHint(QPainter.Antialiasing)
            self.scene().render(painter, QRectF(), srectf)

            painter.end()

            # image = QImage(self.pixmap.copy(rect))
            fileName = os.path.splitext(os.path.basename(self.filePathForSave))[0]
            imageSavePath = self.scene().get_unique_path_for_embeded_image("cropped_{}.jpg".format(fileName))
            pixmap.save(imageSavePath)

            pos = self.scenePos()

            pos.setX(pos.x() + 5)
            pos.setY(pos.y() + 5)

            imageItem = Image(imageSavePath, pos, rectf, self.yaziRengi, self.arkaPlanRengi,
                              self._pen, self.font(), isEmbeded=True)

            self.scene().parent().increase_zvalue(imageItem)
            self.scene().undoRedo.undoableAddItem(self.scene().undoStack, "add new cropped image", self.scene(),
                                                  imageItem)
            imageItem.reload_image_after_scale()
            self.scene().unite_with_scene_rect(imageItem.sceneBoundingRect())
            self.scene().parent().setCursor(Qt.ArrowCursor)

        self._isCropping = False
        self.cropRectF = QRectF()
        self.scene().parent().setCursor(Qt.ArrowCursor)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if self._isCropping:
            self.finish_crop()

        super(Image, self).mouseReleaseEvent(event)

        self.reload_image_after_scale()

    # ---------------------------------------------------------------------
    def hoverEnterEvent(self, event):
        # event propagationdan dolayi bos da olsa burda implement etmek lazim
        # mousePress,release,move,doubleclick de bu mantıkta...
        # baska yerden baslayip mousepress ile , mousemove baska, mouseReleas baska widgetta gibi
        # icinden cikilmaz durumlara sebep olabiliyor.
        # ayrica override edince accept() de edilmis oluyor mouseeventler
        super(Image, self).hoverEnterEvent(event)

    # ---------------------------------------------------------------------
    def hoverMoveEvent(self, event):
        # self.sagUstKare.hide()

        # cursor = self.scene().parent().cursor()
        if self._isCropping:
            self.scene().parent().setCursor(Qt.CrossCursor, gecici_mi=True)
        else:
            super(Image, self).hoverMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverLeaveEvent(self, event):
        if self._isCropping:
            self.finish_crop()
        super(Image, self).hoverLeaveEvent(event)

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):
        # if change == self.ItemPositionChange:
        # if change == self.ItemSelectedChange:
        # if change == self.ItemSelectedHasChanged:
        if change == self.ItemSelectedChange:
            if value:
                self.scene().parent().item_selected(self)
            else:  # yani deselected
                self.scene().parent().item_deselected(self)

        # return QGraphicsRectItem.itemChange(self, change, value)
        return value

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):
        # factor = 1.41 ** (event.delta() / 240.0)
        # self.scale(factor, factor)

        toplam = int(event.modifiers())

        # ctrl = int(Qt.ControlModifier)
        shift = int(Qt.ShiftModifier)
        alt = int(Qt.AltModifier)

        ctrlShift = int(Qt.ControlModifier) + int(Qt.ShiftModifier)
        ctrlAlt = int(Qt.ControlModifier) + int(Qt.AltModifier)
        altShift = int(Qt.AltModifier) + int(Qt.ShiftModifier)
        ctrlAltShift = int(Qt.ControlModifier) + int(Qt.AltModifier) + int(Qt.ShiftModifier)

        # if event.modifiers() & Qt.ControlModifier:
        if toplam == ctrlShift:
            self.scaleItem(event.delta())

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            self.rotateItem(event.delta())

        # elif event.modifiers() & Qt.AltModifier:
        elif toplam == alt:
            # self.changeImageAlpha(event.delta())
            self.changeBackgroundColorAlpha(event.delta())

        elif toplam == ctrlAlt:
            # self.changeLineColorAlpha(event.delta())
            self.changeTextColorAlpha(event.delta())

        elif toplam == ctrlAltShift:
            self.changeFontSize(event.delta())

        elif toplam == altShift:
            # self.changeTextBackgroundColorAlpha(event.delta())
            # self.changeLineColorAlpha(event.delta())
            self.changeImageItemTextBackgroundColorAlpha(event.delta())

        # elif toplam == ctrlAltShift:
        #     self.scaleItemByResizing(event.delta())

        else:
            super(Image, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def changeImageItemTextBackgroundColorAlpha(self, delta):

        col = shared.calculate_alpha(delta, QColor(self.arkaPlanRengi))

        if self.childItems():
            self.scene().undoStack.beginMacro("change image items' text background alpha")
            self.scene().undoRedo.undoableSetItemBackgroundColorAlpha(self.scene().undoStack,
                                                                      "_change image item's background alpha", self,
                                                                      col)
            for c in self.childItems():
                c.changeImageItemTextBackgroundColorAlpha(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetItemBackgroundColorAlpha(self.scene().undoStack,
                                                                      "change image item's background alpha", self, col)

    # ---------------------------------------------------------------------
    def changeBackgroundColorAlpha(self, delta):
        # self.changeImageAlpha(delta)
        if self.childItems():
            self.scene().undoStack.beginMacro("change items' background alpha")
            self.changeImageOpacity(delta)
            for c in self.childItems():
                c.changeBackgroundColorAlpha(delta)
            self.scene().undoStack.endMacro()
        else:
            self.changeImageOpacity(delta)

    # ---------------------------------------------------------------------
    def changeImageOpacity(self, delta):
        if delta > 0:
            if self.imageOpacity + 0.05 < 1:
                self.imageOpacity += 0.05
            else:
                self.imageOpacity = 1
        else:
            if self.imageOpacity - 0.05 > 0:
                self.imageOpacity -= 0.05
            else:
                self.imageOpacity = 0

        self.update()

        # self.pixmap.setAlphaChannel()

        # self.setBrush(self.arkaPlanRengi)
        # self.update()
        self.scene().undoRedo.undoableSetImageOpacity(self.scene().undoStack, "change image opacity", self,
                                                      self.imageOpacity)

    # ---------------------------------------------------------------------
    def changeFontSize(self, delta):

        # font = self.font()
        size = self.fontPointSize()

        if delta > 0:
            # font.setPointSize(size + 1)
            size += 1

        else:
            if size > 10:
                # font.setPointSize(size - 1)
                size -= 1
            else:
                # undolari biriktermesin diye donuyoruz,
                # yoksa zaten ayni size de yeni bir undolu size komutu veriyor.
                return

        # self.setFont(font)
        if self.childItems():
            self.scene().undoStack.beginMacro("change text")
            self.scene().undoRedo.undoableSetFontSize(self.scene().undoStack, "change text size", self, size)
            for c in self.childItems():
                c.changeFontSize(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetFontSize(self.scene().undoStack, "change text size", self, size)

    # ---------------------------------------------------------------------
    def update_painter_text_rect(self):
        # dummy method
        # basede var, ordaki hesaplamalari yapmasin
        pass

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):

        painter.setClipRect(option.exposedRect)

        painter.setBrush(Qt.NoBrush)
        # rect = self.boundingRect().toRect()
        rect = self._rect.toRect()
        painter.setOpacity(self.imageOpacity)
        painter.drawPixmap(rect, self.pixmap)
        painter.setOpacity(1)

        if option.state & QStyle.State_Selected or self.cosmeticSelect:

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
        if self._isCropping:
            # painter.setBrush(Qt.green)
            painter.setPen(self.yaziRengi)
            # painter.setOpacity(.35)
            painter.drawRect(self.cropRectF)

        # # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self.rect(), "{0:.2f},  {1:.2f} pos \n{2:.2f},  {3:.2f} spos".format(p.x(), p.y(), s.x(), s.y()))
        # # # t = self.transformOriginPoint()
        # # # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self.rect().topLeft())
        # painter.drawText(self.rect().x(), self.rect().y(), "{0:.2f}  {1:.2f} map".format(mapped.x(), mapped.y()))
        # painter.drawEllipse(self.scenePos(), 10, 10)
        # painter.setPen(Qt.blue)
        # painter.drawEllipse(self.mapFromScene(self.pos()), 10, 10)
        # r = self.textItem.boundingRect()
        # r = self.mapRectFromItem(self.textItem, r)
        # painter.drawRect(r)
        # painter.drawText(self.rect().center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # painter.setPen(QPen(Qt.red,17))
        # painter.drawPoint(self.rect().center())
        # painter.setPen(QPen(Qt.green,12))
        # painter.drawPoint(self.mapFromScene(self.sceneBoundingRect().center()))
        # painter.setPen(QPen(Qt.blue,8))
        # painter.drawPoint(self.sceneBoundingRect().center())
        # painter.drawRect(self.sceneBoundingRect())
        # # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, resim_kopyalaniyor_mu):
        # resim_adres= f'<img src="{item.filePathForSave}" style="object-fit: fill;"></img>'
        resim_adi = os.path.basename(self.filePathForSave)
        resim_adres = self.filePathForSave
        if not html_klasor_kayit_adres:  # def dosyasi icine kaydediliyor
            if self.isEmbeded:
                resim_adres = os.path.join("images", resim_adi)
        else:  # dosya html olarak baska bir yere kaydediliyor
            # kopyalanmazsa da, zaten embed olmayan resim normal hddeki adresten yuklenecektir.
            if resim_kopyalaniyor_mu:
                # iptal: if not self.isEmbeded:  # embed ise zaten tmp klasorden hedef klasore baska metodta kopylanıyor hepsi.
                # embed veya degil, yukarda bahsettigi gibi resim kopyalansa da adresi de guncellemek lazim.
                resim_adres = os.path.join(html_klasor_kayit_adres, "images", resim_adi)

        img_str = f'<img src="{resim_adres}" style="width:100%; height:100%;"></img>'

        w = self._rect.width() * self.scale()
        h = self._rect.height() * self.scale()

        c = self.sceneBoundingRect().center()

        xr = c.x() - w / 2
        yr = c.y() - h / 2
        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = xr - xs
        y = yr - ys

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
                     color:rgba{renk_yazi};
                     font-size:{self.fontPointSize()}pt; 
                     font-family:{self.font().family()};
                     {bicimler1}
                     {bicimler2}
                     position:absolute;
                     z-index:{int(self.zValue() * 10) if self.zValue() else 0};
                     width:{self._rect.width() * self.scale()}px;
                     height:{self._rect.height() * self.scale()}px;
                     top:{y}px;
                     left:{x}px;
                     opacity:{self.imageOpacity};
                     transform-box: fill-box;
                     transform-origin: center;
                     transform: rotate({self.rotation()}deg);
                     " id="{self._kim}">{img_str}</div>\n"""

        # /*background-image:url('{resim_adres}');*/
        return div_str
