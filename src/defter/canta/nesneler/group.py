# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QStyle, QGraphicsItem
from .. import shared


########################################################################
class Group(QGraphicsItem):
    Type = shared.GROUP_ITEM_TYPE

    def __init__(self, arkaPlanRengi=Qt.GlobalColor.transparent,
                 yaziRengi=Qt.GlobalColor.transparent, pen=QPen(Qt.PenStyle.DotLine),
                 parent=None):
        super(Group, self).__init__(parent)

        self._kim = shared.kim(kac_basamak=16)

        self.ustGrup = None
        self._itemsBoundingRect = QRectF()

        self.setHandlesChildEvents(False)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                      | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                      # | QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
                      )

        self.secili_nesne_kalem_kalinligi = 0
        self.cizgiTipi = Qt.PenStyle.SolidLine
        self.cizgiUcuTipi = Qt.PenCapStyle.RoundCap
        self.cizgiBirlesimTipi = Qt.PenJoinStyle.RoundJoin

        self.activeItemLineColor = shared.activeItemLineColor
        self._pen = pen
        self.setCizgiRengi(pen.color())
        self.arkaPlanRengi = arkaPlanRengi  # grup nesnesinde kullanilmiyor
        self.yaziRengi = yaziRengi  # grup nesnesinde kullanilmiyor
        self.cizgiRengi = pen.color()

        self.cosmeticSelect = False
        self.isActiveItem = False
        self._isPinned = False

        self.allNonGroupGroupChildren = []
        self.parentedWithParentOperation = []  # as is
        self.allFirstLevelGroupChildren = []  # we use this for calculating group's bounding box.

        self.oklar_dxdy_nokta = {}

    # ---------------------------------------------------------------------
    def type(self):
        return Group.Type

    # ---------------------------------------------------------------------
    @property
    def isPinned(self):
        return self._isPinned

    # ---------------------------------------------------------------------
    @isPinned.setter
    def isPinned(self, value):
        if value:
            self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                          # | QGraphicsItem.ItemIsMovable
                          #  | QGraphicsItem.ItemIsFocusable
                          )

        else:
            self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                          | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                          | QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self._isPinned = value

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
    def update_resize_handles(self):
        # dummy method
        # while zooming, view, updates activeItem's resize handles.
        # filtering out group type is an another option but,
        # we may add resize functions to the group object in the future.
        # so ...
        pass

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      "kim": self._kim,
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "zValue": self.zValue(),
                      "yaziRengi": self.yaziRengi,  # yaziRengi grup nesnesinde aktik olarak kullanilmiyor
                      "arkaPlanRengi": self.arkaPlanRengi,  # arkaPlanRengi grup nesnesinde aktik olarak kullanilmiyor
                      "pen": self._pen,
                      "isPinned": self.isPinned,
                      }
        return properties

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

        # self.scene().parent().group_item_context_menu(self, event.screenPos())
        self.scene().parent().on_grup_sag_menu_about_to_show(self)
        self.scene().parent().grupSagMenu.popup(event.screenPos())
        event.accept()

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
    def moveCenterToPosition(self, scenePos):
        self.setPos(scenePos - self._itemsBoundingRect.center())

    # ---------------------------------------------------------------------
    def flipHorizontal(self, mposx):

        eskiRot = self.rotation()
        if eskiRot:
            self.rotateWithOffset(0)

        for c in self.allFirstLevelGroupChildren:
            c.flipHorizontal(mposx)
        self.updateBoundingRect()

        # burda, yani grupta, base itema gore biraz daha degisik bir durum var,
        # zaten burda basta sifirliyoruz rotationu, tekrar sifirlamaya gerek kalmiyor
        # eger grup item ayni zamanda normal parent ise, icerigi asagida flip ediyoruz.
        for c in self.parentedWithParentOperation:
            c.flipHorizontal(mposx)

        if eskiRot:
            self.rotateWithOffset(360 - eskiRot)

    # ---------------------------------------------------------------------
    def flipVertical(self, mposy):

        eskiRot = self.rotation()
        if eskiRot:
            self.rotateWithOffset(0)

        for c in self.allFirstLevelGroupChildren:
            c.flipVertical(mposy)
        self.updateBoundingRect()

        for c in self.parentedWithParentOperation:
            c.flipVertical(mposy)

        if eskiRot:
            self.rotateWithOffset(360 - eskiRot)

    # ---------------------------------------------------------------------
    def _update_rect_recursively(self, items, rect):

        for c in items:
            # rect = rect.united(self.mapRectFromItem(c, c.boundingRect()))
            rect |= self.mapRectFromItem(c, c.boundingRect())
            # burda sub item grup olsa bile ayirmaya gerek yok "allFirstLevelGroupChildren" diye childitemlari
            # cunku asıl grup hepsini kapsamak zorunda
            if c.childItems():
                rect = self._update_rect_recursively(c.childItems(), rect)

        return rect

    # ---------------------------------------------------------------------
    def updateBoundingRect(self):
        self.prepareGeometryChange()  # TODO: bunu debug et acaip uzun suruyor
        # rect = self.childrenBoundingRect()

        rect = QRectF()
        # for item in self.childItems():
        for item in self.allFirstLevelGroupChildren:
            # rect = rect.united(self.mapRectFromItem(item, item.boundingRect()))
            rect |= self.mapRectFromItem(item, item.boundingRect())
            # burda sub item grup olsa bile ayirmaya gerek yok "allFirstLevelGroupChildren" diye childitemlari
            # cunku asıl grup hepsini kapsamak zorunda
            if item.childItems():
                rect = self._update_rect_recursively(item.childItems(), rect)

        # self._itemsBoundingRect = rect

        # TODO: bir bak
        # pozisyonu sahne koordinatlarında topLefte almak icin,
        # ama scaled group mirrorunu bozuyor.
        diff = self.scenePos() - self.mapToScene(rect.topLeft())
        self.setPos(self.mapToScene(rect.topLeft()))
        rect.moveTo(0, 0)
        self._itemsBoundingRect = rect
        for c in self.allFirstLevelGroupChildren:
            # c.setPos(c.pos()+diff)
            c.moveBy(diff.x(), diff.y())

        # self.tumElemanlariEkleyincePozisyonGuncelle()

    # # ---------------------------------------------------------------------
    # def tumElemanlariEkleyincePozisyonGuncelle(self):
    #     # self.updateBoundingRect()
    #     self.setPos(self.mapToScene(self._itemsBoundingRect.topLeft()))

    # ---------------------------------------------------------------------
    def addSingleItemToGroup(self, item):
        if not item:
            return
        # self.prepareGeometryChange()
        eskiItemRot = item.rotation()
        item.setParentItem(self)
        item.ustGrup = self
        item.rotateWithOffset(eskiItemRot - self.rotation())
        item.isPinned = True  # !! bunun yeri onemli , asagidaki flagleri set edisimizin altında bunu set edersek,
        # isPinned bir property oldugundan, set kisminda her halukarda  "ItemIsSelectable ,True"oldugundan override
        # ediyor ve gruplanmis item secilebilir oluyor.
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, True)
        # TODO: ispinned e niye gerek duyduk.. destroy groupta da false ediliyor

        if item.type() == self.type():
            # TODO: set ve daha sonra destroy mu kullansak, ungroup ederken.
            self.allNonGroupGroupChildren.extend(item.allNonGroupGroupChildren)
        else:
            self.allNonGroupGroupChildren.append(item)
            if item.childItems():
                self.allNonGroupGroupChildren.extend(item.childItems())
        # we re adding directly because, if an item and its parent is selected, we don't add item to a group,
        # we re adding only its parent.
        self.allFirstLevelGroupChildren.append(item)

    # ---------------------------------------------------------------------
    def destroyGroupForPaste(self):
        # python deletes these "reparented to None" items, if we dont keep references to them.
        unGroupedRootItems = []

        # for item in self.childItems():
        # + self.parentedWithParentOperation cunku normal parent edilmis nesneleri ungroup edince siliyor.
        for item in self.allFirstLevelGroupChildren:  # + self.parentedWithParentOperation:
            # if for first level child items
            # if item.parentItem() == self:
            pos = self.mapToScene(item.pos())
            unGroupedRootItems.append(item)
            item.setParentItem(None)
            item.setPos(pos)
            item.setSelected(True)

        self.scene().unGroupedRootItems.update(unGroupedRootItems)

    # ---------------------------------------------------------------------
    def destroyGroup(self):
        # items = self.childItems()

        # python deletes these "reparented to None" items, if we dont keep references to them.
        unGroupedRootItems = []

        # for item in self.childItems():
        # + self.parentedWithParentOperation cunku normal parent edilmis nesneleri ungroup edince siliyor.
        # self.parentedWithParentOperation[:] kopyasi cunku : itemchange te otomatik olarak bosaltildigi icin
        for item in self.allFirstLevelGroupChildren + self.parentedWithParentOperation[:]:
            # if for first level child items
            # if item.parentItem() == self:
            parent = self.parentItem()
            if not parent:
                pos = self.mapToScene(item.pos())
                unGroupedRootItems.append(item)
                item.setParentItem(parent)  # sets parent to None
            else:
                pos = self.mapToItem(parent, item.pos())  # eger grup parented ise, cozulunce icerigi ayni yerde kalsin.
                item.setParentItem(parent)
                if parent.type() == self.type():
                    parent.parentedWithParentOperation.append(item)

            item.isPinned = False
            item.ustGrup = None
            if not item.type() == shared.LINE_ITEM_TYPE:
                item.rotateWithOffset(self.rotation() + item.rotation())
            else:
                item.rotateWithOffset(self.rotation() - item.rotation())
                # item._line.setAngle(item._line.angle() - self.rotation())
                # item.update_arrow()
            item.setPos(pos)
            item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                          QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                          QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, False)
            # TODO: info: gruplanmiş parentlarin childlerini grupta tutmuyoruz. dolayisi ile
            # burda manual ayarliyoruz flaglari. yoksa secilemez oluyrolar. manual false etmistik zaten act_groupta.
            if not item.type() == self.type():  # grubun iceriginin secilemezligi korunsun diye
                for c in item.childItems():
                    c.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                               QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                               QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
                    c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, False)
                    c.setSelected(True)
            else:
                for c in item.parentedWithParentOperation:
                    c.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                               QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                               QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
                    c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, False)
                    c.setSelected(True)
            item.setSelected(True)
        self.scene().unGroupedRootItems.update(unGroupedRootItems)
        self.setSelected(False)  # to remove from selectionQueue
        self.parentedWithParentOperation = []
        self.allFirstLevelGroupChildren = []
        self.allNonGroupGroupChildren = []

        # no need to below, because we will delete this instance immediately.
        # self.prepareGeometryChange()
        # self._itemsBoundingRect = self.childrenBoundingRect()

    # ---------------------------------------------------------------------
    def boundingRect(self):
        return self._itemsBoundingRect

    # # ---------------------------------------------------------------------
    # def shape(self):
    #     path = QPainterPath()
    #     # path.addRect(self.rect)
    #     path.addRect(self._itemsBoundingRect)
    #     # return self.qt_graphicsItem_shapeFromPath(path, self._pen)
    #     return path

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):
        # if change == self.ItemPositionChange:
        # if change == self.ItemSelectedChange:
        # if change == self.ItemSelectedHasChanged:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.scene().parent().group_item_selected(self)
                # self.selectAllChildren()
            else:
                self.scene().parent().group_item_deselected(self)
                # self.deSelectAllChildren()

        if change == QGraphicsItem.GraphicsItemChange.ItemChildRemovedChange:  # sahneden delete ile mesela remove edince, bir de unparent edince
            # TODO: allNonGroupGroupChildren yerine bu changed kullanilabilir mi acaba.
            if value in self.parentedWithParentOperation:
                self.parentedWithParentOperation.remove(value)

        # return QGraphicsRectItem.itemChange(self, change, value)
        return value
        # super(Rect, self).itemChange(change, value)

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
    def setCizgiKalinligi(self, width):
        self._pen.setWidthF(width)
        # self.textPen.setWidthF(width)
        # self.selectionPenBottom.setWidthF(width)
        # self.selectionPenBottomIfAlsoActiveItem.setWidthF(width)
        # self.selectionPenTop.setWidthF(width)

        self.update()

    # ---------------------------------------------------------------------
    def setArkaPlanRengi(self, col):
        # arkaplanRengi ve yaziRengi grup nesnesinde kullanilmiyor
        # fasulyeden method
        self.arkaPlanRengi = col

    # ---------------------------------------------------------------------
    def setYaziRengi(self, col):
        # arkaplanRengi ve yaziRengi grup nesnesinde kullanilmiyor
        # fasulyeden method
        self.yaziRengi = col

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):

        super(Group, self).mousePressEvent(event)

        # print(self.allFirstLevelGroupChildren)
        # print(self.allNonGroupGroupChildren)
        # print(self.parentedWithParentOperation)

        # TODO: bu kozmetik amacli, sadece release de olunca gecikmeli seciyormus hissi oluyor
        if self.isSelected() and self.parentedWithParentOperation:
            self.scene().select_all_children_recursively(self, cosmeticSelect=True)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):

        super(Group, self).mouseReleaseEvent(event)

        # TODO: and self.childItems() a gerek var mi. bos grup olmuyor cunku.
        if self.parentedWithParentOperation:
            if self.isSelected():
                self.scene().select_all_children_recursively(self, cosmeticSelect=False, topmostParent=True)
            else:
                self.scene().select_all_children_recursively(self, cosmeticSelect=False, topmostParent=False)

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):

        if self.ustGrup:
            return QGraphicsItem.wheelEvent(self, event)

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
            self.scaleItemByResizing(event.delta())

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            self.changeFontSizeF(event.delta())

        elif toplam == alt:
            self.changeBackgroundColorAlpha(event.delta())

        elif toplam == ctrlAlt:
            self.changeLineColorAlpha(event.delta())

        elif toplam == ctrlAltShift:
            self.rotateItem(event.delta())

        elif toplam == altShift:
            self.changeImageItemTextBackgroundColorAlpha(event.delta())
        #
        # elif toplam == ctrlAltShift:
        #     pass

        else:
            super(Group, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def scaleItemByResizing(self, delta):

        scaleFactor = 1.1
        if delta < 0:
            scaleFactor = 1 / scaleFactor

        # eskiTamCerceve = self.boundingRect() | self.childrenBoundingRect()
        # rect = self.childrenBoundingRect()
        rect = self._itemsBoundingRect
        center = rect.center()

        rect = QRectF(rect.topLeft(), rect.size() * scaleFactor)
        rect.moveCenter(center)
        yeniPos = self.mapToScene(rect.topLeft())
        if self.parentItem():
            yeniPos = self.mapToParent(rect.topLeft())
        rect.moveTo(0, 0)

        self.scene().undoRedo.undoableScaleGroupItemByResizing(self.scene().undoStack,
                                                               "_scale by resizing",
                                                               self, rect, scaleFactor,
                                                               yeniPos)

        # self.updateBoundingRect()

    # ---------------------------------------------------------------------
    def rotateWithOffset(self, angle):
        cEski = self.sceneCenter()
        self.setRotation(angle)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())
        # self.updateBoundingRect()

    # ---------------------------------------------------------------------
    def rotateItem(self, delta):
        if delta > 0:
            # self.setRotation(self.rotation() + 5)
            # self.rotateWithOffset(self.rotation() + 5)
            self.scene().undoRedo.undoableRotateWithOffset(self.scene().undoStack, "rotate", self, self.rotation() + 5)
        else:
            # self.setRotation(self.rotation() - 5)
            # self.rotateWithOffset(self.rotation() - 5)
            self.scene().undoRedo.undoableRotateWithOffset(self.scene().undoStack, "rotate", self, self.rotation() - 5)

    # ---------------------------------------------------------------------
    def changeBackgroundColorAlpha(self, delta):
        self.scene().undoStack.beginMacro("change items' background alpha")
        for c in self.childItems():
            c.changeBackgroundColorAlpha(delta)
        self.scene().undoStack.endMacro()

    # ---------------------------------------------------------------------
    def changeLineColorAlpha(self, delta):
        self.scene().undoStack.beginMacro("change items' line alpha")
        for c in self.childItems():
            c.changeLineColorAlpha(delta)
        self.scene().undoStack.endMacro()

    # ---------------------------------------------------------------------
    def changeFontSizeF(self, delta):
        self.scene().undoStack.beginMacro("change text size")
        for c in self.childItems():
            c.changeFontSizeF(delta)
        self.scene().undoStack.endMacro()

    # ---------------------------------------------------------------------
    def changeImageItemTextBackgroundColorAlpha(self, delta):
        self.scene().undoStack.beginMacro("change image items' text background alpha")
        for c in self.childItems():
            c.changeImageItemTextBackgroundColorAlpha(delta)
        self.scene().undoStack.endMacro()

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):
        # painter.setBrush(self.arkaPlanRengi)

        if option.state & QStyle.StateFlag.State_Selected or self.cosmeticSelect:
            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
            else:
                selectionPenBottom = self.selectionPenBottom

            painter.setPen(selectionPenBottom)
            # painter.drawRect(self.boundingRect())
            painter.drawRect(self._itemsBoundingRect)

            # painter.setPen(self.selectionPenTop)
            # painter.drawRect(self.boundingRect())

        else:
            painter.setPen(self._pen)
            # painter.drawRect(self.boundingRect())
            painter.drawRect(self._itemsBoundingRect)

        # if option.state & QStyle.StateFlag.State_MouseOver:
        #     painter.setBrush(Qt.BrushStyle.NoBrush)
        #     painter.setPen(self.selectionPenBottom)
        #     painter.drawRect(self._itemsBoundingRect)

        # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self.boundingRect(),
        #                  "{0:.2f},  {1:.2f} pos \n{2:.2f},  {3:.2f} spos".format(p.x(), p.y(), s.x(), s.y()))
        # painter.setPen(QPen(Qt.green, 8))
        # painter.drawPoint(self.mapFromScene(self.sceneBoundingRect().center()))
        # painter.drawPoint(0, 0)
        # painter.setPen(QPen(Qt.red, 16))
        # painter.drawPoint(self.mapFromScene(self.scenePos()))
        # painter.setPen(QPen(Qt.blue, 12))
        # painter.drawPoint(self.mapFromScene(self.scenePos()))
        # t = self.transformOriginPoint()
        # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self.boundingRect().topLeft())
        # painter.drawText(self.boundingRect().center().x(), self.boundingRect().center().y(),
        #                  "{0:.2f}  {1:.2f}".format(mapped.x(), mapped.y()))
        # painter.drawText(self.boundingRect().center().x(), self.boundingRect().center().y(),
        #                  "{0:.3f}".format(self.scale()))
        # painter.drawRect(self.boundingRect())
        # painter.setPen(QPen(Qt.yellow, 1))
        # painter.drawRect(QRectF(0, 0, 50, 50))
        # painter.drawText(self._rect.center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):
        return ""
