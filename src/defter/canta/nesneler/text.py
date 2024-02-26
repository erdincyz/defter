# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtCore import Qt, Signal, QSizeF, QRectF, QPointF, Slot, QUrl
from PySide6.QtGui import QBrush, QPen, QColor, QPainterPath, QFontMetricsF, QTextCursor
from PySide6.QtWidgets import QGraphicsTextItem, QStyle
from .. import shared


########################################################################
class Text(QGraphicsTextItem):
    Type = shared.TEXT_ITEM_TYPE

    # textItemFocusedOut = Signal(QGraphicsTextItem)
    textItemFocusedOut = Signal(object)

    # textItemSelectedChanged = Signal(QGraphicsTextItem)

    # ---------------------------------------------------------------------
    def __init__(self, cursorPos, yaziRengi, arkaPlanRengi, pen, font, rect=None, text=None, parent=None):
        super(Text, self).__init__(text, parent)

        self._kim = shared.kim(kac_basamak=16)

        self.setAcceptHoverEvents(True)

        self.doc = self.document()
        # self.doc.cursorPositionChanged.connect(self.doc_layout_changed)
        self.docLayout = self.doc.documentLayout()
        # self.docLayout.documentSizeChanged.connect(self.doc_layout_changed)

        # self.doc.setUndoRedoEnabled(True)

        self.doc.undoCommandAdded.connect(self.act_undo_eklendi)

        self.setFont(font)
        self.secili_nesne_kalem_kalinligi = 0

        self.isTextOverflowed = False
        self._resizing = False

        self.handleSize = 10
        self.resizeHandleSize = QSizeF(self.handleSize, self.handleSize)
        self.boundingRectTasmaDegeri = self.handleSize / 2

        if not rect:
            # self._rect = QRectF()
            self._rect = super(Text, self).boundingRect()
            # self._rect = QRectF(QPointF(0,0), self.doc.size())
            # self._rect = self.boundingRect()
        else:
            # rect.moveTo(0, 0)  # gerek yok cunku zaten 0,0 liyoruz scene den gondeririken.
            self._rect = rect
            self.setTextWidth(rect.size().width())

        self._boundingRect = self._rect.adjusted(-self.boundingRectTasmaDegeri, -self.boundingRectTasmaDegeri,
                                                 self.boundingRectTasmaDegeri, self.boundingRectTasmaDegeri)

        self.docLayout.documentSizeChanged.connect(self.doc_layout_changed)

        # self.setPos(cursorPos + QPointF(1, 1))
        self.setPos(cursorPos)

        self._eskiRectBeforeResize = None
        self._eskiPosBeforeResize = None

        self.update_resize_handles()

        # self.setCacheMode(Text.DeviceCoordinateCache)
        # self.setCacheMode(Text.ItemCoordinateCache)
        self.setCacheMode(Text.CacheMode.NoCache)
        self.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable)

        # self.setTextInteractionFlags(Qt.TextEditable)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)

        self.cursorPos = cursorPos

        self.hiza = Qt.AlignmentFlag.AlignLeft

        # fmt = QTextBlockFormat()
        # fmt.setAlignment(Qt.AlignCenter)
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
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
        self._isPinned = False
        self.ustGrup = None
        self._command = {}

        self.isPlainText = True
        self.oklar_dxdy_nokta = {}

        # self.zenginYaziBelirteci = QRect(0, 0, 10, 10)

        # self.cursor_eski_anchor = 0
        # self.cursor_eski_pozisyon = 0
        # self.doc.cursorPositionChanged.connect(self.cursor_pos_degisti)

    # # ---------------------------------------------------------------------
    # def cursor_pos_degisti(self, cursor):
    #     self.cursor_eski_pozisyon = cursor.position()
    #     self.cursor_eski_anchor = cursor.anchor()

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return Text.Type

    # ---------------------------------------------------------------------
    @property
    def isPinned(self):
        return self._isPinned

    # ---------------------------------------------------------------------
    @isPinned.setter
    def isPinned(self, value):
        if value:
            self.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable
                          # | QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable
                          #  | QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable
                          )

        else:
            self.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable
                          | QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable
                          | QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable)
        self._isPinned = value

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      "kim": self._kim,
                      "rect": self._rect,
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "zValue": self.zValue(),
                      "pen": self._pen,
                      "font": self.font(),
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "isPlainText": self.isPlainText,
                      "yaziHiza": int(self.doc.defaultTextOption().alignment()),
                      "isPinned": self.isPinned,
                      "command": self._command,
                      }
        if self.isPlainText:
            properties["text"] = self.toPlainText()
        else:
            properties["html"] = self.toHtml()
        return properties

    # ---------------------------------------------------------------------
    @Slot()
    def act_undo_eklendi(self):
        self.scene().undoRedo.undoRedoBaglantisiYaziNesnesiDocuna(self.scene().undoStack,
                                                                  self.scene().tr("change text"),
                                                                  self.doc)

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
                if ok._text:
                    ok.update_painter_text_rect()

    # ---------------------------------------------------------------------
    def varsaEnUsttekiGrubuGetir(self):
        parentItem = self.parentItem()
        while parentItem:
            if parentItem.type() == shared.GROUP_ITEM_TYPE:
                return parentItem
            parentItem = parentItem.parentItem()
        return None

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
        # self.doc.setBaseUrl(QUrl("file://{}/images-html/".format(url)))
        self.doc.setBaseUrl(QUrl("file://{}/".format(url)))
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
            self._boundingRect = self._rect.adjusted(-self.boundingRectTasmaDegeri,
                                                     -self.boundingRectTasmaDegeri,
                                                     self.boundingRectTasmaDegeri,
                                                     self.boundingRectTasmaDegeri)

            self.update_resize_handles()

    # ---------------------------------------------------------------------
    def update_resize_handles(self):
        self.prepareGeometryChange()

        if self.scene():
            resizeHandleSize = self.resizeHandleSize / self.scene().views()[0].transform().m11()
        else:
            resizeHandleSize = self.resizeHandleSize

        # bunlarin yeri onemli degil, QSize(0,0) da olur, asagida yerlerine kaydiriliorlar
        self.topLeftHandle = QRectF(self._rect.topLeft(), resizeHandleSize)
        self.topRightHandle = QRectF(self._rect.topRight(), resizeHandleSize)
        self.bottomRightHandle = QRectF(self._rect.bottomRight(), resizeHandleSize)
        self.bottomLeftHandle = QRectF(self._rect.bottomLeft(), resizeHandleSize)

        # # self.topLeftHandle.moveTopLeft(self._rect.topLeft())
        # self.topRightHandle.moveTopRight(self._rect.topRight())
        # self.bottomRightHandle.moveBottomRight(self._rect.bottomRight())
        # self.bottomLeftHandle.moveBottomLeft(self._rect.bottomLeft())

        self.topLeftHandle.moveCenter(self._rect.topLeft())
        self.topRightHandle.moveCenter(self._rect.topRight())
        self.bottomRightHandle.moveCenter(self._rect.bottomRight())
        self.bottomLeftHandle.moveCenter(self._rect.bottomLeft())

    # ---------------------------------------------------------------------
    def sceneCenter(self):
        if self.parentItem():
            return self.mapToParent(self.boundingRect().center())
        return self.mapToScene(self.boundingRect().center())

    # ---------------------------------------------------------------------
    def sceneWidth(self):
        return self.sceneRight() - self.sceneLeft()

    # ---------------------------------------------------------------------
    def sceneHeight(self):
        return self.sceneBottom() - self.sceneTop()

    # ---------------------------------------------------------------------
    def sceneRight(self):
        return max(self.sceneBoundingRect().topRight().x(),
                   self.sceneBoundingRect().bottomRight().x())

    # ---------------------------------------------------------------------
    def sceneLeft(self):
        return min(self.sceneBoundingRect().topLeft().x(),
                   self.sceneBoundingRect().bottomLeft().x())

    # ---------------------------------------------------------------------
    def sceneTop(self):
        return min(self.sceneBoundingRect().topLeft().y(),
                   self.sceneBoundingRect().topRight().y())

    # ---------------------------------------------------------------------
    def sceneBottom(self):
        return max(self.sceneBoundingRect().bottomRight().y(),
                   self.sceneBoundingRect().bottomLeft().y())

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
    def contextMenuEvent(self, event):
        # TODO: bu alttaki iki satir aktif idi, ve de ctrl harici sag tiklayinca
        # (base- text -path -group nesnelerinin contextMenuEventinde var)
        # mesela birden fazla nesne secili ve de gruplayacagız diyelim sag menu ile
        # ctrl basılı degil ise tikladigimiz secili kaliyor digerleri siliniyordu
        # uygunsuz bir kullanıcı deneyimi, niye yaptık acaba boyleyi hatırlayana kadar kalsın burda :)
        # if not event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        #     self.scene().clearSelection()
        self.setSelected(True)

        # self.scene().parent().item_context_menu(self, event.screenPos())
        self.scene().parent().on_yazi_sag_menu_about_to_show(self)
        self.scene().parent().yaziSagMenu.popup(event.screenPos())

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
    def setFont(self, font, yaziTipiMiDegisti=True):
        if yaziTipiMiDegisti:
            font.setBold(self.font().bold())
            font.setItalic(self.font().italic())
            font.setUnderline(self.font().underline())
            font.setStrikeOut(self.font().strikeOut())
            font.setOverline(self.font().overline())
            # font.setPointSizeF(self.font().pointSizeF())
        super(Text, self).setFont(font)
        if self.parentItem():
            self.yazi_kutusunu_daralt()

    # ---------------------------------------------------------------------
    def setFontPointSizeF(self, fontPointSizeF):
        font = self.font()
        font.setPointSizeF(fontPointSizeF)
        self.setFont(font, yaziTipiMiDegisti=False)
        self.update()

    # ---------------------------------------------------------------------
    def fontPointSizeF(self):
        return self.font().pointSizeF()

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
        self.setFont(font, yaziTipiMiDegisti=False)
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
                                       Qt.PenStyle.DashLine,
                                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.selectionPenBottomIfAlsoActiveItem = QPen(_activeItemLineColor,
                                                       self.secili_nesne_kalem_kalinligi,
                                                       Qt.PenStyle.DashLine,
                                                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

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
        self.update()

    # ---------------------------------------------------------------------
    def setArkaPlanRengi(self, col):
        self.arkaPlanRengi = col
        self.setBrush(QBrush(col))
        if col.value() > 245:
            self.handleBrush = shared.handleBrushKoyu
        else:
            self.handleBrush = shared.handleBrushAcik

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):

        if change == QGraphicsTextItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.scene().parent().text_item_selected(self)
            else:
                self.scene().parent().text_item_deselected(self)

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

        self.textItemFocusedOut.emit(self)
        if self.scene():
            self.scene().parent()._statusBar.clearMessage()

        # self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        # self.clear_selection()
        if self.textCursor().hasSelection():
            return QGraphicsTextItem.focusOutEvent(self, event)

        super(Text, self).focusOutEvent(event)

    # ---------------------------------------------------------------------
    def clear_selection(self):
        cursor = self.textCursor()
        # self.cursor_eski_pozisyon = cursor.position()
        # self.cursor_eski_anchor = cursor.anchor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        # if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        #     self.scene().parent().web_browser_ac(self.text())
        # elif event.modifiers() == Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier:
        #     self.scene().parent().web_browser_ac("https://www.google.com/search?q=" + self.text())
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.yazi_kutusunu_daralt()

        # elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
        #     self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        #     self.clear_selection()

        else:
            # if self.textInteractionFlags() == Qt.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus()
            # self.clearFocus()
        super(Text, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def hoverEnterEvent(self, event):
        # event propagationdan dolayi bos da olsa burda implement etmek lazim
        # mousePress,release,move,doubleclick de bu mantıkta...
        # baska yerden baslayip mousepress ile , mousemove baska, mouseReleas baska widgetta gibi
        # icinden cikilmaz durumlara sebep olabiliyor.
        # ayrica override edince accept() de edilmis oluyor mouseeventler
        super(Text, self).hoverEnterEvent(event)

    # ---------------------------------------------------------------------
    def hoverMoveEvent(self, event):

        # cursor = self.scene().parent().cursor()

        # if self.isSelected() and self.scene().aktifArac == self.scene().SecimAraci:
        if not self.ustGrup:
            if self.scene().aktifArac == self.scene().SecimAraci:
                if self.topLeftHandle.contains(event.pos()) or self.bottomRightHandle.contains(event.pos()):
                    self.scene().parent().setCursor(Qt.CursorShape.SizeFDiagCursor, gecici_mi=True)
                    # self.setCursor(Qt.SizeFDiagCursor, gecici_mi=True)
                elif self.topRightHandle.contains(event.pos()) or self.bottomLeftHandle.contains(event.pos()):
                    self.scene().parent().setCursor(Qt.CursorShape.SizeBDiagCursor, gecici_mi=True)
                    # self.setCursor(Qt.SizeBDiagCursor, gecici_mi=True)
                else:
                    self.scene().parent().setCursor(self.scene().parent().imlec_arac, gecici_mi=True)

        super(Text, self).hoverMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverLeaveEvent(self, event):
        # if self.isSelected():
        # self.setCursor(self.saved_cursor)
        if not self.ustGrup:
            self.scene().parent().setCursor(self.scene().parent().imlec_arac, gecici_mi=True)

        super(Text, self).hoverLeaveEvent(event)

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):

        if self.ustGrup:
            return QGraphicsTextItem.wheelEvent(self, event)

        toplam = event.modifiers().value

        # ctrl = int(Qt.ControlModifier)
        shift = Qt.KeyboardModifier.ShiftModifier.value
        alt = Qt.KeyboardModifier.AltModifier.value

        ctrlAlt = Qt.KeyboardModifier.ControlModifier.value + Qt.KeyboardModifier.AltModifier.value
        ctrlShift = Qt.KeyboardModifier.ControlModifier.value + Qt.KeyboardModifier.ShiftModifier.value
        altShift = Qt.KeyboardModifier.AltModifier.value + Qt.KeyboardModifier.ShiftModifier.value
        ctrlAltShift = Qt.KeyboardModifier.ControlModifier.value + Qt.KeyboardModifier.AltModifier.value + Qt.KeyboardModifier.ShiftModifier.value

        # if event.modifiers() & Qt.ControlModifier:
        if toplam == ctrlShift:
            # self.scaleItem(event.delta())
            self.scaleItemWithFontSizeF(event.delta())
            # self.scaleItem(event.angleDelta().y())

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            self.changeFontSizeF(event.delta())

        # elif event.modifiers() & Qt.AltModifier:
        elif toplam == alt:
            self.changeBackgroundColorAlpha(event.delta())

        elif toplam == ctrlAlt:
            self.changeTextColorAlpha(event.delta())

        elif toplam == ctrlAltShift:
            self.rotateItem(event.delta())

        elif toplam == altShift:
            # self.changeImageItemTextBackgroundColorAlpha(event.delta())
            self.changeLineColorAlpha(event.delta())

        # elif toplam == ctrlAltShift:
        #     self.scaleItemWithFontSizeF(event.delta())

        else:
            super(Text, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def scaleItemWithFontSizeF2(self, delta):
        self.changeFontSizeF(delta)

    # ---------------------------------------------------------------------
    def scaleItemWithFontSizeF(self, delta):

        scaleFactor = 1.1
        if delta < 0:
            scaleFactor = 1 / scaleFactor
            # scaleFactor = 0.91

        # self.setTransformOriginPoint(self.boundingRect().center())
        # fontPointSizeF = max(3, (self.fontPointSizeF() * scaleFactor))
        fontPointSizeF = self.fontPointSizeF() * scaleFactor

        # eskiTamCerceve = self.boundingRect() | self.childrenBoundingRect()
        # yeniTamCerceveSize = eskiTamCerceve.size() * scaleFactor

        self.scene().undoRedo.undoableScaleTextItemByResizing(self.scene().undoStack,
                                                              "_scale by resizing",
                                                              self, scaleFactor, fontPointSizeF
                                                              )

        self.yazi_kutusunu_daralt()

    # ---------------------------------------------------------------------
    def changeFontSizeF(self, delta):
        # font = self.font()
        size = self.fontPointSizeF()

        if delta > 0:
            # font.setPointSizeF(size + 1)
            size += 1

        else:
            if size > 3:
                # font.setPointSizeF(size - 1)
                size -= 1
            else:
                # undolari biriktermesin diye donuyoruz,
                # yoksa zaten ayni size de yeni bir undolu size komutu veriyor.
                return

        self.scene().undoRedo.undoableSetFontSizeF(self.scene().undoStack, "change text size", self, size)
        self.yazi_kutusunu_daralt()
        # TODO: child items baseden bak

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
            self.scene().undoRedo.undoableRotateWithOffset(self.scene().undoStack, "rotate", self, self.rotation() + 5)
        else:
            # self.setRotation(self.rotation() - 5)
            self.scene().undoRedo.undoableRotateWithOffset(self.scene().undoStack, "rotate", self, self.rotation() - 5)
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
        # grup nesnesinden cagriliyor alt+shift
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
    def mousePressEvent(self, event):

        self._resizing = False  # we could use "self._resizingFrom = 0" instead, but self._resizing is more explicit.
        self._fixedResizePoint = None
        self._resizingFrom = None
        self._eskiRectBeforeResize = None

        self._eskiPosBeforeResize = self.pos()
        # self._eskiPosBeforeResize = self.scenePos()

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
            #                                         # yeniRect=self._rect,
            #                                         yeniRect=rect,
            #                                         eskiRect=self._eskiRectBeforeResize,
            #                                         eskiPos=self._eskiPosBeforeResize)

            # TODO: bu satir eger cizim disari tasarsa, scene recti ona uygun ayarlamak icin
            # fakat eger cizim disari tasarsa evet uyarliyor ama bazen de çizilen itemin geometrisini degistiriyor.
            # o yuzden simdilik iptal.
            # self.scene().unite_with_scene_rect(self.sceneBoundingRect())

            # rect = self.boundingRect()
            rect = self._rect
            # self.setPos(self.mapToScene(rect.topLeft()))
            # rect.moveTo(0, 0)
            # self.doc.setTextWidth(rect.width())

            # undo icinde
            # self.update_resize_handles()

            self.scene().undoRedo.undoableResizeBaseItem(self.scene().undoStack,
                                                         "resize",
                                                         self,
                                                         # yeniRect=self._rect,
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
    def yazi_kutusunu_daralt(self):
        # self._rect.setSize(QSizeF(self.doc.size()))
        r = QRectF(self._rect)
        # r.setSize(QSizeF(self.textWidth(), self.doc.size().height()))

        fm = QFontMetricsF(self.font())
        # yaziGenislik = fm.horizontalAdvance(self.text(), QTextOption())
        yaziGenislik = fm.boundingRect(r, 0, self.text()).size().width()
        # yaziYukseklik = fm.height()
        # self.doc.adjustSize()
        # self.doc.setTextWidth(yaziGenislik + 10)
        r.setWidth(yaziGenislik + 10)
        r.setHeight(self.doc.size().height())
        # r.setSize(QSizeF(self.doc.size()))
        self.setRect(r)

    # ---------------------------------------------------------------------
    def setRect(self, rect):
        if self._rect == rect:
            return

        self.prepareGeometryChange()
        self._rect = rect
        # TODO: burda direkt self.settextwidth niye demedik ki
        # self.doc.setTextWidth(rect.width())
        # self.doc.setPageSize(rect.size())
        self._boundingRect = rect.adjusted(-self.boundingRectTasmaDegeri, -self.boundingRectTasmaDegeri,
                                           self.boundingRectTasmaDegeri, self.boundingRectTasmaDegeri)
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
        # if self._rect.isEmpty():
        #     return super(Text, self).shape()
        # else:
        #     path.addRect(self._rect)
        # # return self.qt_graphicsItem_shapeFromPath(path, self._pen)
        #     return path

        path = QPainterPath()
        # path.addRect(self._rect)
        path.addRect(self._boundingRect)
        return path

    # ---------------------------------------------------------------------
    def boundingRect(self):
        # return self._rect
        return self._boundingRect
        # br = QRectF(self.rect())

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

        if event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
            # bu asagidaki if var cunku text item bos ise
            # birden fazla defa selectionqueue da remove etmeye calisabiliyor
            # veya item sahneden silindiginden item.scene() none donuyor gibi sebeplerden dolayi.
            # self.childItems() kontrolu de, yazi bir baska nesnenin parenti iken silinmis olabilir diye.
            if self.toPlainText() or self.childItems():
                self.setSelected(False)

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                self.clearFocus()
                if self.toPlainText() or self.childItems():
                    self.setSelected(False)

        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                self.clearFocus()
                if self.toPlainText() or self.childItems():
                    self.setSelected(False)
                    self.scene().create_empty_text_object_with_double_click(
                        QPointF(self.sceneLeft(), self.sceneBottom() + 10))

        super(Text, self).keyPressEvent(event)

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):
        rect = self.sceneBoundingRect()

        x = self.scenePos().x()
        y = self.scenePos().y()
        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = x - xs
        y = y - ys

        w = rect.width()
        h = rect.height()

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

        if self.isPlainText:
            yazi_str = f'<p style=" display: inline-block; ' \
                       f'color:rgba{renk_yazi}; ' \
                       f'margin:0; padding:7px;">{self.text()}</p>'
        else:
            html = self.toHtml()
            body_baslangic = html.find("<bo")
            bas = html.find('">', body_baslangic)
            son = html.find("</bo")
            # yazi = self.toHtml()
            yazi_str = html[bas + 2:son]

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

        div_str = f"""
                    <article style=" 
                     color:rgba{renk_yazi};
                     background:rgba{renk_arkaPlan};
                     font-size:{self.fontPointSizeF()}pt; 
                     font-family:{self.font().family()};
                     text-align: {yazi_hiza};
                     {bicimler1}
                     {bicimler2}
                     position:absolute;
                     z-index:{int(self.zValue() * 10) if self.zValue() else 0};
                     top:{y}px;
                     left:{x}px;
                     width:{w};
                     height:{h};
                     transform-box: fill-box;
                     transform-origin: top left;
                     transform: rotate({self.rotation()}deg);

                     " id="{self._kim}">{yazi_str}</article>\n
            """

        return div_str

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget):

        painter.save()
        # painter.fillRect(option.rect, self.arkaPlanRengi)
        painter.fillRect(option.rect, self.brush())

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
            painter.setPen(selectionPenBottom)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(option.rect)

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
        #     # painter.setPen(QPen(Qt.GlobalColor.red))
        #     painter.drawRect(option.rect)

        if self.isTextOverflowed:
            painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DotLine))
            painter.drawLine(self._boundingRect.bottomLeft(), self._boundingRect.bottomRight())

        # if not self.isPlainText:
        #     # painter.drawEllipse(self.zenginYaziBelirteci)
        #     # painter.drawText(5, 5, "📌🎨☼☀®")
        #     painter.drawText(0, 10, "*")

        # painter.setPen(Qt.blue)
        # painter.drawRect(self.boundingRect())
        # painter.setPen(Qt.green)
        # painter.drawRect(self._rect)
        painter.restore()

        # option2 = QStyleOptionGraphicsItem(option)
        # option2.state = 0
        # option.state &= ~(QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_HasFocus)
        # option2.exposedRect.setSize(self.document().pageSize())
        # # option2.exposedRect.setSize(self.document().documentLayout().documentSize())
        #
        # option.exposedRect = self.boundingRect()
        # option.rect = option.exposedRect.toRect()
        #
        # rect = QRectF(self._rect)
        # rect.moveTo(0, 0)
        # option2.exposedRect = rect

        # TODO bunlar niye koyuldu?
        option.exposedRect = self._rect
        option.rect = self._rect.toRect()

        # painter.setClipRect(option.exposedRect)
        super(Text, self).paint(painter, option, widget)

        # self.doc.drawContents(painter, self._rect)

        # # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self._rect,
        #                  "{0:.2f},  {1:.2f} pos \n{2:.2f},  {3:.2f} spos".format(p.x(), p.y(), s.x(), s.y()))
        # painter.setPen(QPen(Qt.green, 12))
        # painter.drawPoint(self.mapFromScene(self.sceneBoundingRect().center()))
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
        # painter.drawPoint(self.boundingRect().center())
        # painter.setPen(QPen(Qt.blue,8))
        # painter.drawPoint(self.sceneBoundingRect().center())
        # painter.drawRect(self.sceneBoundingRect())
        # # # # # # debug end - pos() # # # # #
