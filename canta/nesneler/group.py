# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtCore import (Qt, QRectF, QPointF)
from PySide6.QtGui import (QColor, QPen)
from PySide6.QtWidgets import (QStyle, QGraphicsItem)
from canta import shared


########################################################################
class Group(QGraphicsItem):
    Type = shared.GROUP_ITEM_TYPE

    def __init__(self, arkaPlanRengi=QColor(Qt.transparent), pen=QPen(Qt.DotLine), parent=None):
        super(Group, self).__init__(parent)

        self._kim = shared.kim(kac_basamak=16)

        self._itemsBoundingRect = QRectF()

        self.setHandlesChildEvents(True)
        self.setFlags(self.ItemIsSelectable
                      | self.ItemIsMovable
                      # | self.ItemIsFocusable
                      )

        self.secili_nesne_kalem_kalinligi = 0
        self.cizgiTipi = Qt.SolidLine
        self.cizgiUcuTipi = Qt.RoundCap
        self.cizgiBirlesimTipi = Qt.RoundJoin

        self.activeItemLineColor = shared.activeItemLineColor
        self._pen = pen
        self.setCizgiRengi(pen.color())
        # self.arkaPlanRengi(arkaPlanRengi)  # no need, in gorupItem, it only sets self.arkaplanRengi
        self.arkaPlanRengi = arkaPlanRengi

        self.cosmeticSelect = False
        self.isActiveItem = False
        self._isPinned = False

        self.allNonGroupGroupChildren = []
        self.parentedWithParentOperation = []  # as is
        self.allFirstLevelGroupChildren = []  # we use this for calculating group's bounding box.

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
    def update_resize_handles(self, force=False):
        # dummy method
        # while zooming, view, updates activeItem's resize handles.
        # filtering out group type is an another option but,
        # we may add resize functions to the group object in the future.
        # so ...
        pass

    # ---------------------------------------------------------------------
    def type(self):
        return Group.Type

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):
        return ""

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      "kim": self._kim,
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "scale": self.scale(),
                      "zValue": self.zValue(),
                      "arkaPlanRengi": self.arkaPlanRengi,
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
        # if not event.modifiers() & Qt.ControlModifier:
        #     self.scene().clearSelection()
        self.setSelected(True)

        # self.scene().parent().group_item_context_menu(self, event.screenPos())
        self.scene().parent().on_group_item_context_menu_about_to_show(self)
        self.scene().parent().groupContextMenu.popup(event.screenPos())
        event.accept()

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
    def moveCenterToPosition(self, scenePos):
        self.setPos(scenePos - self._itemsBoundingRect.center())

    # ---------------------------------------------------------------------
    def _update_scene_rect_recursively(self, items, rect):
        for c in items:
            rect = rect.united(c.sceneBoundingRect())
            if c.type() == Group.Type:
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
        for c in self.parentedWithParentOperation:
            rect = rect.united(c.sceneBoundingRect())
            if c.type() == Group.Type:
                if c.parentedWithParentOperation:
                    rect = self._update_scene_rect_recursively(c.parentedWithParentOperation, rect)
            else:
                if c.childItems():
                    rect = self._update_scene_rect_recursively(c.childItems(), rect)
        return rect

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
            rect = rect.united(self.mapRectFromItem(c, c.boundingRect()))
            # burda sub item grup olsa bile ayirmaya gerek yok "allFirstLevelGroupChildren" diye childitemlari
            # cunku asıl grup hepsini kapsamak zorunda
            if c.childItems():
                rect = self._update_rect_recursively(c.childItems(), rect)

        return rect

    # ---------------------------------------------------------------------
    def updateBoundingRect(self):
        self.prepareGeometryChange()  # TODO: bunu debug et acaip uzun suruyor
        # self._itemsBoundingRect = self.childrenBoundingRect()
        rect = QRectF()
        # for item in self.childItems():
        for item in self.allFirstLevelGroupChildren:
            rect = rect.united(self.mapRectFromItem(item, item.boundingRect()))
            # burda sub item grup olsa bile ayirmaya gerek yok "allFirstLevelGroupChildren" diye childitemlari
            # cunku asıl grup hepsini kapsamak zorunda
            if item.childItems():
                rect = self._update_rect_recursively(item.childItems(), rect)

        # # pozisyonu shane koordinatlarında topLefte almak icin,
        # # ama scaled group mirrorunu bozuyor.
        # diff = self.scenePos() - self.mapToScene(rect.topLeft())
        # self.setPos(self.mapToScene(rect.topLeft()))
        # rect.moveTo(0, 0)
        # for c in self.childItems():
        #     # c.setPos(c.pos()+diff)
        #     c.moveBy(diff.x(), diff.y())

        self._itemsBoundingRect = rect

    # # ---------------------------------------------------------------------
    # def addItemsToGroup(self, items):
    #     # TODO: if item == this !!
    #     if not items:
    #             return
    #
    #     for item in items:
    #         item.setParentItem(self)
    #         item.setFlag(item.ItemIsSelectable, False)
    #         item.setFlag(item.ItemIsMovable, False)
    #         item.setFlag(item.ItemIsFocusable, False)
    #         item.isPinned = True
    #         if item.type() == self.type():
    #             # TODO: set ve daha sonra destroy mu kullansak, ungroup ederken.
    #             self.allNonGroupGroupChildren.extend(item.allNonGroupGroupChildren)
    #         else:
    #             self.allNonGroupGroupChildren.append(item)
    #         self.allFirstLevelGroupChildren.append(item)
    #
    #     self.updateBoundingRect()

    # ---------------------------------------------------------------------
    def addSingleItemToGroup(self, item):
        if not item:
            return
        # self.prepareGeometryChange()
        eskiItemRot = item.rotation()
        eskiScale = item.scale()
        item.setParentItem(self)
        item.rotateWithOffset(eskiItemRot - self.rotation())
        item.scaleWithOffset(eskiScale / self.scale())
        item.isPinned = True  # !! bunun yeri onemli , asagidaki flagleri set edisimizin altında bunu set edersek,
        # isPinned bir property oldugundan, set kisminda her halukarda  "ItemIsSelectable ,True"oldugundan override
        # ediyor ve gruplanmis item secilebilir oluyor.
        item.setFlag(item.ItemIsSelectable, False)
        item.setFlag(item.ItemIsMovable, False)
        item.setFlag(item.ItemIsFocusable, False)
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

    # # ---------------------------------------------------------------------
    # def removeItemFromGroup(self, item):
    #     if not item:
    #         return
    #     parent = self.parentItem()
    #     pos = self.mapToScene(item.pos())
    #     # item.setParentItem(None)
    #     item.setParentItem(parent)
    #     item.isPinned = False
    #     item.setPos(pos)
    #     item.setFlags(self.ItemIsSelectable
    #                   | self.ItemIsMovable
    #                   | self.ItemIsFocusable
    #                   )
    #     # self.update()
    #     self.prepareGeometryChange()
    #     self._itemsBoundingRect = self.childrenBoundingRect()

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
            if not item.type() == shared.LINE_ITEM_TYPE:
                item.rotateWithOffset(self.rotation() + item.rotation())
            else:
                item.rotateWithOffset(self.rotation() - item.rotation())
                # item._line.setAngle(item._line.angle() - self.rotation())
                # item.update_arrow()
            item.scaleWithOffset(self.scale() * item.scale())
            item.setPos(pos)
            item.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemIsFocusable)
            # TODO: info: gruplanmiş parentlarin childlerini grupta tutmuyoruz. dolayisi ile
            # burda manual ayarliyoruz flaglari. yoksa secilemez oluyrolar. manual false etmistik zaten act_groupta.
            if not item.type() == self.type():  # grubun iceriginin secilemezligi korunsun diye
                for c in item.childItems():
                    c.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemIsFocusable)
                    c.setSelected(True)
            else:
                for c in item.parentedWithParentOperation:
                    c.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemIsFocusable)
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
        # rect = QRectF()
        # # for item in self.childItems():
        # for item in self.allFirstLevelGroupChildren:
        #     rect = rect.unite(self.mapRectFromItem(item, item.boundingRect()))
        # return rect
        return self._itemsBoundingRect
        # TODO: icindeki itemleer scale ve rotate edilince bbox degismiyor.
        # itemlardan bir signal mi gondersek, grup icinde de degillerse o zaman bosa kaynak harcanmasin.
        # alttaki satir biraz cozuyor gibi ama o da yine surekli hesap
        # return self.childrenBoundingRect()

    # # ---------------------------------------------------------------------
    # def shape(self):
    #     path = QPainterPath()
    #     # path.addRect(self.rect)
    #     path.addRect(self._rect)
    #     return self.qt_graphicsItem_shapeFromPath(path, self._pen)

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):
        # if change == self.ItemPositionChange:
        # if change == self.ItemSelectedChange:
        # if change == self.ItemSelectedHasChanged:
        if change == self.ItemSelectedChange:
            if value:
                self.scene().parent().group_item_selected(self)
                # self.selectAllChildren()
            else:
                self.scene().parent().group_item_deselected(self)
                # self.deSelectAllChildren()

        if change == self.ItemChildRemovedChange:  # sahneden delete ile mesela remove edince, bir de unparent edince
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
        # self.cizgiRengi = col

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
        # self.setBrush(QBrush(col))
        self.update()

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):
        # painter.setBrush(self.arkaPlanRengi)

        if option.state & QStyle.State_Selected or self.cosmeticSelect:
            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
            else:
                selectionPenBottom = self.selectionPenBottom

            painter.setPen(selectionPenBottom)
            painter.drawRect(self.boundingRect())

            # painter.setPen(self.selectionPenTop)
            # painter.drawRect(self.boundingRect())

        else:
            painter.setPen(self._pen)
            painter.drawRect(self.boundingRect())

        # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self.boundingRect(),
        #                  "{0:.2f},  {1:.2f} pos \n{2:.2f},  {3:.2f} spos".format(p.x(), p.y(), s.x(), s.y()))
        # painter.setPen(QPen(Qt.green,12))
        # painter.drawPoint(self.mapFromScene(self.sceneBoundingRect().center()))
        # t = self.transformOriginPoint()
        # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self.boundingRect().topLeft())
        # painter.drawText(self.boundingRect().center().x(), self.boundingRect().center().y(),
        #                  "{0:.2f}  {1:.2f}".format(mapped.x(), mapped.y()))
        # painter.drawText(self.boundingRect().center().x(), self.boundingRect().center().y(),
        #                  "{0:.3f}".format(self.scale()))
        # painter.drawRect(self.boundingRect())
        # painter.drawText(self.rect().center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # # # # # debug end - pos() # # # # #

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
            self.scaleItem(event.delta())

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            self.rotateItem(event.delta())

        elif toplam == alt:
            self.changeBackgroundColorAlpha(event.delta())

        elif toplam == ctrlAlt:
            self.changeLineColorAlpha(event.delta())

        elif toplam == ctrlAltShift:
            self.changeFontSize(event.delta())

        elif toplam == altShift:
            self.changeImageItemTextBackgroundColorAlpha(event.delta())
        #
        # elif toplam == ctrlAltShift:
        #     pass

        else:
            super(Group, self).wheelEvent(event)

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
        # self.updateBoundingRect()

    # ---------------------------------------------------------------------
    def rotateWithOffset(self, angle):
        cEski = self.sceneCenter()
        self.setRotation(angle)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())

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
    def changeFontSize(self, delta):
        self.scene().undoStack.beginMacro("change text size")
        for c in self.childItems():
            c.changeFontSize(delta)
        self.scene().undoStack.endMacro()

    # ---------------------------------------------------------------------
    def changeImageItemTextBackgroundColorAlpha(self, delta):
        self.scene().undoStack.beginMacro("change image items' text background alpha")
        for c in self.childItems():
            c.changeImageItemTextBackgroundColorAlpha(delta)
        self.scene().undoStack.endMacro()
