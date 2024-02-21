# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

import filecmp
import os
import shutil

from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QGraphicsItem

from .nesneler.group import Group
from .nesneler.base import BaseItem
from . import shared


# # ---------------------------------------------------------------------
# def tum_parentitemleri_tara_ve_grup_tipinde_olanlarin_boundingrectini_guncelle(nesne):
#     if nesne.parentItem():
#         if nesne.parentItem().type() == shared.GROUP_ITEM_TYPE:
#             nesne.parentItem().updateBoundingRect()
#         tum_parentitemleri_tara_ve_grup_tipinde_olanlarin_boundingrectini_guncelle(nesne.parentItem())


#######################################################################
class UndoRedoBaglantisiYaziNesnesiDocuna(QUndoCommand):
    # ---------------------------------------------------------------------
    def __init__(self, description, doc, parent=None):
        self.doc = doc
        super(UndoRedoBaglantisiYaziNesnesiDocuna, self).__init__(description, parent)

    # ---------------------------------------------------------------------
    def undo(self) -> None:
        self.doc.undo()

    # ---------------------------------------------------------------------
    def redo(self) -> None:
        self.doc.redo()


########################################################################
class UndoableSayfaAdiDegistir(QUndoCommand):
    """ """

    # TODO: sayfa ve itemin burda referanslarinin tutulmasi problem olur mu acaba,
    # tab kapatılınca veya sayfa silinince silinmiş gozukuyorlar gibi ama detaylı da bakılmadı.

    # ---------------------------------------------------------------------
    def __init__(self, description, sayfa, sayfa_eski_adi, parent=None):
        super(UndoableSayfaAdiDegistir, self).__init__(description, parent)

        self.sayfa = sayfa
        self.sayfa_adi = sayfa.adi
        self.sayfa_eski_adi = sayfa_eski_adi

    # ---------------------------------------------------------------------
    def redo(self):
        # TODO: gerek var mı blocklamaya?? ?
        # self.sayfa.model().blockSignals(True)
        self.sayfa.adi = self.sayfa_adi
        # self.sayfa.setData(self.sayfa_adi, Qt.DisplayRole)
        # self.sayfa.model().blockSignals(False)

    # ---------------------------------------------------------------------
    def undo(self):
        # self.sayfa.model().blockSignals(True)
        self.sayfa.adi = self.sayfa_eski_adi
        # self.sayfa.setData(self.eski_sayfa_adi, Qt.DisplayRole)
        # self.sayfa.model().blockSignals(False)


########################################################################
class UndoableAddItem(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, scene, item, parent=None):
        super(UndoableAddItem, self).__init__(description, parent)
        self.scene = scene
        self.item = item

    # ---------------------------------------------------------------------
    def redo(self):
        self.scene.parent().act_aramayi_temizle()

        self.scene.addItem(self.item)
        if isinstance(self.item, BaseItem):
            self.item.update_resize_handles()
        self.scene.clearSelection()
        # setSelected iptal edildi. Nesne sayisi cok olan dosyalarin acilis hizi yari yariyadan fazla dusuyor.
        # self.item.setSelected(self.sec)
        # alt satiri burda cagirmiyoruz cunku bazi nesneler ilk once bos olarak ekleniyor, icerikleri sonra ekleniyor.
        # self.scene.unite_with_scene_rect(self.item.mapRectToScene(self.item.boundingRect()))

        # oklar varsa oka bu nesneyi kaydet
        if self.item.oklar_dxdy_nokta:
            for ok, dx_dy_nokta in self.item.oklar_dxdy_nokta.items():
                ok.baglanmis_nesneler[self.item._kim] = dx_dy_nokta[2]

        # silinen ok ise, okun eski bagli oldugu nesnelere okun bilgisini tekrar ekliyoruz
        if self.item.type() == shared.LINE_ITEM_TYPE:
            if self.item.baglanmis_nesneler:
                for baglanmis_nesne_kimlik, nokta in self.item.baglanmis_nesneler.items():  # dict items()
                    baglanmis_nesne = self.scene._kimlik_nesne_sozluk[baglanmis_nesne_kimlik]
                    if nokta == 1:
                        baglanmis_nesne.ok_ekle(self.item, self.item.mapToScene(self.item._line.p1()),
                                                1)
                    if nokta == 2:
                        baglanmis_nesne.ok_ekle(self.item, self.item.mapToScene(self.item._line.p2()),
                                                2)

    # ---------------------------------------------------------------------
    def undo(self):
        self.scene.parent().act_aramayi_temizle()

        # oklar varsa, oktan bu nesneyi sil, (silinen nesne bir ok nesnesi degil)
        if self.item.oklar_dxdy_nokta:
            for ok in self.item.oklar_dxdy_nokta.keys():
                del ok.baglanmis_nesneler[self.item._kim]

        # silinen ok ise, okun baglanmis oldugu nesnelerden okun bilgisini siliyoruz
        if self.item.type() == shared.LINE_ITEM_TYPE:
            if self.item.baglanmis_nesneler:
                for baglanmis_nesne_kimlik, nokta in self.item.baglanmis_nesneler.items():  # dict items()
                    baglanmis_nesne = self.scene._kimlik_nesne_sozluk[baglanmis_nesne_kimlik]
                    del baglanmis_nesne.oklar_dxdy_nokta[self.item]

        self.scene.clearSelection()
        self.scene.removeItem(self.item)


########################################################################
class UndoableRemoveItem(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, scene, item, addToUnGroupedRootItems=False, parent=None):
        super(UndoableRemoveItem, self).__init__(description, parent)
        self.item = item
        self.scene = scene
        self.itemParent = item.parentItem()
        self.addToUnGroupedRootItems = addToUnGroupedRootItems

    # ---------------------------------------------------------------------
    def redo(self):
        self.scene.parent().act_aramayi_temizle()

        self.scene.clearSelection()
        if self.item.type() == shared.VIDEO_ITEM_TYPE:
            self.item.nesne_sahneden_silinmek_uzere()
        self.scene.removeItem(self.item)
        # # ilk silerken, itemlar secili ve selectionQueue icindeler,
        # # ama undo edip sahneye geri aldik ve de her seyi secisiz halde getirip
        # # sonra tekrar redo ile ikinci defa sildigimizde bu sefer az once secisiz hale geldiklerinde
        # # selectionQueue dan silinmeleri sebebi ile, bu ikinci redo da alt satirda tekrar silinmeye calisildiklarindan
        # # hata oluyor. dolayisi ile if ile kontrol ediyoruz.
        # if self.item in self.scene.selectionQueue:
        #     self.scene.selectionQueue.remove(self.item)

        if self.addToUnGroupedRootItems:
            self.scene.unGroupedRootItems.discard(self.item)

        # oklar varsa, oktan bu nesneyi sil, (silinen nesne bir ok nesnesi degil)
        if self.item.oklar_dxdy_nokta:
            for ok in self.item.oklar_dxdy_nokta.keys():
                del ok.baglanmis_nesneler[self.item._kim]

        # silinen ok ise, okun baglanmis oldugu nesnelerden okun bilgisini siliyoruz
        if self.item.type() == shared.LINE_ITEM_TYPE:
            if self.item.baglanmis_nesneler:
                for baglanmis_nesne_kimlik, nokta in self.item.baglanmis_nesneler.items():  # dict items()
                    baglanmis_nesne = self.scene._kimlik_nesne_sozluk[baglanmis_nesne_kimlik]
                    del baglanmis_nesne.oklar_dxdy_nokta[self.item]

    # # ---------------------------------------------------------------------
    # def append_all_childitems_in_hierarchy_to_selection_queue(self, i):
    #     for c in i.childItems():
    #         if c.childItems():
    #             self.append_all_childitems_in_hierarchy_to_selection_queue(c)
    #         # tempList.append(c)
    #         self.scene.selectionQueue.append(c, simpleAppend=True)

    # ---------------------------------------------------------------------
    def undo(self):
        self.scene.parent().act_aramayi_temizle()

        # self.scene.selectionQueue.append(self.item)
        # # normalde en alt satirdaki select_all_children_recursively halletmesi lazim
        # # ama onu itemlari mouseReleasinde kullaniyoruz super().mouseRelease den sonra
        # # dolayısı ile super() secmiş oluyor ve de selectionQueue ya eklenmis oluyorlar
        # # yine dolayisi ile biz select_all_children_recursively de secsek de, tekrar eklemiyoruz
        # # selectionQueue ya. o yuzden burda recursive eklemek durumundayiz .
        # self.append_all_childitems_in_hierarchy_to_selection_queue(self.item)

        self.scene.addItem(self.item)
        if self.itemParent:
            self.item.setParentItem(self.itemParent)
            if self.itemParent.type() == shared.GROUP_ITEM_TYPE:
                self.itemParent.parentedWithParentOperation.append(self.item)
        if self.addToUnGroupedRootItems:
            self.scene.unGroupedRootItems.add(self.item)
        # self.scene.select_all_children_recursively(self.item, cosmeticSelect=False, topmostParent=True)

        # oklar varsa oka bu nesneyi kaydet
        if self.item.oklar_dxdy_nokta:
            for ok, dx_dy_nokta in self.item.oklar_dxdy_nokta.items():
                ok.baglanmis_nesneler[self.item._kim] = dx_dy_nokta[2]

        # silinen ok ise, okun eski bagli oldugu nesnelere okun bilgisini tekrar ekliyoruz
        if self.item.type() == shared.LINE_ITEM_TYPE:
            if self.item.baglanmis_nesneler:
                for baglanmis_nesne_kimlik, nokta in self.item.baglanmis_nesneler.items():  # dict items()
                    baglanmis_nesne = self.scene._kimlik_nesne_sozluk[baglanmis_nesne_kimlik]
                    if nokta == 1:
                        baglanmis_nesne.ok_ekle(self.item, self.item.mapToScene(self.item._line.p1()),
                                                1)
                    if nokta == 2:
                        baglanmis_nesne.ok_ekle(self.item, self.item.mapToScene(self.item._line.p2()),
                                                2)


########################################################################
class UndoableMove(QUndoCommand):
    # TODO:  bazen moved 0 item diyor ozellikle kaydedilmis dosya yukleyip icerigini hareket ettirince.
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, movedItem, eskiPosition, parent=None):
        """ """
        super(UndoableMove, self).__init__(description, parent)

        self.movedItem = movedItem
        self.eskiPosition = eskiPosition
        self.yeniPosition = self.movedItem.pos()

    # ---------------------------------------------------------------------
    def undo(self):
        # self.movedItem.moveBy(-self.dx, -self.dy)
        self.movedItem.setPos(self.eskiPosition)
        self.movedItem.ok_guncelle()

        # ok bagli iken nesne olarak tasinirsa, bagli oldugu nesnelere bagliligi devam ettigi halde baglanti noktalarina
        # olan bagi gevsetiliyor (offset)
        if self.movedItem.type() == shared.LINE_ITEM_TYPE:
            if self.movedItem.baglanmis_nesneler:
                for baglanmis_nesne_kimlik, nokta in self.movedItem.baglanmis_nesneler.items():  # dict items()
                    baglanmis_nesne = self.movedItem.scene()._kimlik_nesne_sozluk[baglanmis_nesne_kimlik]
                    if nokta == 1:
                        baglanmis_nesne.ok_ekle(self.movedItem, self.movedItem.mapToScene(self.movedItem._line.p1()),
                                                1)
                    if nokta == 2:
                        baglanmis_nesne.ok_ekle(self.movedItem, self.movedItem.mapToScene(self.movedItem._line.p2()),
                                                2)

    # ---------------------------------------------------------------------
    def redo(self):
        # self.movedItem.moveBy(self.dx, self.dy)
        self.movedItem.setPos(self.yeniPosition)
        self.movedItem.ok_guncelle()

        # ok bagli iken nesne olarak tasinirsa, bagli oldugu nesnelere bagliligi devam ettigi halde baglanti noktalarina
        # olan bagi gevsetiliyor (offset)
        if self.movedItem.type() == shared.LINE_ITEM_TYPE:
            if self.movedItem.baglanmis_nesneler:
                for baglanmis_nesne_kimlik, nokta in self.movedItem.baglanmis_nesneler.items():  # dict items()
                    baglanmis_nesne = self.movedItem.scene()._kimlik_nesne_sozluk[baglanmis_nesne_kimlik]
                    if nokta == 1:
                        baglanmis_nesne.ok_ekle(self.movedItem, self.movedItem.mapToScene(self.movedItem._line.p1()),
                                                1)
                    if nokta == 2:
                        baglanmis_nesne.ok_ekle(self.movedItem, self.movedItem.mapToScene(self.movedItem._line.p2()),
                                                2)


########################################################################
class UndoableMovePathPoint(QUndoCommand):

    # ---------------------------------------------------------------------
    def __init__(self, description, item, movedPointIndex, eskiPosTuple, yeniPosTuple, parent=None):
        """ """
        super(UndoableMovePathPoint, self).__init__(description, parent)

        self.item = item
        self.movedPointIndex = movedPointIndex
        self.eskiPosTuple = eskiPosTuple
        self.yeniPosTuple = yeniPosTuple

    # ---------------------------------------------------------------------
    def undo(self):
        self.item._path.setElementPositionAt(self.movedPointIndex, self.eskiPosTuple[0], self.eskiPosTuple[1])
        self.item.update()

    # ---------------------------------------------------------------------
    def redo(self):
        self.item._path.setElementPositionAt(self.movedPointIndex, self.yeniPosTuple[0], self.yeniPosTuple[1])
        self.item.update()


########################################################################
class UndoableDeletePathPoint(QUndoCommand):

    # ---------------------------------------------------------------------
    def __init__(self, description, item, eskiPath, yeniPath, parent=None):
        """ """
        super(UndoableDeletePathPoint, self).__init__(description, parent)

        self.item = item
        self.eskiPath = eskiPath
        self.yeniPath = yeniPath

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setPath(self.eskiPath)
        # self.item.update()

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setPath(self.yeniPath)
        # self.item.update()


########################################################################
class UndoableGroup(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, items, scene, parent=None):
        super(UndoableGroup, self).__init__(description, parent)

        self.group = Group()
        self.items = items
        self.scene = scene

    # ---------------------------------------------------------------------
    def redo(self):
        self.scene.addItem(self.group)
        self.scene.parent().increase_zvalue(self.group)
        for item in self.items:
            if item.parentItem():
                if item.parentItem() in self.items:  # o zaman bunu gruplamaya gerek yok cunku parenti gruplanacak zaten.
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, True)
                    # muhtemelen parentta da sorun var
                    # continue
                else:
                    self.scene.parent().act_unparent_items(item)
                    self.group.addSingleItemToGroup(item)
                    # TODO: if ile kontrol etsek once daha mi hizli olur, time complexity ye bakmak lazim.
                    # gruplandigi icin referansi parentta olacak ayrica tutmaya gerek yok
                    # burda da ihtiyac var discarda cunku yukarda unparent edilince ekleniyor unGroupedRootItems a.
                    self.scene.unGroupedRootItems.discard(item)
            else:
                if item.childItems():  # sadece parent secilmis iken alt nesneleri secilemez hale getiriyoruz.
                    for c in item.childItems():
                        c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                        c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                        c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)
                        c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, True)
                self.group.addSingleItemToGroup(item)
                # TODO: if ile kontrol etsek once daha mi hizli olur, time complexity ye bakmak lazim.
                # gruplandigi icin referansi parentta olacak ayrica tutmaya gerek yok
                self.scene.unGroupedRootItems.discard(item)
        self.group.updateBoundingRect()
        self.group.setSelected(True)

    # ---------------------------------------------------------------------
    def undo(self):
        self.group.destroyGroup()
        self.scene.removeItem(self.group)


########################################################################
class UndoableUnGroup(QUndoCommand):
    """ """

    def __init__(self, description, group, parent=None):
        super(UndoableUnGroup, self).__init__(description, parent)
        self.group = group
        self.scene = group.scene()
        self.itemsList = group.allFirstLevelGroupChildren
        self.itemsListWithPos = [[item, item.pos()] for item in group.allFirstLevelGroupChildren]
        # self.itemsDictWithPos = {item: item.pos() for item in group.allFirstLevelGroupChildren}
        # import sys
        # print(sys.getsizeof(self.itemsListWithPos))
        # print(sys.getsizeof(self.itemsDictWithPos))

    # ---------------------------------------------------------------------
    def redo(self):
        self.group.destroyGroup()
        self.scene.removeItem(self.group)
        # self.group.scene().removeItem(self.group)
        # oklar varsa, oktan bu nesneyi sil, (silinen nesne bir ok nesnesi degil)
        if self.group.oklar_dxdy_nokta:
            for ok in self.group.oklar_dxdy_nokta.keys():
                del ok.baglanmis_nesneler[self.group._kim]

    # ---------------------------------------------------------------------
    def undo(self):

        # group = Group()
        # # group = QGraphicsItemGroup(None)
        # group.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        #                |QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        #                # | QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
        #                )

        self.scene.addItem(self.group)
        # #### self.scene.parent().increase_zvalue(self.group)
        for item, itemEskiPos in self.itemsListWithPos:
            if item.parentItem():
                if item.parentItem() in self.itemsList:  # o zaman bunu gruplamaya gerek yok cunku parenti gruplanacak zaten.
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, True)
                    # muhtemelen parentta da sorun var
                    # continue
                else:
                    # self.scene.parent().act_unparent_items(item)
                    self.group.addSingleItemToGroup(item)
                    # TODO: if ile kontrol etsek once daha mi hizli olur, time complexity ye bakmak lazim.
                    # gruplandigi icin referansi parentta olacak ayrica tutmaya gerek yok
                    # burda da ihtiyac var discarda cunku yukarda unparent edilince ekleniyor unGroupedRootItems a.
                    self.scene.unGroupedRootItems.discard(item)
            else:
                if item.childItems():  # sadece parent secilmis iken alt nesneleri secilemez hale getiriyoruz.
                    for c in item.childItems():
                        c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                        c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                        c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)
                        c.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, True)
                self.group.addSingleItemToGroup(item)
                # TODO: if ile kontrol etsek once daha mi hizli olur, time complexity ye bakmak lazim.
                # gruplandigi icin referansi parentta olacak ayrica tutmaya gerek yok
                self.scene.unGroupedRootItems.discard(item)
            item.setPos(itemEskiPos)
        # #### self.group.updateBoundingRect()
        # oklar varsa oka bu nesneyi kaydet
        if self.group.oklar_dxdy_nokta:
            for ok, dx_dy_nokta in self.group.oklar_dxdy_nokta.items():
                ok.baglanmis_nesneler[self.group._kim] = dx_dy_nokta[2]

        self.group.setSelected(True)


########################################################################
class UndoableParent(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, parentItem, yeniPos, parent=None):
        super(UndoableParent, self).__init__(description, parent)
        self.item = item
        self.parentItem = parentItem
        self.parentRot = 0
        while parentItem:
            # cunku itemRot mesela 40 derece ise, yeni parentRot 10 derece ise, item parent edilince 40-10 = 30 oluyor.
            # dolayısı ile ne kadar parent icinde ise hepsinin rotation toplami asil sceneRotation unu veriyor.
            self.parentRot += parentItem.rotation()
            parentItem = parentItem.parentItem()
        self.eskiParentItem = item.parentItem()
        self.yeniPos = yeniPos
        self.eskiPos = item.pos()
        self.eskiRot = item.rotation()

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setParentItem(self.parentItem)
        self.item.setPos(self.yeniPos)
        self.item.setRotation(self.item.rotation() - self.parentRot)
        # if self.parentItem:
        if self.parentItem.type() == shared.GROUP_ITEM_TYPE:
            self.parentItem.parentedWithParentOperation.append(self.item)
        self.item.scene().unGroupedRootItems.discard(self.item)

    # ---------------------------------------------------------------------
    def undo(self):
        if self.eskiParentItem:
            self.item.setParentItem(self.eskiParentItem)
            # eger self.eskiParentItem grupsa, parentedWithParentOperation dan silmeye gerek yok cunku
            # onu grupta hallediyoruz.
        else:
            self.item.scene().unGroupedRootItems.add(self.item)
            self.item.setParentItem(None)

        self.item.setPos(self.eskiPos)
        self.item.setRotation(self.eskiRot)


########################################################################
class UndoableUnParent(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, yeniParentItem, yeniPos, parent=None):
        super(UndoableUnParent, self).__init__(description, parent)
        self.item = item
        self.yeniParentItem = yeniParentItem

        self.yeniPos = yeniPos
        # self.eskiPos = item.scenePos()
        self.eskiPos = item.pos()

        self.eskiParentItem = item.parentItem()
        eskiParentItem = self.eskiParentItem
        self.eskiParentRot = 0
        while eskiParentItem:
            self.eskiParentRot += eskiParentItem.rotation()
            eskiParentItem = eskiParentItem.parentItem()

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.scene().unGroupedRootItems.add(self.item)
        self.item.setPos(self.yeniPos)
        self.item.setRotation(self.item.rotation() + self.eskiParentRot)
        self.item.setParentItem(self.yeniParentItem)
        # eger self.eskiParentItem grupsa, parentedWithParentOperation dan silmeye gerek yok cunku
        # onu grupta hallediyoruz.

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setParentItem(self.eskiParentItem)
        self.item.setPos(self.eskiPos)
        self.item.setRotation(self.item.rotation() - self.eskiParentRot)
        # if self.eskiParentItem:
        if self.eskiParentItem.type() == shared.GROUP_ITEM_TYPE:
            self.eskiParentItem.parentedWithParentOperation.append(self.item)
        self.item.scene().unGroupedRootItems.discard(self.item)


########################################################################
class UndoableSetFont(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, font, parent=None):
        super(UndoableSetFont, self).__init__(description, parent)
        self.item = item
        self.font = font
        self.eskiFont = item.font()

    # ---------------------------------------------------------------------
    def id(self):
        return 1

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.font = enSonUndo.font
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setFont(self.font)
        self.item.scene().parent().change_font_combobox_value(self.font)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setFont(self.eskiFont)
        self.item.scene().parent().change_font_combobox_value(self.eskiFont)


########################################################################
class UndoableSetFontSizeF(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, fontPointSizeF, parent=None):
        super(UndoableSetFontSizeF, self).__init__(description, parent)
        self.item = item
        self.fontPointSizeF = fontPointSizeF
        self.eskiFontPointSizeF = item.font().pointSizeF()

    # ---------------------------------------------------------------------
    def id(self):
        return 2

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        # TODO: for now this is useless because it is in a macro. and other ones are too,
        # which are called from a macro.
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.fontPointSizeF = enSonUndo.fontPointSizeF
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setFontPointSizeF(self.fontPointSizeF)
        self.item.scene().parent().change_font_point_sizef_spinbox_value(self.fontPointSizeF)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setFontPointSizeF(self.eskiFontPointSizeF)
        self.item.scene().parent().change_font_point_sizef_spinbox_value(self.eskiFontPointSizeF)


########################################################################
class UndoableSetCharacterFormat(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, bicim, parent=None):
        super(UndoableSetCharacterFormat, self).__init__(description, parent)
        self.item = item
        self.bicim = bicim
        self.eski_bicim = item.ver_karakter_bicimi()

    # # ---------------------------------------------------------------------
    # def id(self):
    #     return 3
    #
    # # ---------------------------------------------------------------------
    # def mergeWith(self, enSonUndo):
    #     if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
    #         return False
    #     self.bicim = enSonUndo.bicim
    #     return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.kur_karakter_bicimi(self.bicim)
        self.item.scene().parent().karakter_bicimi_degisti(self.bicim)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.kur_karakter_bicimi(self.eski_bicim)
        self.item.scene().parent().karakter_bicimi_degisti(self.eski_bicim)


########################################################################
class UndoableSetTextAlignment(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, hiza, parent=None):
        super(UndoableSetTextAlignment, self).__init__(description, parent)
        self.item = item
        self.hiza = hiza
        self.eski_hiza = item.ver_yazi_hizasi()

    # # ---------------------------------------------------------------------
    # def id(self):
    #     return 4
    #
    # # ---------------------------------------------------------------------
    # def mergeWith(self, enSonUndo):
    #     if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
    #         return False
    #     self.hiza = enSonUndo.hiza
    #     return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.kur_yazi_hizasi(self.hiza)
        self.item.scene().parent().yazi_hizalama_degisti(self.hiza)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.kur_yazi_hizasi(self.eski_hiza)
        self.item.scene().parent().yazi_hizalama_degisti(self.eski_hiza)


########################################################################
class UndoableResizeBaseItem(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, yeniRect, eskiRect, eskiPos, parent=None):
        super(UndoableResizeBaseItem, self).__init__(description, parent)
        self.item = item
        self.yeniPos = self.item.pos()
        self.yeniRect = yeniRect
        self.eskiPos = eskiPos
        self.eskiRect = eskiRect

    # ---------------------------------------------------------------------
    # def id(self):
    #     return 5
    #
    # # ---------------------------------------------------------------------
    # def mergeWith(self, enSonUndo):
    #     if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
    #         return False
    #
    #     self.yeniRect = enSonUndo.yeniRect
    #     return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setPos(self.yeniPos)
        self.item.setRect(self.yeniRect)
        # if not self.item.type() == shared.TEXT_ITEM_TYPE:
        #     self.item.repositionChildItems(self.eskiPos - self.yeniPos)
        self.item.update_resize_handles()
        self.item.scene().parent().change_transform_box_values(self.item)
        if self.item.type() == shared.IMAGE_ITEM_TYPE:
            self.item.reload_image_after_scale()

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setPos(self.eskiPos)
        self.item.setRect(self.eskiRect)
        # if not self.item.type() == shared.TEXT_ITEM_TYPE:
        #     self.item.repositionChildItems(self.yeniPos - self.eskiPos)
        self.item.update_resize_handles()
        self.item.scene().parent().change_transform_box_values(self.item)
        if self.item.type() == shared.IMAGE_ITEM_TYPE:
            self.item.reload_image_after_scale()


########################################################################
class UndoableResizeLineItem(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, yeniLine, eskiLine, eskiPos, degisenNokta=None, parent=None):
        super(UndoableResizeLineItem, self).__init__(description, parent)
        self.cizgiNesnesi = item
        self.scene = item.scene()
        self.yeniPos = item.pos()
        self.yeniLine = yeniLine
        self.eskiPos = eskiPos
        self.eskiLine = eskiLine
        self.degisenNokta = degisenNokta

        self.p1_in_baglandigi_eski_nesne = None
        self.p2_in_baglandigi_eski_nesne = None
        for baglanmis_nesne_kimlik, nokta in self.cizgiNesnesi.baglanmis_nesneler.items():  # dict.items()
            baglanmis_nesne = self.scene._kimlik_nesne_sozluk[baglanmis_nesne_kimlik]
            if 1 == nokta:
                self.p1_in_baglandigi_eski_nesne = baglanmis_nesne
            if 2 == nokta:
                self.p2_in_baglandigi_eski_nesne = baglanmis_nesne

    # ---------------------------------------------------------------------
    # def id(self):
    #     return 6
    #
    # # ---------------------------------------------------------------------
    # def mergeWith(self, enSonUndo):
    #     if not enSonUndo.id() == self.id() or self.cizgiNesnesi is not enSonUndo.cizgiNesnesi:
    #         return False
    #
    #     self.yeniRect = enSonUndo.yeniRect
    #     return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.cizgiNesnesi.setPos(self.yeniPos)
        self.cizgiNesnesi.setLine(self.yeniLine)
        self.cizgiNesnesi.repositionChildItems(self.eskiPos - self.yeniPos)
        self.cizgiNesnesi.update_resize_handles()
        # self.scene.parent().change_transform_box_values(self.cizgiNesnesi)

        if self.degisenNokta == 1:
            p1_scene_pos = self.cizgiNesnesi.mapToScene(self.yeniLine.p1())
            ustuneOkCizilenItemList_p1 = self.scene.items(p1_scene_pos,
                                                          deviceTransform=self.scene.views()[0].transform())
            # bazen veya (eskiden?) cizilen ok da listelenebiliyor(du).
            if self.cizgiNesnesi in ustuneOkCizilenItemList_p1:
                ustuneOkCizilenItemList_p1.remove(self.cizgiNesnesi)
            if ustuneOkCizilenItemList_p1:
                p1_in_baglanacagi_yeni_nesne = ustuneOkCizilenItemList_p1[0]
                enustGrup = p1_in_baglanacagi_yeni_nesne.varsaEnUsttekiGrubuGetir()
                if enustGrup:
                    p1_in_baglanacagi_yeni_nesne = enustGrup

                if self.p1_in_baglandigi_eski_nesne:  # noktayi bosluktan yeni nesnenin ustune tasiyor da olabiliriz 
                    if not p1_in_baglanacagi_yeni_nesne._kim == self.p1_in_baglandigi_eski_nesne._kim:
                        self.p1_in_baglandigi_eski_nesne.ok_sil(self.cizgiNesnesi)
                p1_in_baglanacagi_yeni_nesne.ok_ekle(self.cizgiNesnesi, p1_scene_pos, 1)
            else:
                # eski nesne uzerinden bosluga tasidik noktayi ve hala eski nesneye bagli, pozisyon ayarlamasi yapiliyor
                # bir benzeri UndoableMove() da var. Ok nesne olarak tasinirsa ve bagli oldugu nesneler varsa
                # bagli oldugu noktalarin pozisyon ayarlamasi yapilior (offset)
                if self.p1_in_baglandigi_eski_nesne:
                    self.p1_in_baglandigi_eski_nesne.ok_ekle(self.cizgiNesnesi, p1_scene_pos, 1)

        elif self.degisenNokta == 2:
            p2_scene_pos = self.cizgiNesnesi.mapToScene(self.yeniLine.p2())
            ustuneOkCizilenItemList_p2 = self.scene.items(p2_scene_pos,
                                                          deviceTransform=self.scene.views()[0].transform())
            # bazen veya (eskiden?) cizilen ok da listelenebiliyor(du).
            if self.cizgiNesnesi in ustuneOkCizilenItemList_p2:
                ustuneOkCizilenItemList_p2.remove(self.cizgiNesnesi)
            if ustuneOkCizilenItemList_p2:
                p2_in_baglanacagi_yeni_nesne = ustuneOkCizilenItemList_p2[0]
                enustGrup = p2_in_baglanacagi_yeni_nesne.varsaEnUsttekiGrubuGetir()
                if enustGrup:
                    p2_in_baglanacagi_yeni_nesne = enustGrup

                if self.p2_in_baglandigi_eski_nesne:  # noktayi bosluktan yeni nesnenin ustune tasiyor da olabiliriz
                    if not p2_in_baglanacagi_yeni_nesne._kim == self.p2_in_baglandigi_eski_nesne._kim:
                        self.p2_in_baglandigi_eski_nesne.ok_sil(self.cizgiNesnesi)
                p2_in_baglanacagi_yeni_nesne.ok_ekle(self.cizgiNesnesi, p2_scene_pos, 2)
            else:
                # eski nesne uzerinden bosluga tasidik noktayi ve hala eski nesneye bagli, pozisyon ayarlamasi yapiliyor
                # bir benzeri UndoableMove() da var. Ok nesne olarak tasinirsa ve bagli oldugu nesneler varsa
                # bagli oldugu noktalarin pozisyon ayarlamasi yapilior (offset)
                if self.p2_in_baglandigi_eski_nesne:
                    self.p2_in_baglandigi_eski_nesne.ok_ekle(self.cizgiNesnesi, p2_scene_pos, 2)
        # else:
        #     print(self.degisenNokta)

    # ---------------------------------------------------------------------
    def undo(self):
        self.cizgiNesnesi.setPos(self.eskiPos)
        self.cizgiNesnesi.setLine(self.eskiLine)
        self.cizgiNesnesi.repositionChildItems(self.yeniPos - self.eskiPos)
        self.cizgiNesnesi.update_resize_handles()
        # self.scene.parent().change_transform_box_values(self.cizgiNesnesi)

        if self.degisenNokta == 1:
            p1_scene_pos = self.cizgiNesnesi.mapToScene(self.eskiLine.p1())
            ustuneOkCizilenItemList_p1 = self.scene.items(p1_scene_pos,
                                                          deviceTransform=self.scene.views()[0].transform())
            # bazen veya (eskiden?) cizilen ok da listelenebiliyor(du).
            if self.cizgiNesnesi in ustuneOkCizilenItemList_p1:
                ustuneOkCizilenItemList_p1.remove(self.cizgiNesnesi)
            if ustuneOkCizilenItemList_p1:
                p1_in_baglanacagi_yeni_nesne = ustuneOkCizilenItemList_p1[0]
                enustGrup = p1_in_baglanacagi_yeni_nesne.varsaEnUsttekiGrubuGetir()
                if enustGrup:
                    p1_in_baglanacagi_yeni_nesne = enustGrup

                if self.p1_in_baglandigi_eski_nesne:  # noktayi bosluktan yeni nesnenin ustune tasiyor da olabiliriz
                    if not p1_in_baglanacagi_yeni_nesne._kim == self.p1_in_baglandigi_eski_nesne._kim:
                        self.p1_in_baglandigi_eski_nesne.ok_sil(self.cizgiNesnesi)
                p1_in_baglanacagi_yeni_nesne.ok_ekle(self.cizgiNesnesi, p1_scene_pos, 1)
            else:
                # eski nesne uzerinden bosluga tasidik noktayi ve hala eski nesneye bagli, pozisyon ayarlamasi yapiliyor
                # bir benzeri UndoableMove() da var. Ok nesne olarak tasinirsa ve bagli oldugu nesneler varsa
                # bagli oldugu noktalarin pozisyon ayarlamasi yapilior (offset)
                if self.p1_in_baglandigi_eski_nesne:
                    self.p1_in_baglandigi_eski_nesne.ok_ekle(self.cizgiNesnesi, p1_scene_pos, 1)

        elif self.degisenNokta == 2:
            p2_scene_pos = self.cizgiNesnesi.mapToScene(self.eskiLine.p2())
            ustuneOkCizilenItemList_p2 = self.scene.items(p2_scene_pos,
                                                          deviceTransform=self.scene.views()[0].transform())
            # bazen veya (eskiden?) cizilen ok da listelenebiliyor(du).
            if self.cizgiNesnesi in ustuneOkCizilenItemList_p2:
                ustuneOkCizilenItemList_p2.remove(self.cizgiNesnesi)
            if ustuneOkCizilenItemList_p2:
                p2_in_baglanacagi_yeni_nesne = ustuneOkCizilenItemList_p2[0]
                enustGrup = p2_in_baglanacagi_yeni_nesne.varsaEnUsttekiGrubuGetir()
                if enustGrup:
                    p2_in_baglanacagi_yeni_nesne = enustGrup

                if self.p2_in_baglandigi_eski_nesne:  # noktayi bosluktan yeni nesnenin ustune tasiyor da olabiliriz
                    if not p2_in_baglanacagi_yeni_nesne._kim == self.p2_in_baglandigi_eski_nesne._kim:
                        self.p2_in_baglandigi_eski_nesne.ok_sil(self.cizgiNesnesi)
                p2_in_baglanacagi_yeni_nesne.ok_ekle(self.cizgiNesnesi, p2_scene_pos, 2)
            else:
                # eski nesne uzerinden bosluga tasidik noktayi ve hala eski nesneye bagli, pozisyon ayarlamasi yapiliyor
                # bir benzeri UndoableMove() da var. Ok nesne olarak tasinirsa ve bagli oldugu nesneler varsa
                # bagli oldugu noktalarin pozisyon ayarlamasi yapilior (offset)
                if self.p2_in_baglandigi_eski_nesne:
                    self.p2_in_baglandigi_eski_nesne.ok_ekle(self.cizgiNesnesi, p2_scene_pos, 2)


########################################################################
class UndoableResizeGroupItem(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, eskiRect, yeniRect, eskiPos, yeniPos, scaleFactorX, scaleFactorY, parent=None):
        super(UndoableResizeGroupItem, self).__init__(description, parent)
        self.item = item
        # self.eskiRect = item._rect
        self.eskiRect = eskiRect
        self.yeniRect = yeniRect
        self.scaleFactorX = scaleFactorX
        self.scaleFactorY = scaleFactorY

        self.eskiPos = eskiPos
        self.yeniPos = yeniPos

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setPos(self.yeniPos)
        self.yeniRect.moveTo(0, 0)
        self.item.setRect(self.yeniRect)
        # Dikkat: Demiyoruz ki; burda gerek yok zaten mouseMoveda bu islem hallediliyor
        # geri-al ileri-al yapılırsa ihtiyac olacak
        shared._scaleChildItemsByResizing(self.item, self.scaleFactorX, self.scaleFactorY, True)
        self.item.update_resize_handles()
        self.item.scene().parent().change_transform_box_values(self.item)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setPos(self.eskiPos)
        self.item.setRect(self.eskiRect)
        shared._scaleChildItemsByResizing(self.item, 1 / self.scaleFactorX, 1 / self.scaleFactorY, True)
        self.item.update_resize_handles()
        self.item.scene().parent().change_transform_box_values(self.item)


########################################################################
class UndoableResizePathItem(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, scaledPath, yeniPos, parent=None):
        super(UndoableResizePathItem, self).__init__(description, parent)
        self.item = item
        self.eskiPath = item.path()
        self.eskiPos = item.pos()
        self.yeniPath = scaledPath
        self.yeniPos = yeniPos

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setPath(self.yeniPath)
        self.item.setPos(self.yeniPos)
        self.item.update_painter_text_rect()
        self.item.scene().parent().change_transform_box_values(self.item)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setPath(self.eskiPath)
        self.item.setPos(self.eskiPos)
        self.item.update_painter_text_rect()
        self.item.scene().parent().change_transform_box_values(self.item)


########################################################################
class UndoableScaleTextItemByResizing(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, scaleFactor, fontPointSizeF, parent=None):
        super(UndoableScaleTextItemByResizing, self).__init__(description, parent)
        self.item = item
        self.scaleFactor = scaleFactor
        self.fontPointSizeF = fontPointSizeF
        self.eskiFontPointSizeF = self.item.fontPointSizeF()

    # ---------------------------------------------------------------------
    def id(self):
        return 7

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False

        self.scaleFactor *= enSonUndo.scaleFactor  # dikkat *=
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setFontPointSizeF(self.fontPointSizeF)
        self.item.scene().parent().change_font_point_sizef_spinbox_value(self.fontPointSizeF)
        shared._scaleChildItemsByResizing(self.item, self.scaleFactor)
        self.item.update_resize_handles()
        self.item.scene().parent().change_transform_box_values(self.item)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setFontPointSizeF(self.eskiFontPointSizeF)
        self.item.scene().parent().change_font_point_sizef_spinbox_value(self.eskiFontPointSizeF)
        shared._scaleChildItemsByResizing(self.item, 1 / self.scaleFactor)
        self.item.update_resize_handles()
        self.item.scene().parent().change_transform_box_values(self.item)


########################################################################
class UndoableScaleGroupItemByResizing(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, yeniRect, scaleFactor, yeniPos, parent=None):
        super(UndoableScaleGroupItemByResizing, self).__init__(description, parent)
        self.item = item
        self.eskiRect = item._rect
        self.yeniRect = yeniRect
        self.scaleFactor = scaleFactor
        self.yeniPos = yeniPos
        self.eskiPos = item.pos()

    # ---------------------------------------------------------------------
    def id(self):
        return 8

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False

        self.yeniRect = enSonUndo.yeniRect
        self.yeniPos = enSonUndo.yeniPos
        self.scaleFactor *= enSonUndo.scaleFactor  # dikkat *=
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setRect(self.yeniRect)
        self.item.setPos(self.yeniPos)
        shared._scaleChildItemsByResizing(self.item, self.scaleFactor)
        self.item.scene().parent().change_transform_box_values(self.item)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setRect(self.eskiRect)
        self.item.setPos(self.eskiPos)
        shared._scaleChildItemsByResizing(self.item, 1 / self.scaleFactor)
        self.item.scene().parent().change_transform_box_values(self.item)


########################################################################
class UndoableScaleBaseItemByResizing(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, yeniRect, scaleFactor, yeniPos, parent=None):
        super(UndoableScaleBaseItemByResizing, self).__init__(description, parent)
        self.item = item
        self.eskiRect = item.rect()
        self.yeniRect = yeniRect
        self.scaleFactor = scaleFactor
        self.eskiPos = item.pos()
        self.yeniPos = yeniPos

    # ---------------------------------------------------------------------
    def id(self):
        return 9

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False

        self.yeniRect = enSonUndo.yeniRect
        self.yeniPos = enSonUndo.yeniPos
        self.scaleFactor *= enSonUndo.scaleFactor  # dikkat *=
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setRect(self.yeniRect)
        self.item.setPos(self.yeniPos)
        shared._scaleChildItemsByResizing(self.item, self.scaleFactor)
        self.item.update_resize_handles()
        self.item.scene().parent().change_transform_box_values(self.item)
        self.item.update_painter_text_rect()
        if self.item.type() == shared.IMAGE_ITEM_TYPE:
            self.item.reload_image_after_scale()

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setRect(self.eskiRect)
        self.item.setPos(self.eskiPos)
        shared._scaleChildItemsByResizing(self.item, 1 / self.scaleFactor)
        self.item.update_resize_handles()
        self.item.scene().parent().change_transform_box_values(self.item)
        self.item.update_painter_text_rect()
        if self.item.type() == shared.IMAGE_ITEM_TYPE:
            self.item.reload_image_after_scale()


########################################################################
class UndoableScalePathItemByScalingPath(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, path, scaleFactor, parent=None):
        super(UndoableScalePathItemByScalingPath, self).__init__(description, parent)
        self.item = item
        self.path = path
        self.eskiPath = item.path()
        self.scaleFactor = scaleFactor

    # ---------------------------------------------------------------------
    def id(self):
        return 10

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.path = enSonUndo.path
        self.scaleFactor *= enSonUndo.scaleFactor  # dikkat *=
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setPath(self.path)
        shared._scaleChildItemsByResizing(self.item, self.scaleFactor)
        self.item.update_painter_text_rect()
        self.item.scene().parent().change_transform_box_values(self.item)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setPath(self.eskiPath)
        shared._scaleChildItemsByResizing(self.item, 1 / self.scaleFactor)
        self.item.update_painter_text_rect()
        self.item.scene().parent().change_transform_box_values(self.item)


########################################################################
class UndoableScaleLineItemByScalingLine(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, line, scaleFactor, parent=None):
        super(UndoableScaleLineItemByScalingLine, self).__init__(description, parent)
        self.item = item
        self.eskiLine = item.line()
        self.line = line
        self.scaleFactor = scaleFactor

    # ---------------------------------------------------------------------
    def id(self):
        return 11

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.line = enSonUndo.line
        self.scaleFactor *= enSonUndo.scaleFactor  # dikkat *=
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setLine(self.line)
        shared._scaleChildItemsByResizing(self.item, self.scaleFactor)
        self.item.update_painter_text_rect()
        self.item.scene().parent().change_transform_box_values(self.item)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setLine(self.eskiLine)
        shared._scaleChildItemsByResizing(self.item, self.scaleFactor)
        self.item.update_painter_text_rect()
        self.item.scene().parent().change_transform_box_values(self.item)


########################################################################
class UndoableRotate(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, rotation, parent=None):
        super(UndoableRotate, self).__init__(description, parent)
        self.item = item
        self.rotation = rotation % 360
        self.eskiRotation = item.rotation() % 360

    # ---------------------------------------------------------------------
    def id(self):
        return 12

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.rotation = enSonUndo.rotation
        # self.eskiRotation = enSonUndo.eskiRotation
        # self.rotation += enSonUndo.rotation
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setRotation(self.rotation)
        self.item.scene().parent().itemRotationSBox_tbar.setValue(self.rotation)
        self.item.scene().parent().itemRotationSBox_nesnedw.setValue(self.rotation)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setRotation(self.eskiRotation)
        self.item.scene().parent().itemRotationSBox_tbar.setValue(self.eskiRotation)
        self.item.scene().parent().itemRotationSBox_nesnedw.setValue(self.eskiRotation)


########################################################################
class UndoableRotateWithOffset(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, rotation, parent=None):
        super(UndoableRotateWithOffset, self).__init__(description, parent)
        self.item = item
        self.rotation = rotation % 360
        self.eskiRotation = item.rotation() % 360

    # ---------------------------------------------------------------------
    def id(self):
        return 13

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.rotation = enSonUndo.rotation
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.rotateWithOffset(self.rotation)
        self.item.scene().parent().itemRotationSBox_tbar.setValue(self.rotation)
        self.item.scene().parent().itemRotationSBox_nesnedw.setValue(self.rotation)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.rotateWithOffset(self.eskiRotation)
        self.item.scene().parent().itemRotationSBox_tbar.setValue(self.eskiRotation)
        self.item.scene().parent().itemRotationSBox_nesnedw.setValue(self.eskiRotation)


########################################################################
class UndoableSetZValue(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, zValue, parent=None):
        super(UndoableSetZValue, self).__init__(description, parent)
        self.item = item
        self.zValue = zValue
        self.eskiZValue = item.zValue()

    # ---------------------------------------------------------------------
    def id(self):
        return 14

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.zValue is not enSonUndo.zValue:
            return False
        self.zValue = enSonUndo.zValue
        # self.eskiRotation = enSonUndo.eskiRotation
        # self.rotation += enSonUndo.rotation
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setZValue(self.zValue)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setZValue(self.eskiZValue)


########################################################################
class UndoableSetLineCapStyle(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, capStyle, parent=None):
        super(UndoableSetLineCapStyle, self).__init__(description, parent)
        self.item = item
        self.capStyle = capStyle
        self.eskiCapStyle = item._pen.capStyle()

    # ---------------------------------------------------------------------
    def id(self):
        return 15

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.capStyle = enSonUndo.capStyle
        # self.eskiRotation = enSonUndo.eskiRotation
        # self.rotation += enSonUndo.rotation
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item._pen.setCapStyle(self.capStyle)
        self.item.update()

    # ---------------------------------------------------------------------
    def undo(self):
        self.item._pen.setCapStyle(self.eskiCapStyle)
        self.item.update()


########################################################################
class UndoableSetLineJoinStyle(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, joinStyle, parent=None):
        super(UndoableSetLineJoinStyle, self).__init__(description, parent)
        self.item = item
        self.joinStyle = joinStyle
        self.eskiJoinStyle = item._pen.joinStyle()

    # ---------------------------------------------------------------------
    def id(self):
        return 16

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.joinStyle = enSonUndo.joinStyle
        # self.eskiRotation = enSonUndo.eskiRotation
        # self.rotation += enSonUndo.rotation
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item._pen.setJoinStyle(self.joinStyle)
        self.item.update()

    # ---------------------------------------------------------------------
    def undo(self):
        self.item._pen.setJoinStyle(self.eskiJoinStyle)
        self.item.update()


########################################################################
class UndoableSetLineStyle(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, lineStyle, parent=None):
        super(UndoableSetLineStyle, self).__init__(description, parent)
        self.item = item
        self.lineStyle = lineStyle
        self.eskiLineStyle = item._pen.style()

    # ---------------------------------------------------------------------
    def id(self):
        return 17

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.lineStyle = enSonUndo.lineStyle
        # self.eskiRotation = enSonUndo.eskiRotation
        # self.rotation += enSonUndo.rotation
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item._pen.setStyle(self.lineStyle)
        self.item.update()

    # ---------------------------------------------------------------------
    def undo(self):
        self.item._pen.setStyle(self.eskiLineStyle)
        self.item.update()


########################################################################
class UndoableSetLineWidthF(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, widthF, parent=None):
        super(UndoableSetLineWidthF, self).__init__(description, parent)
        self.item = item
        self.widthF = widthF
        self.eskiWidthF = item._pen.widthF()

    # ---------------------------------------------------------------------
    def id(self):
        return 18

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.widthF = enSonUndo.widthF
        # self.eskiRotation = enSonUndo.eskiRotation
        # self.rotation += enSonUndo.rotation
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setCizgiKalinligi(self.widthF)
        self.item.scene().parent().change_line_widthF(self.widthF)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setCizgiKalinligi(self.eskiWidthF)
        self.item.scene().parent().change_line_widthF(self.eskiWidthF)


########################################################################
class UndoableSetLineColor(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, color, renkSecicidenMi, parent=None):
        super(UndoableSetLineColor, self).__init__(description, parent)
        self.item = item
        self.color = color
        self.eskiColor = item.cizgiRengi
        self.renkSecicidenMi = renkSecicidenMi

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setCizgiRengi(self.color)
        if self.item.isSelected():
            self.item.scene().parent().degistir_cizgi_rengi_ikonu(self.color, nesne_arkaplan_ikonu_guncelle=True,
                                                                  renkSecicidenMi=self.renkSecicidenMi)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setCizgiRengi(self.eskiColor)
        if self.item.isSelected():
            self.item.scene().parent().degistir_cizgi_rengi_ikonu(self.eskiColor, nesne_arkaplan_ikonu_guncelle=True,
                                                                  renkSecicidenMi=self.renkSecicidenMi)


########################################################################
class UndoableSetTextColor(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, color, renkSecicidenMi, parent=None):
        super(UndoableSetTextColor, self).__init__(description, parent)
        self.item = item
        self.color = color
        self.eskiColor = item.yaziRengi
        self.renkSecicidenMi = renkSecicidenMi
        # if item.type() == shared.TEXT_ITEM_TYPE:
        #     self.eskiColor = item.defaultTextColor()
        #     # self.setText("change text color")
        # else:
        #     self.eskiColor = item._pen.color()

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setYaziRengi(self.color)
        if self.item.isSelected():
            self.item.scene().parent().degistir_yazi_rengi_ikonu(self.color, nesne_arkaplan_ikonu_guncelle=True,
                                                                 renkSecicidenMi=self.renkSecicidenMi)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setYaziRengi(self.eskiColor)
        if self.item.isSelected():
            self.item.scene().parent().degistir_yazi_rengi_ikonu(self.eskiColor, nesne_arkaplan_ikonu_guncelle=True,
                                                                 renkSecicidenMi=self.renkSecicidenMi)


########################################################################
class UndoableSetLineColorAlpha(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, color, parent=None):
        super(UndoableSetLineColorAlpha, self).__init__(description, parent)
        self.item = item
        self.color = color
        self.eskiColor = item.cizgiRengi
        # if item.type() == shared.TEXT_ITEM_TYPE:
        #     self.eskiColor = item.defaultTextColor()
        # else:
        #     self.eskiColor = item._pen.color()
        #     if self.item.type() == shared.IMAGE_ITEM_TYPE:
        #         self.setText("change item's text alpha")

    # ---------------------------------------------------------------------
    def id(self):
        return 19

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.color = enSonUndo.color
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setCizgiRengi(self.color)
        if self.item.isSelected():
            self.item.scene().parent().degistir_cizgi_rengi_ikonu(self.color, nesne_arkaplan_ikonu_guncelle=True)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setCizgiRengi(self.eskiColor)
        if self.item.isSelected():
            self.item.scene().parent().degistir_cizgi_rengi_ikonu(self.eskiColor, nesne_arkaplan_ikonu_guncelle=True)


########################################################################
class UndoableSetTextColorAlpha(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, color, parent=None):
        super(UndoableSetTextColorAlpha, self).__init__(description, parent)
        self.item = item
        self.color = color
        self.eskiColor = item.yaziRengi
        # if item.type() == shared.TEXT_ITEM_TYPE:
        #     self.eskiColor = item.defaultTextColor()
        # else:
        #     self.eskiColor = item._pen.color()
        #     if self.item.type() == shared.IMAGE_ITEM_TYPE:
        #         self.setText("change item's text alpha")

    # ---------------------------------------------------------------------
    def id(self):
        return 20

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.color = enSonUndo.color
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setYaziRengi(self.color)
        if self.item.isSelected():
            self.item.scene().parent().degistir_yazi_rengi_ikonu(self.color, nesne_arkaplan_ikonu_guncelle=True)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setYaziRengi(self.eskiColor)
        if self.item.isSelected():
            self.item.scene().parent().degistir_yazi_rengi_ikonu(self.eskiColor, nesne_arkaplan_ikonu_guncelle=True)


########################################################################
class UndoableSetItemBackgroundColor(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, color, renkSecicidenMi, parent=None):
        super(UndoableSetItemBackgroundColor, self).__init__(description, parent)
        self.item = item
        self.color = color
        self.eskiColor = item.arkaPlanRengi
        self.renkSecicidenMi = renkSecicidenMi

    # # ---------------------------------------------------------------------
    # def id(self):
    #     return 21
    #
    # # ---------------------------------------------------------------------
    # def mergeWith(self, enSonUndo):
    #     if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
    #         return False
    #     self.color = enSonUndo.color
    #     return True

    # # ---------------------------------------------------------------------
    # def mergeWithh(self, enSonUndo):
    #     if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
    #         return False
    #     if self.onizleme_mi:
    #         self.color = enSonUndo.color
    #         return True
    #     else:
    #         return False
    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setArkaPlanRengi(self.color)
        if self.item.isSelected():
            self.item.scene().parent().degistir_nesne_arkaplan_rengi_ikonu(self.color, self.item.yaziRengi,
                                                                           self.item.cizgiRengi, self.renkSecicidenMi)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setArkaPlanRengi(self.eskiColor)
        if self.item.isSelected():
            self.item.scene().parent().degistir_nesne_arkaplan_rengi_ikonu(self.eskiColor, self.item.yaziRengi,
                                                                           self.item.cizgiRengi, self.renkSecicidenMi)


########################################################################
class UndoableSetItemBackgroundColorAlpha(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, color, parent=None):
        super(UndoableSetItemBackgroundColorAlpha, self).__init__(description, parent)
        self.item = item
        self.color = color
        self.eskiColor = item.arkaPlanRengi
        if self.item.type() == shared.IMAGE_ITEM_TYPE:
            self.setText("change item's text background alpha")

    # ---------------------------------------------------------------------
    def id(self):
        return 22

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.color = enSonUndo.color
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setArkaPlanRengi(self.color)
        if self.item.isSelected():
            self.item.scene().parent().degistir_nesne_arkaplan_rengi_ikonu(self.color, self.item.yaziRengi,
                                                                           self.item.cizgiRengi)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setArkaPlanRengi(self.eskiColor)
        if self.item.isSelected():
            self.item.scene().parent().degistir_nesne_arkaplan_rengi_ikonu(self.eskiColor, self.item.yaziRengi,
                                                                           self.item.cizgiRengi)


########################################################################
class UndoableStilAdiDegistir(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, nesne, yeni_isim, parent=None):
        super(UndoableStilAdiDegistir, self).__init__(description, parent)

        self.nesne = nesne
        self.eski_isim = nesne.text()
        self.yeni_isim = yeni_isim

    # ---------------------------------------------------------------------
    def redo(self):
        self.nesne.setText(self.yeni_isim)

    # ---------------------------------------------------------------------
    def undo(self):
        self.nesne.setText(self.eski_isim)


########################################################################
class UndoableStiliUygula(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, eskiPen, yeniPen, yaziRengi, eskiYaziRengi, cizgiRengi, eskiCizgiRengi,
                 eskiArkaPlanRengi, yeniArkaPlanRengi, eskiFont, yeniFont,
                 scene, parent=None):
        super(UndoableStiliUygula, self).__init__(description, parent)
        self.font = yeniFont
        self.eskiFont = eskiFont
        self.pen = yeniPen
        self.eskiPen = eskiPen
        self.cizgiRengi = cizgiRengi
        self.eskiCizgiRengi = eskiCizgiRengi
        self.yaziRengi = yaziRengi
        self.eskiYaziRengi = eskiYaziRengi
        self.eskiArkaPlanRengi = eskiArkaPlanRengi
        self.yeniArkaPlanRengi = yeniArkaPlanRengi
        # self.cizgiKalinligi = yeniPen.widthF()
        # self.eskiCizgiKalinligi = eskiPen.widthF()
        self.scene = scene

    # # ---------------------------------------------------------------------
    # def id(self):
    #     return 23

    # # ---------------------------------------------------------------------
    # def mergeWith(self, enSonUndo):
    #     if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
    #         return False
    #     self.font = enSonUndo.font
    #     self.pen = enSonUndo.pen
    #     self.brush = enSonUndo.brush
    #     self.cizgiKalinligi = enSonUndo.cizgiKalinligi
    #     # self.eskiRotation = enSonUndo.eskiRotation
    #     # self.rotation += enSonUndo.rotation
    #     return True

    # ---------------------------------------------------------------------
    def redo(self):
        # self.scene.parent().currentFont=QFont(self.font)
        self.scene.aktifArac.yaziTipi = self.font

        self.scene.aktifArac.kalem = self.pen

        self.scene.aktifArac.yaziRengi = self.yaziRengi
        self.scene.aktifArac.cizgiRengi = self.cizgiRengi
        self.scene.aktifArac.arkaPlanRengi = self.yeniArkaPlanRengi

        self.scene.parent().degistir_yazi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=False)
        self.scene.parent().degistir_cizgi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=False)
        self.scene.parent().degistir_nesne_arkaplan_rengi_ikonu()
        self.scene.parent().change_font_point_sizef_spinbox_value(self.font.pointSizeF())
        self.scene.parent().change_line_style_options(self.pen)
        self.scene.parent().change_font_combobox_value(self.font)

    # ---------------------------------------------------------------------
    def undo(self):
        # self.scene.parent().currentFont=QFont(self.font)
        self.scene.aktifArac.yaziTipi = self.eskiFont

        self.scene.aktifArac.kalem = self.eskiPen

        self.scene.aktifArac.yaziRengi = self.eskiYaziRengi
        self.scene.aktifArac.cizgiRengi = self.eskiCizgiRengi
        self.scene.aktifArac.arkaPlanRengi = self.eskiArkaPlanRengi

        self.scene.parent().degistir_yazi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=False)
        self.scene.parent().degistir_cizgi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=False)
        self.scene.parent().degistir_nesne_arkaplan_rengi_ikonu()
        self.scene.parent().change_font_point_sizef_spinbox_value(self.eskiFont.pointSizeF())
        self.scene.parent().change_line_style_options(self.eskiPen)
        self.scene.parent().change_font_combobox_value(self.eskiFont)


########################################################################
class UndoableStiliNesneyeUygula(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, pen, brush, font, yaziRengi, cizgiRengi, parent=None):
        super(UndoableStiliNesneyeUygula, self).__init__(description, parent)
        self.item = item
        self.font = font
        self.eskiFont = item.font()
        self.pen = pen
        self.eskiPen = item.pen()
        self.brush = brush
        self.eskiBrush = item.brush()
        self.cizgiRengi = cizgiRengi
        self.eskiCizgiRengi = item.cizgiRengi
        self.yaziRengi = yaziRengi
        self.eskiYaziRengi = item.yaziRengi
        self.cizgiKalinligi = pen.widthF()
        self.eskiCizgiKalinligi = item._pen.widthF()

    # ---------------------------------------------------------------------
    def id(self):
        return 24

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.font = enSonUndo.font
        self.pen = enSonUndo.pen
        self.brush = enSonUndo.brush
        self.cizgiKalinligi = enSonUndo.cizgiKalinligi
        self.cizgiRengi = enSonUndo.cizgiRengi
        self.yaziRengi = enSonUndo.yaziRengi
        # self.eskiRotation = enSonUndo.eskiRotation
        # self.rotation += enSonUndo.rotation
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.setPen(self.pen)
        self.item.setCizgiRengi(self.cizgiRengi)
        # self.item.setYaziRengi(self.pen.color())
        self.item.setYaziRengi(self.yaziRengi)
        self.item.setCizgiKalinligi(self.cizgiKalinligi)  # cunku bi kac tane pen var guncellenmesi gereken
        # self.item.setBrush(self.brush)
        self.item.setArkaPlanRengi(self.brush.color())  # also sets brush
        self.item.setFont(self.font)
        # self.item.update()
        if self.item.isSelected():
            self.item.scene().parent().degistir_yazi_rengi_ikonu(self.yaziRengi, nesne_arkaplan_ikonu_guncelle=False)
            self.item.scene().parent().degistir_cizgi_rengi_ikonu(self.cizgiRengi, nesne_arkaplan_ikonu_guncelle=False)
            self.item.scene().parent().degistir_nesne_arkaplan_rengi_ikonu(self.brush.color(), self.yaziRengi,
                                                                           self.cizgiRengi)
            self.item.scene().parent().change_font_point_sizef_spinbox_value(self.font.pointSizeF())
            self.item.scene().parent().change_line_style_options(self.pen)
            self.item.scene().parent().change_font_combobox_value(self.font)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.setPen(self.eskiPen)
        self.item.setCizgiRengi(self.eskiCizgiRengi)
        self.item.setYaziRengi(self.eskiYaziRengi)
        self.item.setCizgiKalinligi(self.eskiCizgiKalinligi)  # cunku bi kac tane pen var guncellenmesi gereken
        # self.item.setBrush(self.eskiBrush)

        self.item.setArkaPlanRengi(self.eskiBrush.color())  # also sets brush
        self.item.setFont(self.eskiFont)

        if self.item.isSelected():
            self.item.scene().parent().degistir_yazi_rengi_ikonu(self.eskiYaziRengi,
                                                                 nesne_arkaplan_ikonu_guncelle=False)
            self.item.scene().parent().degistir_cizgi_rengi_ikonu(self.eskiCizgiRengi,
                                                                  nesne_arkaplan_ikonu_guncelle=False)
            self.item.scene().parent().degistir_nesne_arkaplan_rengi_ikonu(self.eskiBrush.color(), self.eskiYaziRengi,
                                                                           self.eskiCizgiRengi)
            self.item.scene().parent().change_font_point_sizef_spinbox_value(self.eskiFont.pointSizeF())
            self.item.scene().parent().change_line_style_options(self.eskiPen)
            self.item.scene().parent().change_font_combobox_value(self.eskiFont)


########################################################################
class UndoableSetImageOpacity(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, imageOpacity, parent=None):
        super(UndoableSetImageOpacity, self).__init__(description, parent)
        self.item = item
        self.imageOpacity = imageOpacity
        self.eskiImageOpacity = item.imageOpacity

    # ---------------------------------------------------------------------
    def id(self):
        return 25

    # ---------------------------------------------------------------------
    def mergeWith(self, enSonUndo):
        if not enSonUndo.id() == self.id() or self.item is not enSonUndo.item:
            return False
        self.imageOpacity = enSonUndo.imageOpacity
        return True

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.imageOpacity = self.imageOpacity
        self.item.update()

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.imageOpacity = self.eskiImageOpacity
        self.item.update()


########################################################################
class UndoableSetPinStatus(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, value, parent=None):
        """ """
        super(UndoableSetPinStatus, self).__init__(description, parent)

        self.item = item
        self.value = value

    # ---------------------------------------------------------------------
    def undo(self):
        # self.redo()
        self.item.isPinned = not self.value

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.isPinned = self.value


########################################################################
class UndoableItemSetText(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, eskiText, text, parent=None):
        """ """
        super(UndoableItemSetText, self).__init__(description, parent)

        self.item = item
        self.eski_text = eskiText
        self.text = text

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.scene().parent().act_aramayi_temizle()
        self.item.setText(self.text)

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.scene().parent().act_aramayi_temizle()
        self.item.setText(self.eski_text)


########################################################################
class UndoableConvertToPlainText(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, parent=None):
        """ """
        super(UndoableConvertToPlainText, self).__init__(description, parent)

        self.item = item
        self.html = item.toHtml()

    # ---------------------------------------------------------------------
    def redo(self):
        text = self.item.toPlainText()
        self.item.document().clear()
        self.item.setPlainText(text)
        self.item.isPlainText = True

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.document().clear()
        self.item.setHtml(self.html)
        self.item.isPlainText = False


########################################################################
class UndoableItemCustomCommand(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, command, parent=None):
        """ """
        super(UndoableItemCustomCommand, self).__init__(description, parent)

        self.item = item
        self.eski_command = item.command
        self.command = command

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.command = self.command
        self.item.setText(self.command["name"])

    # ---------------------------------------------------------------------
    def undo(self):
        self.item.command = self.eski_command
        self.item.setText(self.eski_command["name"])


########################################################################
class UndoableEmbedImage(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, parent=None):
        """ """
        super(UndoableEmbedImage, self).__init__(description, parent)

        self.item = item
        self.eskiImagePath = item.filePathForSave

        self.copyAlreadyExists = False
        for imgItem in self.item.scene().items():
            if imgItem.type() == shared.IMAGE_ITEM_TYPE:
                if imgItem.isEmbeded:
                    if self.item.originalSourceFilePath == imgItem.originalSourceFilePath:
                        self.yeniImagePath = imgItem.filePathForSave
                        self.copyAlreadyExists = True
                        break
        if not self.copyAlreadyExists:
            # self.yeniImagePath = item.scene().get_unique_path_for_embeded_image()
            self.yeniImagePath = item.scene().get_unique_path_for_embeded_image(os.path.basename(item.filePathForSave))

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.isEmbeded = True
        # TODO: bu copy2 hata dondurmuyor imis.
        # digerleri de metadata korumuyor, burda bi kontrol lazim aslinda.
        # eger kopyalandiysa degistirelim image adresi.
        if not self.copyAlreadyExists:
            shutil.copy2(self.item.filePathForSave, self.yeniImagePath)
        self.item.filePathForSave = self.yeniImagePath

    # ---------------------------------------------------------------------
    def undo(self):
        if not self.copyAlreadyExists:
            try:
                os.remove(self.yeniImagePath)
            except OSError as e:
                self.item.scene().parent().log(
                    'Warning! could not delete embeded image file, '
                    'but image\'s file path succesfully reverted to original path. ( {} )'.format(os.strerror(e.errno)),
                    20000, 3)
        # else:
        #     pass
        # finally:
        self.item.isEmbeded = False
        self.item.filePathForSave = self.eskiImagePath


########################################################################
class UndoableEmbedVideo(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, parent=None):
        """ """
        super(UndoableEmbedVideo, self).__init__(description, parent)

        self.item = item
        self.eskiVideoPath = item.filePathForSave

        self.copyAlreadyExists = False
        for videoItem in self.item.scene().items():
            if videoItem.type() == shared.VIDEO_ITEM_TYPE:
                if videoItem.isEmbeded:
                    if self.item.originalSourceFilePath == videoItem.originalSourceFilePath:
                        self.yeniVideoPath = videoItem.filePathForSave
                        self.copyAlreadyExists = True
                        break
        if not self.copyAlreadyExists:
            self.yeniVideoPath = item.scene().get_unique_path_for_embeded_video(os.path.basename(item.filePathForSave))

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.isEmbeded = True
        # TODO: bu copy2 hata dondurmuyor imis.
        # digerleri de metadata korumuyor, burda bi kontrol lazim aslinda.
        # eger kopyalandiysa degistirelim image adresi.
        if not self.copyAlreadyExists:
            shutil.copy2(self.item.filePathForSave, self.yeniVideoPath)
        self.item.filePathForSave = self.yeniVideoPath

    # ---------------------------------------------------------------------
    def undo(self):
        if not self.copyAlreadyExists:
            try:
                os.remove(self.yeniVideoPath)
            except OSError as e:
                self.item.scene().parent().log(
                    'Warning! could not delete embeded video file, '
                    'but video\'s file path succesfully reverted to original path. ( {} )'.format(os.strerror(e.errno)),
                    20000, 3)
        # else:
        #     pass
        # finally:
        self.item.isEmbeded = False
        self.item.filePathForSave = self.eskiVideoPath


########################################################################
class UndoableEmbedFile(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, item, parent=None):
        """ """
        super(UndoableEmbedFile, self).__init__(description, parent)

        self.item = item
        self.eskiFilePath = item.filePathForSave

        self.copyAlreadyExists = False
        for fileItem in self.item.scene().items():
            if fileItem.type() == shared.DOSYA_ITEM_TYPE:
                if fileItem.isEmbeded:
                    if self.item.originalSourceFilePath == fileItem.originalSourceFilePath:
                        self.yeniFilePath = fileItem.filePathForSave
                        self.copyAlreadyExists = True
                        break
        if not self.copyAlreadyExists:
            self.yeniFilePath = item.scene().get_unique_path_for_embeded_file(os.path.basename(item.filePathForSave))

    # ---------------------------------------------------------------------
    def redo(self):
        self.item.isEmbeded = True
        # TODO: bu copy2 hata dondurmuyor imis.
        # digerleri de metadata korumuyor, burda bi kontrol lazim aslinda.
        # eger kopyalandiysa degistirelim image adresi.
        if not self.copyAlreadyExists:
            shutil.copy2(self.item.filePathForSave, self.yeniFilePath)
        self.item.filePathForSave = self.yeniFilePath

    # ---------------------------------------------------------------------
    def undo(self):
        if not self.copyAlreadyExists:
            try:
                os.remove(self.yeniFilePath)
            except OSError as e:
                self.item.scene().parent().log(
                    'Warning! could not delete embeded file, '
                    'but file\'s file path succesfully reverted to original path. ( {} )'.format(os.strerror(e.errno)),
                    20000, 3)
        # else:
        #     pass
        # finally:
        self.item.isEmbeded = False
        self.item.filePathForSave = self.eskiFilePath


########################################################################
class UndoableSetSceneBackgroundBrush(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, view, color, parent=None):
        super(UndoableSetSceneBackgroundBrush, self).__init__(description, parent)
        self.view = view
        self.color = color
        self.eskiColor = self.view.backgroundBrush().color()

    # ---------------------------------------------------------------------
    def redo(self):
        self.view.setBackgroundBrush(self.color)

    # ---------------------------------------------------------------------
    def undo(self):
        self.view.setBackgroundBrush(self.eskiColor)


########################################################################
class UndoableSetSceneBackgroundImage(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, view, imagePath, parent=None):
        super(UndoableSetSceneBackgroundImage, self).__init__(description, parent)
        self.view = view
        self.imagePath = imagePath
        self.eskiImagePath = view.backgroundImagePath
        self.eskiEmbedDurumu = view.backgroundImagePathIsEmbeded

    # ---------------------------------------------------------------------
    def redo(self):
        self.view.set_background_image(self.imagePath)
        self.view.backgroundImagePathIsEmbeded = False

        # if not os.path.exists(self.imagePath):
        #     self.view.parent().log("Can not undo, %s does not exist or could not be read "
        #                             % self.imagePath, 5000, 2)

    # ---------------------------------------------------------------------
    def undo(self):
        self.view.set_background_image(self.eskiImagePath)
        self.view.backgroundImagePathIsEmbeded = self.eskiEmbedDurumu

        # if not os.path.exists(self.imagePath):
        #     self.view.parent().log("Can not undo, %s does not exist or could not be read "
        #                             % self.eskiImagePath, 5000, 2)


########################################################################
class UndoableEmbedSceneBackgroundImage(QUndoCommand):
    """ """

    # ---------------------------------------------------------------------
    def __init__(self, description, view, parent=None):
        """ """
        super(UndoableEmbedSceneBackgroundImage, self).__init__(description, parent)

        self.view = view
        self.eskiImagePath = view.backgroundImagePath

        self.kopya_var = False
        if os.path.exists(self.eskiImagePath):
            resim_klasor = os.path.join(self.view.scene().tempDirPath, "images")
            for resimAdi in os.listdir(resim_klasor):
                resimAdres = os.path.join(resim_klasor, resimAdi)
                if filecmp.cmp(view.backgroundImagePath, resimAdres, shallow=True):
                    self.kopya_var = True
                    break

        if self.kopya_var:
            self.yeniImagePath = resimAdres
        else:
            self.yeniImagePath = view.scene().get_unique_path_for_embeded_image(
                os.path.basename(view.backgroundImagePath))

    # ---------------------------------------------------------------------
    def redo(self):
        if not self.kopya_var:
            shutil.copy2(self.view.backgroundImagePath, self.yeniImagePath)
        self.view.set_background_image(self.yeniImagePath)
        self.view.backgroundImagePathIsEmbeded = True

    # ---------------------------------------------------------------------
    def undo(self):

        self.view.set_background_image(self.eskiImagePath)
        self.view.backgroundImagePathIsEmbeded = False
        if not self.kopya_var:
            try:
                os.remove(self.yeniImagePath)
            except OSError as e:
                self.view.parent().log(
                    'Warning! could not delete embeded background image file, '
                    'but scene\'s background image file path succesfully reverted to original path. ( {} )'.format(
                        os.strerror(e.errno)),
                    20000, 3)
