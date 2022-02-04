# -*- coding: utf-8 -*-


__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '3/28/16'

# from math import fabs
import uuid
from PySide6.QtCore import Qt, Signal, QSizeF, QRectF, QPointF, Slot, QUrl
from PySide6.QtGui import QBrush, QPen, QColor, QPainterPath, QPainterPathStroker, QTextBlockFormat
from PySide6.QtWidgets import QGraphicsTextItem, QStyle
from canta import shared


########################################################################
class Text(QGraphicsTextItem):
    Type = shared.TEXT_ITEM_TYPE

    # textItemFocusedOut = Signal(QGraphicsTextItem)
    textItemFocusedOut = Signal(object)

    # textItemSelectedChanged = Signal(QGraphicsTextItem)

    # ---------------------------------------------------------------------
    def __init__(self, cursorPos, yaziRengi, arkaPlanRengi, pen, font, rect=None, text=None, parent=None):
        super(Text, self).__init__(text, parent)

        self._kim = uuid.uuid4().hex

        self.doc = self.document()
        # self.doc.cursorPositionChanged.connect(self.doc_layout_changed)
        self.docLayout = self.doc.documentLayout()
        # self.docLayout.documentSizeChanged.connect(self.doc_layout_changed)

        # self.doc.setUndoRedoEnabled(True)

        self.setFont(font)

        self.isTextOverflowed = False
        self._resizing = False

        if not rect:
            # self._rect = QRectF()
            self._rect = super(Text, self).boundingRect()
            # self._rect = QRectF(QPointF(0,0), self.doc.size())
            # self._rect = self.boundingRect()
        else:
            # rect.moveTo(0, 0)  # gerek yok cunku zaten 0,0 liyoruz scene den gondeririken.
            self._rect = rect
            self.setTextWidth(rect.size().width())

        self.docLayout.documentSizeChanged.connect(self.doc_layout_changed)

        # self.setPos(cursorPos + QPointF(1, 1))
        self.setPos(cursorPos)

        self._eskiRectBeforeResize = None
        self._eskiPosBeforeResize = None

        self.secili_nesne_kalem_kalinligi = 0
        self.handleSize = 10
        self.resizeHandleSize = QSizeF(self.handleSize, self.handleSize)
        self.create_resize_handles()

        # self.setCacheMode(Text.DeviceCoordinateCache)
        # self.setCacheMode(Text.ItemCoordinateCache)
        self.setCacheMode(Text.NoCache)
        self.setFlags(self.ItemIsSelectable |
                      self.ItemIsMovable |
                      self.ItemIsFocusable)

        # self.setTextInteractionFlags(Qt.TextEditable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.cursorPos = cursorPos

        self.hiza = Qt.AlignLeft

        # fmt = QTextBlockFormat()
        # fmt.setAlignment(Qt.AlignCenter)
        cursor = self.textCursor()
        cursor.select(cursor.Document)
        # cursor.mergeBlockFormat(fmt)
        # cursor.clearSelection()
        self.setTextCursor(cursor)

        self._brush = QBrush()
        # we dont use QPen in this text item.
        # self.cizgiKalinligi = 0
        # self.cizgiTipi = Qt.SolidLine
        # self.cizgiUcuTipi = Qt.RoundCap
        # self.cizgiBirlesimTipi = Qt.RoundJoin

        self.activeItemLineColor = shared.activeItemLineColor
        # self.setDefaultTextColor(cizgiRengi)
        self._pen = pen
        # self.cizgiRengi = QColor(Qt.black)
        self.cizgiRengi = pen.color()  # TODO: hemen asagidaki methodta yine set ediyor
        self.setCizgiRengi(self.cizgiRengi)  # also sets defaultTextColor
        self.yaziRengi = yaziRengi
        self.setYaziRengi(yaziRengi)
        self.setArkaPlanRengi(arkaPlanRengi)  # also sets self._brush

        self.cosmeticSelect = False
        self.isActiveItem = False
        self.isFrozen = False
        self._isPinned = False
        self._command = {}

        self.isPlainText = True
        self.oklar_dxdy_nokta = {}

    # ---------------------------------------------------------------------
    def ok_ekle(self, ok, scenepPos, okunHangiNoktasi):

        # self.oklar_dxdy_nokta.append((ok, self.mapFromScene(scenePos)))
        sceneCenter = self.sceneCenter()
        dx = sceneCenter.x() - scenepPos.x()
        dy = sceneCenter.y() - scenepPos.y()

        # self.oklar_dxdy_nokta[ok._kim] = (dx, dy, nokta)
        self.oklar_dxdy_nokta[ok] = (dx, dy, okunHangiNoktasi)

        ok.baglanmis_nesneler[self._kim] = okunHangiNoktasi

    # ---------------------------------------------------------------------
    def ok_sil(self, ok):
        del self.oklar_dxdy_nokta[ok]
        del ok.baglanmis_nesneler[self._kim]

    # ---------------------------------------------------------------------
    def ok_guncelle(self):
        if self.oklar_dxdy_nokta:
            sceneCenter = self.sceneCenter()
            scx = sceneCenter.x()
            scy = sceneCenter.y()
            for ok, dxdy_nokta in self.oklar_dxdy_nokta.items():
                if dxdy_nokta[2] == 1:
                    ok.temp_prepend(QPointF(scx - dxdy_nokta[0], scy - dxdy_nokta[1]))
                elif dxdy_nokta[2] == 2:
                    ok.temp_append(QPointF(scx - dxdy_nokta[0], scy - dxdy_nokta[1]))

    # ---------------------------------------------------------------------
    @property
    def isPinned(self):
        return self._isPinned

    # ---------------------------------------------------------------------
    @isPinned.setter
    def isPinned(self, value):
        if value:
            self.setFlags(self.ItemIsSelectable
                          # | self.ItemIsMovable
                          #  | item.ItemIsFocusable
                          )

        else:
            self.setFlags(self.ItemIsSelectable
                          | self.ItemIsMovable
                          | self.ItemIsFocusable)
        self._isPinned = value

    # ---------------------------------------------------------------------
    def set_document_url(self, url):

        # # ifdef Q_WS_WIN
        # document()->setMetaInformation(QTextDocument::DocumentUrl, imagePath + "/" );
        # # else
        # document()->setMetaInformation(QTextDocument::DocumentUrl, "file:" + imagePath + "/");
        # # endif

        # self.doc.setMetaInformation(self.doc.DocumentUrl, "file:{}/images/".format(url))

        # http://doc.qt.io/qt-5/qtextdocument.html#baseUrl-prop

        # TODO: bu aslinda boyle degil, url sonda / ile gelmiyor
        # url already comes with a "/" suffix so we use double slash "file://{url}"
        self.doc.setBaseUrl(QUrl("file://{}/images-html/".format(url)))
        # self.doc.setBaseUrl(QUrl(url))
        # print(self.doc.metaInformation(self.doc.DocumentUrl))

    # ---------------------------------------------------------------------
    def get_document_url(self):
        return self.doc.baseUrl()

    # ---------------------------------------------------------------------
    @Slot(QSizeF)
    def doc_layout_changed(self, size):
        # self._rect.setSize(self.doc.size())
        if size.width() > self._rect.size().width() or size.height() > self._rect.size().height():
            self._rect.setSize(size)

        self.update_resize_handles()

    # ---------------------------------------------------------------------
    def create_resize_handles(self):
        self.topLeftHandle = QRectF(self._rect.topLeft(), self.resizeHandleSize)
        self.topRightHandle = QRectF(self._rect.topRight(), self.resizeHandleSize)
        self.bottomRightHandle = QRectF(self._rect.bottomRight(), self.resizeHandleSize)
        self.bottomLeftHandle = QRectF(self._rect.bottomLeft(), self.resizeHandleSize)

        # initial move
        self.topRightHandle.moveTopRight(self._rect.topRight())
        self.bottomRightHandle.moveBottomRight(self._rect.bottomRight())
        self.bottomLeftHandle.moveBottomLeft(self._rect.bottomLeft())

    # ---------------------------------------------------------------------
    def update_resize_handles(self, force=False):
        self.prepareGeometryChange()

        # for future ref, (if we enable ingroup or inparent scaling)
        # a = 1
        # if self.parentItem():
        #     a = self.parentItem().scale()
        # scale = 1 / self.scale() / a

        # we need force parameter  because of possible undo of add item. then , if user redos item.scale() will be 1
        # and handles wont resize, this is a problem if item was scaled in the next redos before first undo.
        # self.handleSize = self.handleSize / self.scene().views()[0]
        # print(self.handleSize)
        if self.scale() != 1 or force:
            hsize = self.handleSize
            # hsize = hsize / self.scale()
            # hsize = hsize / self.scale() * self.scene().views()[0].transform().scale()

            # TODO: buna tamamen bi bakmak lazim.
            # bu if kontrolu konup alt satir tablandi if icine,
            # kaydedilmis dosya acilirken, daha sahnesi olusmadigindan, (daha dosya acilmadigi icin.)
            # self.scene().views()[0].transform().m11() cagrilamiyor.
            if self.scene():
                hsize = hsize / self.scale() / self.scene().views()[
                    0].transform().m11()  # horz. scale, m22 vertical scale
            else:
                hsize = hsize / self.scale()

            self.resizeHandleSize.scale(hsize, hsize, Qt.KeepAspectRatioByExpanding)

            self.topLeftHandle.setSize(self.resizeHandleSize)
            self.topRightHandle.setSize(self.resizeHandleSize)
            self.bottomRightHandle.setSize(self.resizeHandleSize)
            self.bottomLeftHandle.setSize(self.resizeHandleSize)

        # self.topLeftHandle.moveTopLeft(self._rect.topLeft())
        # self.topRightHandle.moveTopRight(self._rect.topRight())
        # self.bottomRightHandle.moveBottomRight(self._rect.bottomRight())
        # self.bottomLeftHandle.moveBottomLeft(self._rect.bottomLeft())

        self.topLeftHandle.moveTopLeft(self.boundingRect().topLeft())
        self.topRightHandle.moveTopRight(self.boundingRect().topRight())
        self.bottomRightHandle.moveBottomRight(self.boundingRect().bottomRight())
        self.bottomLeftHandle.moveBottomLeft(self.boundingRect().bottomLeft())

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return Text.Type

    # ---------------------------------------------------------------------
    def sceneCenter(self):
        return self.mapToScene(self.boundingRect().center())

    # ---------------------------------------------------------------------
    def sceneWidth(self):
        return self.sceneRight() - self.sceneLeft()

    # ---------------------------------------------------------------------
    def sceneHeight(self):
        return self.sceneBottom() - self.sceneTop()

    # ---------------------------------------------------------------------
    def sceneRight(self):
        return max(self.mapToScene(self.boundingRect().topRight()).x(),
                   self.mapToScene(self.boundingRect().bottomRight()).x())

    # ---------------------------------------------------------------------
    def sceneLeft(self):
        return min(self.mapToScene(self.boundingRect().topLeft()).x(),
                   self.mapToScene(self.boundingRect().bottomLeft()).x())

    # ---------------------------------------------------------------------
    def sceneTop(self):
        return min(self.mapToScene(self.boundingRect().topLeft()).y(),
                   self.mapToScene(self.boundingRect().topRight()).y())

    # ---------------------------------------------------------------------
    def sceneBottom(self):
        return max(self.mapToScene(self.boundingRect().bottomRight()).y(),
                   self.mapToScene(self.boundingRect().bottomLeft()).y())

    # ---------------------------------------------------------------------
    def setSceneLeft(self, left):
        self.setX(left + self.scenePos().x() - self.sceneLeft())

    # ---------------------------------------------------------------------
    def setSceneRight(self, right):
        self.setX(right + self.scenePos().x() - self.sceneRight())

    # ---------------------------------------------------------------------
    def setSceneTop(self, top):
        self.setY(top + self.scenePos().y() - self.sceneTop())

    # ---------------------------------------------------------------------
    def setSceneBottom(self, bottom):
        self.setY(bottom + self.scenePos().y() - self.sceneBottom())

    # ---------------------------------------------------------------------
    def setHorizontalCenter(self, hcenter):
        self.setY(hcenter + self.scenePos().y() - self.sceneCenter().y())

    # ---------------------------------------------------------------------
    def setVerticalCenter(self, vcenter):
        self.setX(vcenter + self.scenePos().x() - self.sceneCenter().x())

    # ---------------------------------------------------------------------
    def _update_scene_rect_recursively(self, items, rect):

        for c in items:
            rect = rect.united(c.sceneBoundingRect())
            if c.type() == shared.GROUP_ITEM_TYPE:
                if c.parentedWithParentOperation:
                    rect = self._update_scene_rect_recursively(c.parentedWithParentOperation, rect)
            else:
                if c.childItems():
                    rect = self._update_scene_rect_recursively(c.childItems(), rect)
        return rect

    # ---------------------------------------------------------------------
    def sceneBoundingRectWithChildren(self):
        # rect = QRectF(self.sceneBoundingRect())
        rect = self.sceneBoundingRect()
        for c in self.childItems():
            rect = rect.united(c.sceneBoundingRect())
            if c.type() == shared.GROUP_ITEM_TYPE:
                if c.parentedWithParentOperation:
                    rect = self._update_scene_rect_recursively(c.parentedWithParentOperation, rect)
            else:
                if c.childItems():
                    rect = self._update_scene_rect_recursively(c.childItems(), rect)
        return rect

    # ---------------------------------------------------------------------
    def flipHorizontal(self, mposx):
        ipos = self.scenePos()
        rc = self.mapToScene(self.boundingRect().center())
        diff = mposx - rc.x()

        ipos.setX(ipos.x() + 2 * diff)
        if self.parentItem():
            # ipos = (ipos - self.parentItem().scenePos())
            ipos = (self.parentItem().mapFromScene(ipos))
        self.setPos(ipos)
        if self.rotation():
            self.rotateWithOffset(360 - self.rotation())

        eskiRot = self.rotation()
        if eskiRot:
            self.rotateWithOffset(0)
        for c in self.childItems():
            c.flipHorizontal(self.sceneCenter().x())
        if eskiRot:
            self.rotateWithOffset(eskiRot)

    # ---------------------------------------------------------------------
    def flipVertical(self, mposy):
        ipos = self.scenePos()
        rc = self.mapToScene(self.boundingRect().center())
        diff = mposy - rc.y()

        ipos.setY(ipos.y() + 2 * diff)
        if self.parentItem():
            # ipos = (ipos - self.parentItem().scenePos())
            ipos = (self.parentItem().mapFromScene(ipos))
        self.setPos(ipos)
        if self.rotation():
            self.rotateWithOffset(360 - self.rotation())

        eskiRot = self.rotation()
        if eskiRot:
            self.rotateWithOffset(0)
        for c in self.childItems():
            c.flipVertical(self.sceneCenter().y())
        if eskiRot:
            self.rotateWithOffset(eskiRot)

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      "kim": self._kim,
                      "rect": self.rect(),
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "scale": self.scale(),
                      "zValue": self.zValue(),
                      "pen": self._pen,
                      "font": self.font(),
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "isPlainText": self.isPlainText,
                      "isPinned": self.isPinned,
                      "isFrozen": self.isFrozen,
                      "command": self._command,
                      }
        if self.isPlainText:
            properties["text"] = self.toPlainText()
        else:
            properties["html"] = self.toHtml()
        return properties

    # ---------------------------------------------------------------------
    def contextMenuEvent(self, event):
        # TODO: bu alttaki iki satir aktif idi, ve de ctrl harici sag tiklayinca
        # (base- text -path -group nesnelerinin contextMenuEventinde var)
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
    def setText(self, text):
        self.setPlainText(text)

    # ---------------------------------------------------------------------
    def text(self):
        return self.toPlainText()

    # ---------------------------------------------------------------------
    def setCommand(self, title, command):
        self._command["title"] = title
        self._command["command"] = command

    # ---------------------------------------------------------------------
    def command(self):
        return self._command

    # ---------------------------------------------------------------------
    def yazi_kutusunu_daralt(self):
        # self._rect.setSize(QSizeF(self.doc.size()))
        r = QRectF(self._rect)
        # r.setSize(QSizeF(self.textWidth(), self.doc.size().height()))
        r.setSize(QSizeF(self.doc.size()))
        self.setRect(r)

    # ---------------------------------------------------------------------
    def setFont(self, font):
        super(Text, self).setFont(font)
        if self.parentItem():
            self.yazi_kutusunu_daralt()

    # ---------------------------------------------------------------------
    def setFontPointSize(self, fontPointSize):
        font = self.font()
        font.setPointSize(fontPointSize)
        self.setFont(font)
        self.update()

    # ---------------------------------------------------------------------
    def fontPointSize(self):
        return self.font().pointSize()

    # ---------------------------------------------------------------------
    def ver_yazi_hizasi(self):
        return self.doc.defaultTextOption().alignment()

    # ---------------------------------------------------------------------
    def kur_yazi_hizasi(self, hiza):
        option = self.doc.defaultTextOption()
        option.setAlignment(hiza)
        self.doc.setDefaultTextOption(option)

    # ---------------------------------------------------------------------
    def ver_karakter_bicimi(self):
        # return self._font.bold | self._font.italic | self._font.under | self._font.strikeout
        font = self.font()
        return {"b": font.bold(),
                "i": font.italic(),
                "u": font.underline(),
                "s": font.strikeOut(),
                "o": font.overline(),
                }

    # ---------------------------------------------------------------------
    def kur_karakter_bicimi(self, sozluk):
        font = self.font()
        font.setBold(sozluk["b"])
        font.setItalic(sozluk["i"])
        font.setUnderline(sozluk["u"])
        font.setStrikeOut(sozluk["s"])
        font.setOverline(sozluk["o"])
        self.setFont(font)
        # self.update()

    # ---------------------------------------------------------------------
    def setPen(self, pen):

        if self._pen == pen:
            return
        self.prepareGeometryChange()
        self._pen = pen
        # self._boundingRect = QRectF()
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

        _selectionLineBgColor = QColor.fromHsv(col.hue(),
                                               0,
                                               20 if col.value() > 127 else 250)

        _activeItemLineColor = QColor(self.activeItemLineColor)
        if col.hue() > 300 or col.hue() < 30:
            _activeItemLineColor.setHsv((col.hue() + 150) % 360,
                                        self.activeItemLineColor.saturation(),
                                        self.activeItemLineColor.value())
        self._pen.setColor(col)
        # self.setDefaultTextColor(col)
        self.cizgiRengi = col

        self.selectionPenBottom = QPen(_selectionLineBgColor,
                                       self.secili_nesne_kalem_kalinligi,
                                       Qt.DashLine,
                                       Qt.RoundCap, Qt.RoundJoin)
        self.selectionPenBottomIfAlsoActiveItem = QPen(_activeItemLineColor,
                                                       self.secili_nesne_kalem_kalinligi,
                                                       Qt.DashLine,
                                                       Qt.RoundCap, Qt.RoundJoin)

        self.update()

    # ---------------------------------------------------------------------
    def setYaziRengi(self, col):

        self.yaziRengi = col
        # self.textPen = QPen(QColor().fromRgb(col.red(), col.green(), col.blue(), col.alpha()))
        self.setDefaultTextColor(col)
        self.update()

    # ---------------------------------------------------------------------
    def setCizgiKalinligi(self, width):
        self._pen.setWidthF(width)
        # self.textPen.setWidthF(width)
        # self.selectionPenBottom.setWidthF(width)
        # self.selectionPenBottomIfAlsoActiveItem.setWidthF(width)
        # self.selectionPenTop.setWidthF(width)

        self.update()

    # ---------------------------------------------------------------------
    def setArkaPlanRengi(self, col):
        self.arkaPlanRengi = col
        self.setBrush(QBrush(col))

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):

        if change == self.ItemSelectedChange:
            if value:
                self.scene().parent().text_item_selected(self)
            else:
                self.scene().parent().item_deselected(self)

        # return QGraphicsRectItem.itemChange(self, change, value)
        return value
        # super(Rect, self).itemChange(change, value)

    # ---------------------------------------------------------------------
    def focusInEvent(self, event):

        if self.scene():
            if self.doc.availableUndoSteps():
                self.scene().parent().log(
                    self.tr("{} undo(s), {} redo(s) available for items' text.").format(self.doc.availableUndoSteps(),
                                                                                        self.doc.availableRedoSteps()),
                    4500,
                    toStatusBarOnly=True)

        super(Text, self).focusInEvent(event)

    # ---------------------------------------------------------------------
    def focusOutEvent(self, event):

        # self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setTextInteractionFlags(Qt.NoTextInteraction)

        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.textItemFocusedOut.emit(self)
        if self.scene():
            self.scene().parent()._statusBar.clearMessage()

        super(Text, self).focusOutEvent(event)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        # if event.modifiers() == Qt.ControlModifier:
        #     self.scene().parent().web_browser_ac(self.text())
        # elif event.modifiers() == Qt.ControlModifier | Qt.ShiftModifier:
        #     self.scene().parent().web_browser_ac("https://www.google.com/search?q=" + self.text())
        if event.modifiers() == Qt.ControlModifier:
            self.yazi_kutusunu_daralt()

        else:
            # if self.textInteractionFlags() == Qt.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.setFocus()
            # self.clearFocus()
        super(Text, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def hoverEnterEvent(self, event):
        # TODO: bu hoverlarda bu kareler yerine mouse icon
        # degisse koselere ykenarlar ayaklastikca
        # TODO: bu saved cursor olmadi tam.
        # if self.isSelected() and not self.isFrozen:
        self.saved_cursor = self.scene().parent().cursor()

        super(Text, self).hoverEnterEvent(event)

    # ---------------------------------------------------------------------
    def hoverMoveEvent(self, event):
        # self.sagUstKare.hide()

        # cursor = self.scene().parent().cursor()

        if self.isSelected() and not self.isFrozen:
            if self.topLeftHandle.contains(event.pos()) or self.bottomRightHandle.contains(event.pos()):
                self.scene().parent().setCursor(Qt.SizeFDiagCursor)
                # self.setCursor(Qt.SizeFDiagCursor)
            elif self.topRightHandle.contains(event.pos()) or self.bottomLeftHandle.contains(event.pos()):
                self.scene().parent().setCursor(Qt.SizeBDiagCursor)
                # self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.scene().parent().setCursor(Qt.ArrowCursor)
                # self.setCursor(self.saved_cursor)

        super(Text, self).hoverMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverLeaveEvent(self, event):
        # self.sagUstKare.hide()
        if self.isSelected() and not self.isFrozen:
            # self.scene().parent().setCursor(Qt.ArrowCursor)
            self.scene().parent().setCursor(self.saved_cursor)

        super(Text, self).hoverLeaveEvent(event)

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):

        toplam = int(event.modifiers())

        # ctrl = int(Qt.ControlModifier)
        shift = int(Qt.ShiftModifier)
        alt = int(Qt.AltModifier)

        ctrlAlt = int(Qt.ControlModifier) + int(Qt.AltModifier)
        ctrlShift = int(Qt.ControlModifier) + int(Qt.ShiftModifier)
        altShift = int(Qt.AltModifier) + int(Qt.ShiftModifier)
        ctrlAltShift = int(Qt.ControlModifier) + int(Qt.AltModifier) + int(Qt.ShiftModifier)

        # if event.modifiers() & Qt.ControlModifier:
        if toplam == ctrlShift:
            if not self.isFrozen:
                self.scaleItem(event.delta())
                # self.scaleItem(event.angleDelta().y())
            else:
                super(Text, self).wheelEvent(event)

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            if not self.isFrozen:
                self.rotateItem(event.delta())
            else:
                super(Text, self).wheelEvent(event)

        # elif event.modifiers() & Qt.AltModifier:
        elif toplam == alt:
            self.changeBackgroundColorAlpha(event.delta())

        elif toplam == ctrlAlt:
            self.changeTextColorAlpha(event.delta())

        elif toplam == ctrlAltShift:
            self.changeFontSize(event.delta())

        elif toplam == altShift:
            # self.changeImageItemTextBackgroundColorAlpha(event.delta())
            self.changeLineColorAlpha(event.delta())

        # elif toplam == ctrlAltShift:
        #     if not self.isFrozen:
        #         self.scaleItemWithFontSize(event.delta())
        #     else:
        #         super(Text, self).wheelEvent(event)
        else:
            super(Text, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def scaleItemWithFontSize(self, delta):
        self.changeFontSize(delta)

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

        self.scene().undoRedo.undoableSetFontSize(self.scene().undoStack, "change text size", self, size)

        # # ---------------------------------------------------------------------
        # if self.childItems():
        #     self.scene().undoStack.beginMacro("change text size")
        #     # self.scene().undoableSetFontSize("change text size", self, size)
        #     for c in self.childItems():
        #         c.changeFontSize(delta)
        #     self.scene().undoStack.endMacro()
        # # ---------------------------------------------------------------------
        # # else:
        # #     self.scene().undoableSetFontSize("change text size", self, size)

    # ---------------------------------------------------------------------
    def scaleItem(self, delta):
        # TODO : size sıfır olmasin kontrolu

        scaleFactor = 1.1
        if delta > 0:
            scaleFactor = self.scale() * scaleFactor
            self.scene().unite_with_scene_rect(self.sceneBoundingRect())

        else:
            scaleFactor = self.scale() / scaleFactor

        self.scene().undoRedo.undoableScale(self.scene().undoStack, "scale", self, scaleFactor)

    # ---------------------------------------------------------------------
    def scaleWithOffset(self, scale):
        cEski = self.sceneCenter()
        self.setScale(scale)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())

    # ---------------------------------------------------------------------
    def setScale(self, scale):
        super(Text, self).setScale(scale)
        self.update_resize_handles()

    # ---------------------------------------------------------------------
    def rotateWithOffset(self, angle):
        cEski = self.sceneCenter()
        self.setRotation(angle)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())

    # ---------------------------------------------------------------------
    def rotateItem(self, delta):

        # self.setTransformOriginPoint(self.boundingRect().center())
        if delta > 0:
            # self.setRotation(self.rotation() + 5)
            self.scene().undoRedo.undoableRotateBaseItem(self.scene().undoStack, "rotate", self, self.rotation() + 5)
        else:
            # self.setRotation(self.rotation() - 5)
            self.scene().undoRedo.undoableRotateBaseItem(self.scene().undoStack, "rotate", self, self.rotation() - 5)
        # self.update()

    # ---------------------------------------------------------------------
    def changeBackgroundColorAlpha(self, delta):

        col = shared.calculate_alpha(delta, QColor(self.arkaPlanRengi))

        # self.setBrush(self.arkaPlanRengi)
        # self.update()
        # self.scene().undoableSetItemBackgroundColorAlpha("Change item's background alpha", self, col)
        if self.childItems():
            self.scene().undoStack.beginMacro("change items' background alpha")
            self.scene().undoRedo.undoableSetItemBackgroundColorAlpha(self.scene().undoStack,
                                                                      "_change item's background alpha",
                                                                      self, col)
            for c in self.childItems():
                c.changeBackgroundColorAlpha(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetItemBackgroundColorAlpha(self.scene().undoStack,
                                                                      "change item's background alpha", self,
                                                                      col)

    # ---------------------------------------------------------------------
    def changeLineColorAlpha(self, delta):

        col = shared.calculate_alpha(delta, self.defaultTextColor())

        # self.setDefaultTextColor(col)
        # self.scene().undoableSetLineOrTextColorAlpha("Change item's text alpha", self, col)
        if self.childItems():
            self.scene().undoStack.beginMacro("change items' line alpha")
            self.scene().undoRedo.undoableSetLineColorAlpha(self.scene().undoStack, "_change item's line alpha", self,
                                                            col)
            for c in self.childItems():
                c.changeLineColorAlpha(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetLineColorAlpha(self.scene().undoStack, "change item's line alpha", self,
                                                            col)

    # ---------------------------------------------------------------------
    def changeTextColorAlpha(self, delta):

        col = shared.calculate_alpha(delta, self.yaziRengi)

        if self.childItems():
            self.scene().undoStack.beginMacro("change items' text alpha")
            self.scene().undoRedo.undoableSetTextColorAlpha(self.scene().undoStack, "_change item's text alpha", self,
                                                            col)
            for c in self.childItems():
                c.changeTextColorAlpha(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetTextColorAlpha(self.scene().undoStack, "change item's text alpha", self,
                                                            col)

    # ---------------------------------------------------------------------
    def changeImageItemTextBackgroundColorAlpha(self, delta):
        # this is a wrapper method, actual undoableSetItemBackgroundColorAlpha method is in IMAGE class.
        if self.childItems():
            startedMacro = False
            for c in self.childItems():
                if c.type() == shared.IMAGE_ITEM_TYPE:
                    if not startedMacro:
                        self.scene().undoStack.beginMacro("change image items' text background alpha")
                        startedMacro = True
                    c.changeImageItemTextBackgroundColorAlpha(delta)
            if startedMacro:
                self.scene().undoStack.endMacro()

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget):

        painter.save()
        # painter.fillRect(option.rect, self.arkaPlanRengi)
        painter.fillRect(option.rect, self.brush())

        if option.state & QStyle.State_Selected or self.cosmeticSelect:
            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
            else:
                selectionPenBottom = self.selectionPenBottom
            painter.setPen(selectionPenBottom)
            painter.drawRect(option.rect)

            ########################################################################
            # !!! simdilik iptal, gorsel fazlalik olusturmakta !!!
            ########################################################################
            # if not self.isPinned and not self.isFrozen and self.isActiveItem:
            #     # painter.setPen(self.handlePen)
            #     painter.drawRect(self.topLeftHandle)
            #     painter.drawRect(self.topRightHandle)
            #     painter.drawRect(self.bottomRightHandle)
            #     painter.drawRect(self.bottomLeftHandle)
            ########################################################################

        if self.isTextOverflowed:
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            painter.drawLine(self._rect.bottomLeft(), self._rect.bottomRight())

        # painter.setPen(Qt.blue)
        # painter.drawRect(self.boundingRect())
        # painter.setPen(Qt.green)
        # painter.drawRect(self.rect())
        painter.restore()

        # option2 = QStyleOptionGraphicsItem(option)
        # option2.state = 0
        # option.state &= ~(QStyle.State_Selected | QStyle.State_HasFocus)
        # option2.exposedRect.setSize(self.document().pageSize())
        # option2.exposedRect.setSize(self.document().documentLayout().documentSize())

        # option.exposedRect = self.boundingRect()
        # option.rect = option.exposedRect.toRect()

        # rect = QRectF(self.rect())
        # rect.moveTo(0, 0)
        # option2.exposedRect = rect

        # TODO bunlar niye koyuldu?
        option.exposedRect = self._rect
        option.rect = self._rect.toRect()

        # painter.setClipRect(option.exposedRect)
        super(Text, self).paint(painter, option, widget)

        # self.doc.drawContents(painter, self.rect())

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):

        self._resizing = False  # we could use "self._resizingFrom = 0" instead, but self._resizing is more explicit.
        self._fixedResizePoint = None
        self._resizingFrom = None
        self._eskiRectBeforeResize = None

        self._eskiPosBeforeResize = self.pos()
        # self._eskiPosBeforeResize = self.scenePos()

        if not self.isFrozen:

            if self.topLeftHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self._rect.bottomRight()
                self._resizingFrom = 1
                self._eskiRectBeforeResize = QRectF(self._rect)
            elif self.topRightHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self._rect.bottomLeft()
                self._resizingFrom = 2
                self._eskiRectBeforeResize = QRectF(self._rect)
            elif self.bottomRightHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self._rect.topLeft()
                self._resizingFrom = 3
                self._eskiRectBeforeResize = QRectF(self._rect)
            elif self.bottomLeftHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self._rect.topRight()
                self._resizingFrom = 4
                self._eskiRectBeforeResize = QRectF(self._rect)

        super(Text, self).mousePressEvent(event)

        # TODO: bu kozmetik amacli, sadece release de olunca gecikmeli seciyormus hissi oluyor
        if self.isSelected() and self.childItems():
            self.scene().select_all_children_recursively(self, cosmeticSelect=True)

        # self.scene().deactivate_item(self)
        # self.scene().activate_item(self)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if self._resizing:
            # sahneye ilk cizim kontrolu,(undoya eklemesin diye)
            # if not self._eskiRectBeforeResize.size() == QSizeF(1, 1):
            #     rect = self.boundingRect()
            #     self.setPos(self.mapToScene(rect.topLeft()))
            #     rect.moveTo(0, 0)
            #     self.scene().undoableResizeBaseItem("resize",
            #                                         self,
            #                                         # yeniRect=self.rect(),
            #                                         yeniRect=rect,
            #                                         eskiRect=self._eskiRectBeforeResize,
            #                                         eskiPos=self._eskiPosBeforeResize)

            # TODO: bu satir eger cizim disari tasarsa, scene recti ona uygun ayarlamak icin
            # fakat eger cizim disari tasarsa evet uyarliyor ama bazen de çizilen itemin geometrisini degistiriyor.
            # o yuzden simdilik iptal.
            # self.scene().unite_with_scene_rect(self.sceneBoundingRect())

            # rect = self.boundingRect()
            rect = self.rect()
            self.setPos(self.mapToScene(rect.topLeft()))
            rect.moveTo(0, 0)
            # self.doc.setTextWidth(rect.width())

            # undo icinde
            # self.update_resize_handles()

            self.scene().undoRedo.undoableResizeBaseItem(self.scene().undoStack,
                                                         "resize",
                                                         self,
                                                         # yeniRect=self.rect(),
                                                         yeniRect=rect,
                                                         eskiRect=self._eskiRectBeforeResize,
                                                         eskiPos=self._eskiPosBeforeResize)

            # print(self.mapRectToScene(self._eskiRectBeforeResize))
            # self.scene().update(self.mapRectToScene(self._eskiRectBeforeResize))
            # self.scene().views()[0].updateScene([self.mapRectToScene(self._eskiRectBeforeResize)])
            self._resizing = False
            self.scene().unite_with_scene_rect(self.sceneBoundingRect())

        super(Text, self).mouseReleaseEvent(event)

        if self.childItems():
            if self.isSelected():
                self.scene().select_all_children_recursively(self, cosmeticSelect=False, topmostParent=True)
            else:
                self.scene().select_all_children_recursively(self, cosmeticSelect=False)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        if self._resizing:

            px = self._fixedResizePoint.x()
            py = self._fixedResizePoint.y()

            # mx = event.scenePos().x()
            # my = event.scenePos().y()
            mx = event.pos().x()
            my = event.pos().y()
            topLeft = QPointF(min(px, mx), min(py, my))  # top-left corner (x,y)
            bottomRight = QPointF(max(px, mx), max(py, my))  # bottom-right corner (x,y)
            # size = QSizeF(fabs(mx - px), fabs(my - py))
            # rect = QRectF(topLeft, size)
            # rect = QRectF(QPointF(0, 0), size)

            rect = QRectF(topLeft, bottomRight)
            # rect = rect.normalized()

            # self.setPos(self.mapToScene(topLeft))
            # self.setPos(self.mapFromScene(topLeft))
            # eger bu move to 0,0 koymazsak o zaman normal resize ediyoruz ama
            # sol taraftan resize edersek release edince text tepki veriyor.
            rect.moveTo(0, 0)
            self.setRect(rect)
            # self.setPos(self.mapToScene(rect.topLeft()))
            self.scene().parent().change_transform_box_values(self)

        # event.accept()
        else:
            super(Text, self).mouseMoveEvent(event)

        # super(BaseItem, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def setRect(self, rect):
        if self._rect == rect:
            return

        self.prepareGeometryChange()
        self._rect = rect
        # TODO: burda direkt self.settextwidth niye demedik ki
        self.doc.setTextWidth(rect.width())
        # self.doc.setPageSize(rect.size())
        self.update_resize_handles()
        # self.adjustSize()
        # self.scene().parent().change_transform_box_values(self)
        # self._boundingRect = QRectF()

        if self.doc.size().height() > rect.size().height():
            self.isTextOverflowed = True
        else:
            self.isTextOverflowed = False
        self.update()

    # ---------------------------------------------------------------------
    def rect(self):
        return self._rect

    # ---------------------------------------------------------------------
    def shape(self):

        # if (!dd->control)
        # return QPainterPath();
        #
        # QPainterPath path;
        # path.addRect(dd->boundingRect);
        # return path;

        # path = QPainterPath()
        # # path.addRect(self._rect)
        # if self.rect().isEmpty():
        #     return super(Text, self).shape()
        # else:
        #     path.addRect(self._rect)
        # # return self.qt_graphicsItem_shapeFromPath(path, self._pen)
        #     return path

        path = QPainterPath()
        path.addRect(self._rect)
        return path

    # ---------------------------------------------------------------------
    def boundingRectttt(self):
        if self.rect().isEmpty():
            print("empty")
            return super(Text, self).boundingRect()
            # self.setRect(super(Text, self).boundingRect())
        return self.rect()

    # ---------------------------------------------------------------------
    def boundingRecttt(self):
        bRect = super(Text, self).boundingRect()
        if bRect.width() > self._rect.width():
            self._rect.setSize(QSizeF(bRect.width(), self._rect.height()))
        if bRect.height() > self._rect.height():
            self._rect.setSize(QSizeF(self._rect.width(), bRect.height()))
        return self._rect

    # ---------------------------------------------------------------------
    def boundingRect(self):
        return self._rect

    # void QGraphicsTextItemPrivate::_q_updateBoundingRect(const QSizeF &size)
    # {
    #     if (!control) return; // can't happen
    #     const QSizeF pageSize = control->document()->pageSize();
    #     // paged items have a constant (page) size
    #     if (size == boundingRect.size() || pageSize.height() != -1)
    #         return;
    #     qq->prepareGeometryChange();
    #     boundingRect.setSize(size);
    #     qq->update();
    # }

    # # ---------------------------------------------------------------------
    # def qt_graphicsItem_shapeFromPath(self, path, pen):
    #     # We unfortunately need this hack as QPainterPathStroker will set a width of 1.0
    #     # if we pass a value of 0.0 to QPainterPathStroker.setWidth()
    #     penWidthZero = 0.00000001
    #     if path == QPainterPath():
    #         return path
    #     ps = QPainterPathStroker()
    #     ps.setCapStyle(pen.capStyle())
    #
    #     if pen.widthF() <= 0:
    #         ps.setWidth(penWidthZero)
    #     else:
    #         ps.setWidth(pen.widthF())
    #     ps.setJoinStyle(pen.joinStyle())
    #     ps.setMiterLimit(pen.miterLimit())
    #     p = ps.createStroke(path)  # return type: QPainterPath
    #     p.addPath(path)
    #     return p

    # ---------------------------------------------------------------------
    #         inline QPointF controlOffset() const
    #         {
    #         return QPointF(0., pageNumber * control->document()->pageSize().height());}

    # ---------------------------------------------------------------------
    #     void
    #     QGraphicsTextItem::paint(QPainter * painter, const
    #     QStyleOptionGraphicsItem * option,
    #     QWidget * widget)
    #
    # {
    #     Q_UNUSED(widget);
    # if (dd->control) {
    # painter->save();
    # QRectF r = option->exposedRect;
    # painter->translate(-dd->controlOffset());
    # r.translate(dd->controlOffset());
    #
    # QTextDocument * doc = dd->control->document();
    # QTextDocumentLayout * layout = qobject_cast < QTextDocumentLayout * > (doc->documentLayout());
    #
    # // the layout might need to expand the root frame to
    # // the viewport if NoWrap is set
    # if (layout)
    # layout->setViewport(dd->boundingRect);
    #
    # dd->control->drawContents(painter, r);
    #
    # if (layout)
    # layout->setViewport(QRect());
    #
    # painter->restore();
    # }
    #
    # if (option->state & (QStyle::
    #     State_Selected | QStyle::State_HasFocus))
    # qt_graphicsItem_highlightSelected(this, painter, option);
    # }
    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.clearFocus()
            # bu asagidaki if var cunku text item bos ise
            # birden fazla defa selectionqueue da remove etmeye calisabiliyor
            # veya item sahneden silindiginden item.scene() none donuyor gibi sebeplerden dolayi.
            # self.childItems() kontrolu de, yazi bir baska nesnenin parenti iken silinmis olabilir diye.
            if self.toPlainText() or self.childItems():
                self.setSelected(False)

        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.clearFocus()
                if self.toPlainText() or self.childItems():
                    self.setSelected(False)

        if event.modifiers() & Qt.ShiftModifier:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.clearFocus()
                if self.toPlainText() or self.childItems():
                    self.setSelected(False)
                    self.scene().create_empty_text_object_with_double_click(
                        QPointF(self.sceneLeft(), self.sceneBottom() + 10))

        super(Text, self).keyPressEvent(event)
