# -*- coding: utf-8 -*-
# .


__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '3/27/16'

import os
import uuid
import shutil

from PySide6.QtCore import (Qt, QRectF, QPointF, Slot, Signal, QThread, QLineF, QObject)
from PySide6.QtGui import (QPixmap, QCursor, QPen, QImage, QUndoStack)
from PySide6.QtWidgets import (QApplication, QGraphicsScene)
# from sub.items.base import BaseItem
# TODO: bunu sadece dragEnterEvent kaynagi belirlemek icin kullaniyoruz, bi inceleyelim
from canta.nesneler.yuvarlakFircaBoyutu import YuvarlakFircaBoyutu
from canta.treeView import TreeView
from canta.selectionQueue import SelectionQueue
from canta.nesneler.image import Image
from canta.nesneler.line import LineItem
from canta.nesneler.text import Text
from canta.nesneler.rect import Rect
from canta.nesneler.ellipse import Ellipse
from canta.nesneler.path import PathItem
from canta.nesneler.group import Group
# from canta.nesneler.video import VideoItem
# from canta.nesneler.dosya import DosyaNesnesi
from canta.nesneler.mirrorLine import MirrorLine
from canta.threadWorkers import DownloadWorker
from canta import undoRedoFonksiyolar as undoRedo


########################################################################
class Scene(QGraphicsScene):
    # itemMoved = Signal(QGraphicsItem, QPointF)
    itemMoved = Signal(object, QPointF)
    (NoTool, DrawLineTool, RectTool, EllipseTool,
     DrawPathTool, TextTool, ImageTool, VideoTool,
     DosyaAraci, MirrorX, MirrorY, CropImageTool) = range(12)

    # textItemSelected = Signal(QGraphicsTextItem)

    # ---------------------------------------------------------------------
    def __init__(self, tempDirPath, yaziRengi, arkaPlanRengi, scenePen, parent=None):
        super(Scene, self).__init__(parent)

        # gradient = QRadialGradient(0, 0, 10)
        # gradient.setSpread(QGradient.RepeatSpread)
        # self.setBackgroundBrush(gradient)

        self.tempDirPath = tempDirPath
        self.arkaPlanRengi = arkaPlanRengi
        self.yaziRengi = yaziRengi

        self.scenePen = scenePen

        # self.tempDirPath = tempfile.TemporaryDirectory().name
        # self.tempDirPath = tempfile.TemporaryDirectory()

        # self.saveFilePath = None

        self.toolType = self.NoTool

        # TODO: itemlara set data ve data diyebiliyoruz, (key = int ,value = QVariant)

        # TODO: add itemlarda parent yok..

        # burda, dicti iptal et

        self.space_tusu_su_an_basili = False

        self.lastItem = None
        self.pathItem = None
        self.mirrorLineItem = None
        self.drawLineItem = None
        self.fircaBoyutuItem = None
        self.fircaSonPos = QPointF()

        # self.selectionQueue = deque()
        self.selectionQueue = SelectionQueue(scene=self)

        self.unGroupedRootItems = set()

        self.undoStack = QUndoStack(self)
        # self.actionUndo = self.undoStack.createUndoAction(self)
        # self.actionRedo = self.undoStack.createRedoAction(self)

        self.movingItem = None
        self.movedItemsList = []
        self.isMovingItems = False
        self.itemMoved.connect(self.when_item_moved)

        self.activeItem = None
        self._acceptDrops = True

        self.undoRedo = undoRedo

        self._kimlik_nesne_sozluk = {}

    # ---------------------------------------------------------------------
    def get_properties_for_save(self):
        view = self.views()[0]
        properties = {"yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "scenePen": self.scenePen,
                      "sceneRect": self.sceneRect(),
                      # "embededImageCounter": self.embededImageCounter,
                      "backgroundBrush": view.backgroundBrush(),
                      "backgroundImagePath": view.backgroundImagePath,
                      # "viewMatrix": self.views()[0].matrix()
                      "viewTransform": view.transform(),
                      "viewHorizontalScrollBarValue": view.horizontalScrollBar().value(),
                      "viewVerticalScrollBarValue": view.verticalScrollBar().value()
                      }
        return properties

    # ---------------------------------------------------------------------
    def set_tool(self, toolType, itemText=None, dosyaYolu=None, pos=None):
        # parca bir cok yerde bunu kapatmaktansa basta kapatıp
        # asagida gerekirse aciyoruz
        # setMouseTracking kullanan araclardan sadece DrawPathTool tekrar tekrar cizim yapiyor
        # digerleri tek islem yapiyor ve tooldan cikiyor yani set_tool yani burasi cagriliyor
        # DrawPathToolda surekli cizim yapabildiğimiz için kapatmaya gerek yok
        # aslında bunu da fircaBoyutuItem icin aciyoruz sadece (ilerde baska seylerde de kullanabiliriz)
        self.views()[0].setMouseTracking(False)
        self.finish_interactive_tools()
        self.cancel_mirror_tools()

        self.toolType = toolType
        self.dosyaYolu = dosyaYolu
        self.itemText = itemText

        if self.activeItem:
            # bu ozellikle, sahneye cift tiklayip daha hic bir sey yazilmamis text objesi icin konuldu,
            # yoksa 2 defa bu sahne classindaki is_text_item_empty cagriliyor ve problem oluyor.
            # TODO: buna daha da bi bakilabilir. normalde problem olmamasi lazim. bu gecici bir cozum.
            # mesela sahnede bos text secili ve yanip sonerken, yeni bir kare cizmek icin toolu secip
            # sahneye tikladigimda, hata oluyor. text item deselected oluyor, textitemdaki itemchange sebebi ile
            # selectionqqueden bu gecici text item temizleniyor.
            # sonra kare cizmek icin tiklaninca focus da kayboluyor, textteki focusout da is_text_item_empty cagirip
            # orda da selecitonQueue dan temizlemem var.
            # ordan sinyal gidiyor is_text_item_empty calisiyor, sonra da undoRedoAdditem clearSelection var
            # orda mi problem acaba. 2. defa mi caigiryor.
            # veya hani araya mouseclickevent giriyor bu lost focusu kaybedemedn event undoRedoAdditem
            # cagirip orda da, clearselection sebebi ile focus kaybolma falan derken, event bitince bi de tekrar text
            # signallerinden mi cagriliyor, gibi.. anladın sen.
            self.activeItem.clearFocus()

        if toolType == self.NoTool:
            self.parent().setCursor(Qt.ArrowCursor)
            return

        elif toolType == self.TextTool:
            pixmap = QPixmap(':icons/cursor-text.png')
        elif toolType == self.RectTool:
            pixmap = QPixmap(':icons/cursor-rectangle.png')
        elif toolType == self.DrawLineTool:
            self.views()[0].setMouseTracking(True)
            pixmap = QPixmap(':icons/cursor-line.png')
            self.drawLineItem = None
        elif toolType == self.EllipseTool:
            pixmap = QPixmap(':icons/cursor-circle.png')
        elif toolType == self.DrawPathTool:
            pixmap = QPixmap(':icons/cursor-pen.png')
            # self.pathItem = PathItem(self.yaziRengi, self.arkaPlanRengi, QPen(self.scenePen))
            # self.addItem(self.pathItem)
            self.views()[0].setMouseTracking(True)
            self.pathItem = None
        elif toolType == self.ImageTool:
            pixmap = QPixmap(':icons/cursor-image.png')
        elif toolType == self.VideoTool:
            pixmap = QPixmap(":icons/cursor-pen.png")
        elif toolType == self.DosyaAraci:
            pixmap = QPixmap(":icons/cursor-pen.png")

        elif toolType == self.MirrorX:
            r = self.views()[0].get_visible_rect()
            self.mirrorLineItem = MirrorLine(posFeedback=pos, axis="x")
            self.mirrorLineItem.setLine(pos.x(),
                                        r.top(),
                                        pos.x(),
                                        r.bottom())

            self.views()[0].setMouseTracking(True)
            self.addItem(self.mirrorLineItem)
            self.mirrorLineItem.updateScale()
            self.parent().setCursor(Qt.ArrowCursor)
            return

        elif toolType == self.MirrorY:
            r = self.views()[0].get_visible_rect()
            self.mirrorLineItem = MirrorLine(posFeedback=pos, axis="y")
            self.mirrorLineItem.setLine(r.left(),
                                        pos.y(),
                                        r.right(),
                                        pos.y())

            self.views()[0].setMouseTracking(True)
            self.addItem(self.mirrorLineItem)
            self.mirrorLineItem.updateScale()
            self.parent().setCursor(Qt.ArrowCursor)
            return
            # vh = self.views()[0].height()
            # pixmap = QPixmap(1,vh)
            # # pix.fill(Qt.transparent)
            # painter = QPainter(pixmap)
            # painter.drawLine(0,0,0,vh)
            # painter.end()
            # painter = None
            # del painter
        elif toolType == self.CropImageTool:
            self.activeItem._isCropping = True
            self.parent().setCursor(Qt.CrossCursor)
            return

        # pixmap.setMask(pixmap.mask())
        # cursor = QCursor(pixmap.scaled(QSize(20, 20)))
        self.parent().setCursor(QCursor(pixmap))
        # mesela drawpath tool secildi, hemen sahne uzerine gelindi shifte basildi
        # firca boyutu ayarlamak icin, focus yoksa  key press event calismiyor
        # tabi tool secildi , sayfa degistirldi yine focus gidiyor.
        # acaba follow focus mu yapsak
        # self.views()[0].setFocus()

    # ---------------------------------------------------------------------
    def unite_with_scene_rect(self, rect):
        unitedRect = self.sceneRect().united(rect)
        visRect = self.views()[0].get_visible_rect()
        if unitedRect.size().width() * unitedRect.size().height() > visRect.size().width() * visRect.size().height():
            # self.setSceneRect(visRect.united(unitedRect))
            self.setSceneRect(unitedRect)
        # else:
        #     self.setSceneRect(visRect)

        self.parent().tw_sayfa_guncelle()

    # ---------------------------------------------------------------------
    def addItem(self, item):
        self._kimlik_nesne_sozluk[item._kim] = item
        super(Scene, self).addItem(item)

    # ---------------------------------------------------------------------
    def removeItem(self, item):
        # temptextitem icin,bir bakmak lazim.temp textitem sahneye degil nesneye ekleniyor. o yuzden _kim eklenmiyor
        if item._kim in self._kimlik_nesne_sozluk:
            del self._kimlik_nesne_sozluk[item._kim]
        super(Scene, self).removeItem(item)

    # ---------------------------------------------------------------------
    def isModified(self):
        return not self.undoStack.isClean()

    # # ---------------------------------------------------------------------
    # def set_modified(self, status):
    #     self._isModified = status

    # ---------------------------------------------------------------------
    def get_unique_path_for_downloaded_html_image(self, baseName):
        # onemli: text nesnesindeki set_document_url'de de images-html klasoru ekleniyor.
        # img src= direkt adres yazabiliyoruz boylelikle
        imageDirectory = os.path.join(self.tempDirPath, "images-html")
        if not os.path.exists(imageDirectory):
            os.makedirs(imageDirectory)
        self.parent().cModel.embededImageCounter += 1
        # return os.path.join(imageFolder, "{}.jpg".format(self.embededImageCounter))
        return os.path.join(imageDirectory,
                            "defterHtmlImage-{}-{}-{}".format(self.parent().cModel.embededImageCounter,
                                                              str(uuid.uuid4())[:5],
                                                              baseName))

    # ---------------------------------------------------------------------
    def get_unique_path_for_embeded_image(self, baseName):
        imageFolder = os.path.join(self.tempDirPath, "images")
        if not os.path.exists(imageFolder):
            os.makedirs(imageFolder)

        self.parent().cModel.embededImageCounter += 1
        imgPath = os.path.join(imageFolder,
                               "{}-{}".format(self.parent().cModel.embededImageCounter, baseName))

        if os.path.exists(imgPath):
            # tekrar bu fonksiyonu cagiriyoruz, her cagrildiginda sayac + 1 artiyor
            # tabi halihazirda 1000 resim varsa, yapistirilan resim 1 ile basliyorsa 1000 kere
            # cagrilmayacak cunku 1_pasted_image > 2_1_pasted image seklinde olacak.
            # (baseName olarak dosya_adini gonderiyoruz, bu degisikligi gerektiren durum icin)
            # bir bakilabilir bunlarin hepsini tek fonksiyon ve isimde toparlayabiliriz.
            imgPath = self.get_unique_path_for_embeded_image(baseName)

        # return os.path.join(imageFolder, "{}.jpg".format(self.embededImageCounter))
        return imgPath

    # ---------------------------------------------------------------------
    def get_unique_path_for_embeded_video(self, baseName):
        videoDirectory = os.path.join(self.tempDirPath, "videos")
        if not os.path.exists(videoDirectory):
            os.makedirs(videoDirectory)
        self.parent().cModel.embededVideoCounter += 1
        videoPath = os.path.join(videoDirectory,
                                 "{}-{}".format(self.parent().cModel.embededVideoCounter, baseName))

        if os.path.exists(videoPath):
            # 2_1_basename seklinde basa ekler
            videoPath = self.get_unique_path_for_embeded_video(baseName)

        return videoPath

    # ---------------------------------------------------------------------
    def get_unique_path_for_embeded_file(self, baseName):
        fileDirectory = os.path.join(self.tempDirPath, "files")
        if not os.path.exists(fileDirectory):
            os.makedirs(fileDirectory)
        self.parent().cModel.embededFileCounter += 1
        filePath = os.path.join(fileDirectory,
                                "{}-{}".format(self.parent().cModel.embededFileCounter, baseName))

        if os.path.exists(filePath):
            # 2_1_basename seklinde basa ekler
            filePath = self.get_unique_path_for_embeded_file(baseName)
        return filePath

    # ---------------------------------------------------------------------
    def get_items_selected_top_level_parentitem(self, item):
        parentItem = item.parentItem()
        topLevelSelected = parentItem
        while parentItem:
            if parentItem in self.selectionQueue:
                topLevelSelected = parentItem
            parentItem = parentItem.parentItem()
        return topLevelSelected

    # ---------------------------------------------------------------------
    def get_selected_top_level_items(self):
        items = []
        for i in self.selectionQueue:
            if i.parentItem() in self.selectionQueue:
                continue
            items.append(i)
        return items

    # ---------------------------------------------------------------------
    def select_all_children_recursively(self, item, cosmeticSelect, topmostParent=False):
        if item.type() == Group.Type:
            items = item.parentedWithParentOperation
        else:
            items = item.childItems()

        if cosmeticSelect:
            # method called from parent item's mousePressEvent
            # mouseRelease event will deselect everything
            #  but the item itself (if it is not moved(dragged) after pressed)
            # so we don't use mousePressEvent selection for anything other than visual continuity.
            for c in items:
                if c.childItems():
                    self.select_all_children_recursively(c, cosmeticSelect)
                c.cosmeticSelect = cosmeticSelect
                c.update()
        else:
            # method called from parent item's mouseReleaseEvent
            for c in items:
                if c.childItems():
                    self.select_all_children_recursively(c, cosmeticSelect)
                c.cosmeticSelect = cosmeticSelect
                c.setSelected(True)
                # c.update()
            else:
                if topmostParent:  # there may be parents in parent's childItems()
                    # make item active item
                    # self.activeItem.isActiveItem = False
                    # item.isActiveItem = True
                    # self.activeItem = item
                    # make item last and active item.
                    self.selectionQueue.remove(item)
                    self.selectionQueue.append(item)

    # ---------------------------------------------------------------------
    # @Slot(QGraphicsItem, QPointF)
    @Slot(object, QPointF)
    def when_item_moved(self, movedItem, eskiPosition):
        # self.undoStack.push(UndoableMove(self.tr("Item moved"), movedItem, eskiPosition))
        undoRedo.undoableMove(self.undoStack, self.tr("Item moved"), movedItem, eskiPosition)

    # ---------------------------------------------------------------------
    def cancel_mirror_tools(self):
        if self.mirrorLineItem:
            self.views()[0].setMouseTracking(False)
            self.removeItem(self.mirrorLineItem)
            self.mirrorLineItem = None

    # ---------------------------------------------------------------------
    def finish_interactive_tools(self, kapat=True):

        if self.toolType == self.DrawPathTool:
            if self.pathItem:

                if self.pathItem.path().elementCount() > 1:
                    if self.pathItem.path().elementCount() == 2:
                        kapat = False
                    self.pathItem.close_path(kapat)
                    self.removeItem(self.pathItem)
                    # resim nesnesi uzerine ciziyorsak

                    ilk_nokta = self.pathItem.mapToScene(QPointF(self.pathItem.path().elementAt(0).x,
                                                                 self.pathItem.path().elementAt(0).y))
                    son_nokta = self.pathItem.mapToScene(
                        QPointF(self.pathItem.path().elementAt(self.pathItem.path().elementCount() - 1).x,
                                self.pathItem.path().elementAt(self.pathItem.path().elementCount() - 1).y))

                    ustuneCizilenResimNesnesi = None

                    for nokta in [ilk_nokta, son_nokta]:
                        nesne = self.itemAt(nokta, self.views()[0].transform())
                        if nesne:
                            if nesne.type() == Image.Type:
                                ustuneCizilenResimNesnesi = nesne
                                break

                    if ustuneCizilenResimNesnesi:
                        self.undoStack.beginMacro(self.tr("draw on image"))
                        undoRedo.undoableAddItem(self.undoStack, description=self.tr("add path"), scene=self,
                                                 item=self.pathItem, sec=False)
                        yeniPos = ustuneCizilenResimNesnesi.mapFromScene(self.pathItem.scenePos())
                        undoRedo.undoableParent(self.undoStack, self.tr("_parent"), self.pathItem,
                                                ustuneCizilenResimNesnesi, yeniPos)
                        self.undoStack.endMacro()
                    else:
                        undoRedo.undoableAddItem(self.undoStack, description=self.tr("add path"), scene=self,
                                                 item=self.pathItem, sec=False)

                    self.pathItem = None
                    # DrawPathTool da setMouseTracking surekli acik
                    # self.views()[0].setMouseTracking(False)
                else:
                    self.removeItem(self.pathItem)
                    self.pathItem = None
                    # DrawPathTool da setMouseTracking surekli acik
                    # self.views()[0].setMouseTracking(False)

                return

        elif self.toolType == self.DrawLineTool:

            if self.drawLineItem:
                if self.drawLineItem.length() > 0:

                    self.removeItem(self.drawLineItem)
                    undoRedo.undoableAddItem(self.undoStack, description=self.tr("add line"), scene=self,
                                             item=self.drawLineItem)
                    self.drawLineItem = None
                    self.views()[0].setMouseTracking(False)
                else:
                    self.removeItem(self.drawLineItem)
                    self.drawLineItem = None
                    self.views()[0].setMouseTracking(False)

        elif self.toolType == self.CropImageTool:
            # diger durumlar icin Image.itemChange deselected kullanildi.
            if self.activeItem and self.activeItem.type() == Image.Type:
                self.activeItem.finish_crop()
                # self.activeItem._isCropping = False
                # self.activeItem.rubberBand.hide()
                # self.activeItem.rubberBand.deleteLater()
                # self.activeItem.rubberBand = None

        self.toolType = self.NoTool
        self.parent().setCursor(Qt.ArrowCursor)
        # self.deleteLater()
        self.parent().actionSwitchToSelectionTool.setChecked(True)

    # ---------------------------------------------------------------------
    def _fircaBoyutuItem_olustur(self):
        # self.views()[0].setMouseTracking(True)
        rect = QRectF(-self.scenePen.widthF() / 2, -self.scenePen.widthF() / 2, self.scenePen.widthF(),
                      self.scenePen.widthF())
        pen = QPen(self.scenePen.color(), 2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin)
        self.fircaBoyutuItem = YuvarlakFircaBoyutu(self.fircaSonPos, rect, Qt.transparent,
                                                   # self.scenePen,
                                                   pen)
        self.parent().increase_zvalue(self.fircaBoyutuItem)
        self.addItem(self.fircaBoyutuItem)

    # # ---------------------------------------------------------------------
    # bunu alttaki self.tekerlek_ile_firca_boyu_degistir e tasidik
    # view daki wheel eventten cagiriyoruz
    # yoksa hem scroll ediyor hem de firca boyutu degistiriyordu veya ikisi de olmuyordu.
    # def wheelEvent(self, event):
    #     # factor = 1.41 ** (event.delta() / 240.0)
    #     # self.scale(factor, factor)
    #     if self.toolType == self.DrawPathTool:
    #         if event.modifiers() & Qt.ShiftModifier:
    #             if self.fircaBoyutuItem:
    #
    #                 if event.delta() > 0:
    #                     cap = self.parent().fircaBuyult()
    #                 else:
    #                     cap = self.parent().fircaKucult()
    #
    #                 rect = QRectF(-cap / 2, -cap / 2, cap, cap)
    #                 self.fircaBoyutuItem.setRect(rect)
    #
    #     else:
    #         super(Scene, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def tekerlek_ile_firca_boyu_degistir(self, angleDeltaY):
        # ok cizerken self.fircaBoyutuItem kullanmiyoruz.
        if self.toolType == self.DrawLineTool:
            if angleDeltaY > 0:
                cap = self.parent().fircaBuyult()
            else:
                cap = self.parent().fircaKucult()

            self.drawLineItem.setCizgiKalinligi(cap)

        elif self.toolType == self.DrawPathTool:
            if self.fircaBoyutuItem:
                if angleDeltaY > 0:
                    cap = self.parent().fircaBuyult()
                else:
                    cap = self.parent().fircaKucult()

                rect = QRectF(-cap / 2, -cap / 2, cap, cap)
                self.fircaBoyutuItem.setRect(rect)

    # ---------------------------------------------------------------------
    def shift_drag_ile_firca_boyu_degistir(self, yariCap):
        if self.toolType == self.DrawPathTool:

            if self.fircaBoyutuItem:
                cap = 2 * yariCap
                self.parent().fircaDirektDegerGir(cap)

                rect = QRectF(-yariCap, -yariCap, cap, cap)
                self.fircaBoyutuItem.setRect(rect)

    # ---------------------------------------------------------------------
    def yazi_yazilmiyorsa_nesneyi_kaydir(self, x, y):
        devam = False

        # TODO: basitlesitrilebilir , if hasattr(self.activeItem, 'tempTextItem'): ile belki..
        if self.activeItem:
            if self.activeItem.type() == Text.Type:
                if not self.activeItem.hasFocus():
                    devam = True

            # bu ikisinde tempTextItem yok
            elif self.activeItem.type() == Group.Type:
                devam = True
            # bu ikisinde tempTextItem yok
            elif self.activeItem.type() == LineItem.Type:
                devam = True
            # geri kalanlarda tempTextItem var, (nesne uzerine yazi yazdigimiz item bu)
            else:
                if not self.activeItem.tempTextItem:
                    devam = True

        # tek nesne icin, ne kadar secili nesne olursa olsun , yani self.activeItem icin
        # if devam:
        #     eskiPos = self.activeItem.pos()
        #     self.activeItem.moveBy(x, y)
        #     self.when_item_moved(self.activeItem, eskiPos)

        # butun secili nesneler icin
        if devam:
            items = self.get_selected_top_level_items()

            self.undoStack.beginMacro(self.tr("Item(s) moved"))

            for item in items:
                eskiPos = item.pos()
                item.moveBy(x, y)
                self.when_item_moved(item, eskiPos)

            self.undoStack.endMacro()

    # ---------------------------------------------------------------------
    # @Slot(QGraphicsTextItem)
    @Slot(object)
    def is_text_item_empty(self, textItem):
        # self.childItems() kontrolu de, yazi bir baska nesnenin parenti iken silinmis olabilir diye.
        if not textItem.toPlainText() and not textItem.childItems():
            # self.selectionQueue.remove(textItem)
            # self.removeItem(textItem)
            # undoableRemoveItem icine koymak durumundayiz yoksa yazisi olan nesne daha sonra ici silinince
            # sahneden siliniyor, undo redo durumunda ise problem cunku nesne yok, vs..
            undoRedo.undoableRemoveItem(self.undoStack, self.tr("auto delete empty text item"), self, textItem,
                                        addToUnGroupedRootItems=False)

            # textItem.deleteLater()

    # ---------------------------------------------------------------------
    def create_empty_text_object_with_double_click(self, scenePos):
        textItem = Text(scenePos, self.yaziRengi, self.arkaPlanRengi, QPen(self.scenePen), self.font())
        textItem.set_document_url(self.tempDirPath)
        textItem.textItemFocusedOut.connect(self.is_text_item_empty)
        self.parent().increase_zvalue(textItem)
        # textItem.textItemSelectedChanged.connect(self.textItemSelected)
        # self.addItem(textItem)
        undoRedo.undoableAddItem(self.undoStack, description=self.tr("add text"), scene=self, item=textItem)
        textItem.setFocus()

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # drawlnetool kontrolune gerek yok esasen cunku ilktiklamada cizgiyi bitirip sahneye ekliyor.
            # ama coklu cizgi eklenirse hatirlatma olsun diye..
            if not self.toolType == self.DrawPathTool and not self.toolType == self.DrawLineTool:
                if not self.itemAt(event.scenePos(), self.views()[0].transform()):
                    # modifier yoksa olustur. cunku mesela ctrl basili ise yaiNesnesi olusturup,hemen yazi nesnesine
                    # gidiyor ciftTiklama o da miniWebGezgini aciyor ve yazi bos oldugu ici siliniyor
                    # sahneye ctrl veya ctrl+shift ile cift tiklayina miniWebGezgini acmis oluyoruz.
                    if event.modifiers() == 0:  # 0x00000000
                        self.create_empty_text_object_with_double_click(event.scenePos())
        elif event.button() == Qt.MiddleButton:
            self.views()[0].zoomToFit()
        super(Scene, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            if self.toolType == self.NoTool:
                # if event.modifiers() & Qt.AltModifier:
                #     duplicateItem = self.itemAt(event.scenePos())
                #     self.parent().act_copy()
                #     self.parent().act_paste()
                #     self.set_modified(True)

                mousePos = event.buttonDownScenePos(Qt.LeftButton)
                # self.movingItem = self.itemAt(mousePos)
                self.movingItem = self.itemAt(mousePos, self.views()[0].transform())
                if self.movingItem:  # and event.button() == Qt.LeftButton
                    if self.movingItem.topLevelItem().type() == Group.Type:
                        if self.movingItem in self.movingItem.topLevelItem().allNonGroupGroupChildren:
                            self.movingItem = self.movingItem.topLevelItem()
                    self.eskiPosOfMovingItem = self.movingItem.pos()
                    self.movedItemsList = []
                    selectedItems = self.selectedItems()
                    # hic birsey secili degil iken, tek itema tiklayip tasiyinca, self.selectedItems
                    # bos donuyor. birden fazla item tasimak icin zaten onlar secili olmak durumunda.
                    # dolayisi ile normal calisiyor. bu yuzden manual ekliyoruz
                    # eger sahnede secili item yok ve de self.movingItem var is demek ki,
                    # daha selection guncellenmemis oldugundan. gibi. neden guncellenmiyor
                    # cunku event daha yeni basliyor. qt itemlari secmek icin gerekli islemleri yapmamis oluyor.
                    # super kullandigimizda da problem oldu.
                    #  !!! bu safer de iki tane baska item secili mesela secili olmayan bir itemi tutup tasiyinca,
                    # hali hazirda secili olanlar undo edildi onlar da hareket ettirilmedikleri icin
                    # sahnede bir sey olmadi. yine dolayisi ile bir kontrol daha ekledik
                    # eger self.movingItem selectedItemslar iceresinde yoksa diye.
                    if selectedItems:
                        if self.movingItem in selectedItems:
                            for item in selectedItems:
                                self.movedItemsList.append([item, item.pos()])
                        else:
                            self.movedItemsList.append([self.movingItem, self.movingItem.pos()])
                    else:
                        self.movedItemsList.append([self.movingItem, self.movingItem.pos()])

                return QGraphicsScene.mousePressEvent(self, event)

            elif self.toolType == self.RectTool:

                # rect = QRectF(event.scenePos(), self.itemSize).translated(-self.itemSize.width() / 2,
                #                                                           -self.itemSize.height() / 2)

                # rect = QRectF(event.scenePos(), QSizeF(1, 1))
                rect = QRectF(0, 0, 1, 1)
                item = Rect(event.scenePos(), rect, self.yaziRengi, self.arkaPlanRengi, QPen(self.scenePen),
                            self.font())
                self.parent().increase_zvalue(item)

                # if event.modifiers() & Qt.ShiftModifier:
                item.hide_resize_handles()
                self.lastItem = item
                # self.addItem(item)
                undoRedo.undoableAddItem(self.undoStack, description=self.tr("add rectangle"), scene=self, item=item)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.toolType == self.EllipseTool:
                # rect = QRectF(event.scenePos(), self.itemSize).translated(-self.itemSize.width() / 2,
                #                                                           -self.itemSize.height() / 2)
                # rect = QRectF(event.scenePos(), QSizeF(1, 1))
                rect = QRectF(0, 0, 1, 1)
                item = Ellipse(event.scenePos(), rect, self.yaziRengi, self.arkaPlanRengi, QPen(self.scenePen),
                               self.font())
                self.parent().increase_zvalue(item)
                item.hide_resize_handles()
                self.lastItem = item
                # self.addItem(item)
                undoRedo.undoableAddItem(self.undoStack, description=self.tr("add ellipse"), scene=self, item=item)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.toolType == self.TextTool:

                textItem = Text(event.scenePos(),
                                self.yaziRengi,
                                self.arkaPlanRengi,
                                QPen(self.scenePen),
                                self.font(),
                                text=self.itemText)
                textItem.set_document_url(self.tempDirPath)
                self.parent().increase_zvalue(textItem)
                textItem.textItemFocusedOut.connect(self.is_text_item_empty)
                # textItem.textItemSelectedChanged.connect(self.textItemSelected)
                # self.addItem(textItem)
                undoRedo.undoableAddItem(self.undoStack, description=self.tr("add text"), scene=self, item=textItem)
                # self.itemText = None
                self.toolType = self.NoTool
                self.parent().setCursor(Qt.ArrowCursor)
                self.parent().actionSwitchToSelectionTool.setChecked(True)
                return QGraphicsScene.mousePressEvent(self, event)

            # elif self.toolType == self.ImageTool:
            #     pos = event.scenePos()
            #     pixMap = QPixmap(self.dosyaYolu).scaled(self.itemSize.toSize(), Qt.KeepAspectRatio)
            #     rect = QRectF(pixMap.rect())
            #     rect.moveTo(pos.x() - rect.width() / 2, pos.y() - rect.height() / 2)
            #     self.addItem(Image(self.dosyaYolu, pixMap, rect, self.yaziRengi, self.arkaPlanRengi, self.scenePen))
            #     pixMap = None
            #     #self.dosyaYolu = None

            elif self.toolType == self.ImageTool:
                self.parent().ekle_resim_direkt(self.dosyaYolu, event.scenePos())
                self.toolType = self.NoTool
                self.parent().setCursor(Qt.ArrowCursor)
                self.parent().actionSwitchToSelectionTool.setChecked(True)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.toolType == self.VideoTool:
                self.parent().ekle_video_direkt(self.dosyaYolu, event.scenePos())
                self.toolType = self.NoTool
                self.parent().setCursor(Qt.ArrowCursor)
                self.parent().actionSwitchToSelectionTool.setChecked(True)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.toolType == self.DosyaAraci:
                self.parent().ekle_dosya_direkt(self.dosyaYolu, event.scenePos())
                self.toolType = self.NoTool
                self.parent().setCursor(Qt.ArrowCursor)
                self.parent().actionSwitchToSelectionTool.setChecked(True)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.toolType == self.DrawPathTool:
                self.views()[0].setDragModeNoDrag()
                # self.views()[0].setMouseTracking(True)
                if not self.pathItem:
                    self.pathItem = PathItem(event.scenePos(), self.yaziRengi, self.arkaPlanRengi, QPen(self.scenePen),
                                             self.font())
                    self.parent().increase_zvalue(self.pathItem)
                    # self.pathItem.move_start_point(event.scenePos())
                    self.pathItem.move_start_point()
                    self.addItem(self.pathItem)
                else:
                    if not self.pathItem.intersects:
                        if event.modifiers() & Qt.ControlModifier:
                            self.pathItem.append(event.scenePos())
                            return
                        else:
                            self.finish_interactive_tools(kapat=False)
                            return QGraphicsScene.mousePressEvent(self, event)
                    else:  # intersects
                        self.finish_interactive_tools(kapat=True)
                        return QGraphicsScene.mousePressEvent(self, event)
                # return QGraphicsScene.mousePressEvent(self, event)
                return

            elif self.toolType == self.DrawLineTool:
                self.views()[0].setDragModeNoDrag()
                # self.views()[0].setMouseTracking(True)
                if not self.drawLineItem:
                    self.drawLineItem = LineItem(event.scenePos(), QPen(self.scenePen), yaziRengi=self.yaziRengi,
                                                 font=self.font())
                    self.parent().increase_zvalue(self.drawLineItem)
                    # self.drawLineItem.move_start_point(event.scenePos())
                    self.drawLineItem.move_start_point()
                    self.addItem(self.drawLineItem)
                    ustuneOkCizilenItem = self.itemAt(event.scenePos(), self.views()[0].transform())
                    if ustuneOkCizilenItem:
                        # item sabit, icindeki cizgi degisiyor mousemoveda,diyoruz simdilik
                        # if not self.drawLineItem in ustuneOkCizilenItem.oklar_dxdy_nokta.keys():
                        ustuneOkCizilenItem.ok_ekle(self.drawLineItem, event.scenePos(), 1)
                else:
                    oku_normal_parent_et = False
                    ustuneOkCizilenItemList = self.items(event.scenePos(), deviceTransform=self.views()[0].transform())
                    # bazen veya (eskiden?) cizilen ok da listelenebiliyor(du).
                    if self.drawLineItem in ustuneOkCizilenItemList:
                        ustuneOkCizilenItemList.remove(self.drawLineItem)
                    if ustuneOkCizilenItemList:
                        # okun iki noktasi da ayni nesne ustunde olacak ise
                        # burda ikinci noktayi koydugumuzda, okun  nesneye olan ilk bagini cozup
                        # sonra hiç bir noktasini baglamadan normal parent ediyoruz
                        # asagi tasindi
                        if self.drawLineItem in ustuneOkCizilenItemList[0].oklar_dxdy_nokta:
                            # undoRedo.undoableAddItem ile ekledikten sonra parent ediyoruz
                            # bu asamada yaparsak gecici oku parent etmis oluruz ki siliniyor zaten az sonra
                            oku_normal_parent_et = True

                        else:
                            # beklenen normal islem bu
                            # okun ilk noktasi boslukta ya da baska nesneye bagli
                            # burda da okun ikinci noktasini uzerine tikladigimiz nesneye bagliyoruz
                            ustuneOkCizilenItemList[0].ok_ekle(self.drawLineItem, event.scenePos(), 2)

                    # normal ok cizme islemiyle devam

                    self.drawLineItem.temp_append(event.scenePos())
                    # ok nesnesinde path nesnesindeki gibi close path yok
                    # o yuzden burda isDrawingFinished = True diyoruz.
                    # line.temp_append() icinde deMEmek de tercih edildi.
                    self.drawLineItem.isDrawingFinished = True
                    self.removeItem(self.drawLineItem)
                    undoRedo.undoableAddItem(self.undoStack, description=self.tr("add line"), scene=self,
                                             item=self.drawLineItem)

                    # bunu yukardaki if kontrolunden buraya tasimak gerekti
                    # undoRedo.undoableAddItem ile ekledikten sonra oku parent ediyoruz
                    # oncesinde yaparsak gecici oku parent etmis oluruz ki
                    # siliniyor zaten undoRedo.undoableAddItem ile asil ok nesnesini sahneye eklemeden once
                    if oku_normal_parent_et:
                        #  once az once drawLineItem olsuturulurken olasi baglanmis
                        #  ilk nokta bagliligini cozuyoruz
                        ustuneOkCizilenItemList[0].ok_sil(self.drawLineItem)
                        # su an okun 2 noktasi da hic bir yere baglai degil, okta da baglanmis_nesneler = {}
                        yeniPos = ustuneOkCizilenItemList[0].mapFromScene(self.drawLineItem.scenePos())
                        undoRedo.undoableParent(self.undoStack, self.tr("_parent"), self.drawLineItem,
                                                ustuneOkCizilenItemList[0], QPointF(yeniPos))

                    self.drawLineItem = None

                    self.toolType = self.NoTool
                    self.views()[0].setMouseTracking(False)
                    self.parent().setCursor(Qt.ArrowCursor)
                    # self.parent().setCursor(Qt.ArrowCursor)
                    self.parent().actionSwitchToSelectionTool.setChecked(True)
                # return QGraphicsScene.mousePressEvent(self, event)
                return

            elif self.toolType == self.MirrorX:
                # self.views()[0].setMouseTracking(False)
                self.parent().act_mirror_x(event.scenePos())  # bu cancel_mirror_toolsu da cagiriyor.

            elif self.toolType == self.MirrorY:
                # self.views()[0].setMouseTracking(False)
                self.parent().act_mirror_y(event.scenePos())  # bu cancel_mirror_toolsu da cagiriyor.

            # if not event.modifiers() & Qt.ShiftModifier:
            # if not event.modifiers() & Qt.AltModifier:
            #     if not self.toolType == self.DrawPathTool:
            #         self.toolType = self.NoTool
            #         self.parent().setCursor(Qt.ArrowCursor)
            #
            #     self.pathItem = None
            #     # self.views()[0].setMouseTracking(False)
        super(Scene, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        if self.toolType == self.DrawPathTool:
            self.fircaSonPos = event.scenePos()

        if self.pathItem and self.toolType == self.DrawPathTool:
            if event.modifiers() & Qt.ShiftModifier and self.fircaBoyutuItem:

                # self.fircaBoyutuItem.setPos(QPointF(event.scenePos().x(), event.scenePos().y()))
                fark = QLineF(self.fircaBoyutuItem.pos(), event.scenePos()).length()
                # fark = sqrt((self.fircaBoyutuItem.pos().x() - event.scenePos().x()) ** 2
                #             + (event.scenePos().y() - self.fircaBoyutuItem.pos().y()) ** 2)

                # fark = math.hypot(x2 - x1, y2 - y1)
                self.shift_drag_ile_firca_boyu_degistir(fark / 2)
            else:
                # or'laniyor -> 0x00000000 = hicbiri , 0x00000001 sol , 0x00000002 sag  0x00000004 orta
                if event.buttons() == 1:  # mouse sol tus basili
                    # self.pathItem.replace_last(event.scenePos())
                    self.views()[0].setDragModeNoDrag()
                    self.pathItem.append(event.scenePos())
                    # self.pathItem.check_if_at_start(event.scenePos())
                    # event.accept()
                    # return QGraphicsScene.mouseMoveEvent(self, event)
                    self.views()[0].setDragModeRubberBandDrag()
                    event.ignore()

                else:
                    if event.modifiers() & Qt.ControlModifier:
                        # self.pathItem.replace_last(event.scenePos())
                        self.pathItem.temp_append_and_replace_last(event.scenePos())
                        self.pathItem.check_if_at_start(event.scenePos())
                        # event.accept()
                        # return QGraphicsScene.mouseMoveEvent(self, event)
                        return
                    else:
                        return

        if self.drawLineItem and self.toolType == self.DrawLineTool:
            self.views()[0].setDragModeNoDrag()
            self.drawLineItem.temp_append(event.scenePos())
            self.views()[0].setDragModeRubberBandDrag()
            # self.drawLineItem.line().setP2(event.scenePos())
            # self.drawLineItem.setLine(QLineF(self.line.line().p1(), mouseEvent.scenePos()))

            # return QGraphicsScene.mouseMoveEvent(self, event)
            return

        if self.toolType == self.MirrorX:
            self.mirrorLineItem.updatePosFeedBack(event.scenePos())
            r = self.views()[0].get_visible_rect()

            # m = self.mirrorLineItem.deviceTransform(self.views()[0].viewportTransform()).inverted()[0].m11()
            # m = self.mirrorLineItem.deviceTransform(self.views()[0].viewportTransform()).m11()
            # r= QRectF(m * (r.left()), m * (r.top()),
            #               m * (r.right()), m * (r.bottom()))

            # self.mirrorLineItem.setTransform(self.views()[0].transform().inverted()[0])
            self.mirrorLineItem.setLine(event.scenePos().x(),
                                        r.top(),
                                        event.scenePos().x(),
                                        r.bottom())

            self.mirrorLineItem.updateScale()

        if self.toolType == self.MirrorY:
            self.mirrorLineItem.updatePosFeedBack(event.scenePos())
            r = self.views()[0].get_visible_rect()
            self.mirrorLineItem.setLine(r.left(),
                                        event.scenePos().y(),
                                        r.right(),
                                        event.scenePos().y())

            self.mirrorLineItem.updateScale()

        #
        # else:
        #     super(Scene, self).mouseMoveEvent(event)

        if self.selectedItems():
            self.activeItem.ok_guncelle()

        super(Scene, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.views()[0].setDragModeRubberBandDrag()
            # if event.modifiers() & Qt.AltModifier:
            #     if self.toolType == self.RectTool or self.toolType == self.EllipseTool:
            #         self.toolType = self.NoTool
            #         self.parent().setCursor(Qt.ArrowCursor)
            if self.toolType == self.DrawPathTool:
                # # return QGraphicsScene.mousePressEvent(self, event)
                # if event.modifiers() & Qt.ControlModifier:
                #     return QGraphicsScene.mouseReleaseEvent(self, event)
                # else:
                #     if self.pathItem:
                #         self.finish_interactive_tools(kapat=False)
                #     return QGraphicsScene.mouseReleaseEvent(self, event)

                if not event.modifiers() & Qt.ControlModifier:
                    self.finish_interactive_tools(kapat=False)
                return QGraphicsScene.mouseReleaseEvent(self, event)

            if self.toolType == self.DrawLineTool:
                return QGraphicsScene.mouseReleaseEvent(self, event)

            elif self.toolType == self.RectTool or self.toolType == self.EllipseTool:
                self.lastItem.show_resize_handles()
                # if not event.modifiers() & Qt.AltModifier:
                if not self.space_tusu_su_an_basili:
                    self.lastItem.saved_cursor = Qt.ArrowCursor
                    self.toolType = self.NoTool
                    # self.parent().setCursor(Qt.ArrowCursor)
                    self.parent().actionSwitchToSelectionTool.setChecked(True)
                self.lastItem = None
                # return QGraphicsScene.mousePressEvent(self, event)
                return QGraphicsScene.mouseReleaseEvent(self, event)

            # if self.movingItem:  # and event.button() == Qt.LeftButton:
            #     if not self.eskiPosOfMovingItem == self.movingItem.pos():
            #         self.itemMoved.emit(self.movingItem, self.eskiPosOfMovingItem)
            #     self.movingItem = None

            # this one also handles, sceneRect adaptation for repositioned items.
            if self.movingItem:  # and event.button() == Qt.LeftButton:
                if not self.eskiPosOfMovingItem == self.movingItem.pos():
                    movedItemsBoundingRect = QRectF()  # sceneRect adaptation
                    self.undoStack.beginMacro("move {} item(s)".format(len(self.movedItemsList)))
                    for itemAndEskiPos in self.movedItemsList:
                        self.itemMoved.emit(itemAndEskiPos[0], itemAndEskiPos[1])
                        # v - sceneRect adaptation - v
                        movedItemsBoundingRect = movedItemsBoundingRect.united(itemAndEskiPos[0].sceneBoundingRect())
                    self.undoStack.endMacro()
                    self.unite_with_scene_rect(movedItemsBoundingRect)
                self.movingItem = None

        super(Scene, self).mouseReleaseEvent(event)
        # print(self.selectionQueue)

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Space:
            self.space_tusu_su_an_basili = True

        if event.key() == Qt.Key_Delete \
                or event.key() == Qt.Key_Backspace:
            if self.toolType == self.DrawPathTool:
                if self.pathItem:
                    if self.pathItem.path().elementCount() > 1:
                        self.pathItem.sonNoktaSil()
                    # else:
                    #     self.finish_interactive_tools()

        if event.key() == Qt.Key_Escape:
            self.cancel_mirror_tools()
            self.finish_interactive_tools(kapat=False)

        if event.key() == Qt.Key_Enter \
                or event.key() == Qt.Key_Return:

            if self.toolType == self.MirrorX:
                # self.views()[0].setMouseTracking(False)
                self.parent().act_mirror_x(self.parent().get_mouse_scene_pos())  # bu cancel_mirror_toolsu da cagiriyor.

            elif self.toolType == self.MirrorY:
                # self.views()[0].setMouseTracking(False)
                self.parent().act_mirror_y(self.parent().get_mouse_scene_pos())  # bu cancel_mirror_toolsu da cagiriyor.

        if event.key() == Qt.Key_Enter \
                or event.key() == Qt.Key_Return:
            self.finish_interactive_tools(kapat=True)

        # if event.key() == Qt.Key_Up:
        #     pass
        # if event.key() == Qt.Key_Down:
        #     pass
        # if event.key() == Qt.Key_Right:
        #     self.focusNextPrevChild(True)
        # if event.key() == Qt.Key_Left:
        #     self.focusNextPrevChild(False)

        # if event.key() == Qt.Key_Space:
        #     print(self.selectionQueue)

        ########################################################################

        # # TODO: movelara undo , ayrica sahnede diger nesneye gecmek muhtemelen modifersiz olsun.
        # # dolayisiyla tek birim hareket de alt tusuna falan mi atasak.

        if event.modifiers() & Qt.ShiftModifier:
            if event.key() == Qt.Key_Up:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(0, -10)
            if event.key() == Qt.Key_Down:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(0, 10)
            if event.key() == Qt.Key_Right:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(10, 0)
            if event.key() == Qt.Key_Left:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(-10, 0)

            if event.key() == Qt.Key_Shift:

                if self.toolType == self.DrawPathTool:
                    if not self.fircaBoyutuItem:
                        self._fircaBoyutuItem_olustur()

        # elif event.modifiers() & Qt.ShiftModifier:
        #     if event.key() == Qt.Key_Up:
        #         self.rotateItem(-1)
        #     if event.key() == Qt.Key_Down:
        #         self.rotateItem(1)
        #     if event.key() == Qt.Key_Right:
        #         self.rotateItem(1)
        #     if event.key() == Qt.Key_Left:
        #         self.rotateItem(-1)

        else:
            if event.key() == Qt.Key_Up:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(0, -1)
            if event.key() == Qt.Key_Down:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(0, 1)
            if event.key() == Qt.Key_Right:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(1, 0)
            if event.key() == Qt.Key_Left:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(-1, 0)

            # event.accept()

        super(Scene, self).keyPressEvent(event)

    # ---------------------------------------------------------------------
    def keyReleaseEvent(self, event):

        if event.key() == Qt.Key_Space:
            self.space_tusu_su_an_basili = False

        # if event.key() == Qt.Key_Alt:
        #     if self.toolType == self.RectTool or self.toolType == self.EllipseTool:
        #         self.toolType = self.NoTool
        #         self.parent().setCursor(Qt.ArrowCursor)

        if self.toolType == self.DrawPathTool:
            if event.key() == Qt.Key_Shift:
                if self.fircaBoyutuItem:
                    # self.views()[0].setMouseTracking(False)
                    self.removeItem(self.fircaBoyutuItem)
                    self.fircaBoyutuItem = None

        super(Scene, self).keyReleaseEvent(event)

    # ---------------------------------------------------------------------
    def dragEnterEvent(self, event):
        # self.parent().tabWidget.currentWidget().setFocus()
        # !! burda bir onceki eventin modifierini dikkate aliyor.
        # if event.modifiers() & Qt.ShiftModifier:
        #     print("shift")
        self.parent().raise_()
        self.parent().activateWindow()
        if not self._acceptDrops:
            event.ignore()
            return
            # event.ignore()
            # return QGraphicsScene.dragEnterEvent(self, event)
        # if event.source():
        #     if type(event.source()) == TreeView:
        #         isSourceExternal = 0
        # else:
        #         isSourceExternal = 1

        if isinstance(event.source(), TreeView):
            event.ignore()
            return
        # print(event.source())
        # print(type(event.source()))
        if event.mimeData().hasUrls() or event.mimeData().hasText or event.mimeData().hasHtml():
            event.accept()
            # event.acceptProposedAction()
        # else:
        #     event.ignore()

        else:
            super(Scene, self).dragEnterEvent(event)

    # ---------------------------------------------------------------------
    def dragMoveEvent(self, event):
        # if event.modifiers() & Qt.ShiftModifier:
        #     print("shift")
        # if event.mimeData().hasUrls() or event.mimeData().hasText() or event.mimeData().hasHtml():
        #     event.accept()
        # else:
        #     super(Scene, self).dragMoveEvent(event)
        if not self._acceptDrops:
            event.ignore()
            return

        event.accept()
        # event.acceptProposedAction()
        # super(Scene, self).dragMoveEvent(event)

    # # ---------------------------------------------------------------------
    # def dragLeaveEvent(self, event):
    #     # self.parent().lower()
    #     super(Scene, self).dragLeaveEvent(event)

    # ---------------------------------------------------------------------
    def dropEvent(self, event):
        if not self._acceptDrops:
            event.ignore()
            return

        # print(event.mimeData().formats())
        # print(event.mimeData().urls())

        if event.mimeData().hasUrls():

            # bu tek eleman, browserdan veya webviewdan drag drop edilirse link, ya da resimde link vardir href gibi..
            webUrl = []
            imgPaths = []
            defPaths = []
            otherFilePaths = []
            pos = event.scenePos()
            for url in event.mimeData().urls():
                # links.append(url.toLocalFile())
                if url.isLocalFile():
                    filePath = url.toLocalFile()
                    extension = os.path.splitext(filePath)[1][1:].lower()
                    if extension in self.parent().supportedImageFormatList:
                        imgPaths.append(filePath)
                    elif extension == "def":
                        defPaths.append(filePath)
                    else:
                        if not os.path.isdir(filePath):
                            otherFilePaths.append(filePath)
                else:
                    webUrl.append(url)

            # nesne kutuphanede drag drop edildi ise embeded isaretleyebilmek icin.
            kutuphaneden_mi = False
            if event.source():
                if event.source().objectName() == "kev":  # kutuphane_ekran_viewport
                    kutuphaneden_mi = True
                # mini web browserdan tek imaj tasiyinca
                # secim yapip tasiyinca html tasiyor, onu mimedata.hasHtml() hallediyor.
                elif event.source().objectName() == "webview":

                    if imgPaths:
                        imageFilePath = imgPaths[0]

                        extension = os.path.splitext(imageFilePath)[1][1:]
                        # (zaten kullanmiyoruz asagidaki firefox ile ilgili kisimdaki gibi uzantilari ama)
                        # ayrica chrome da octet/streamden aldigimiz icin datayi, uzantiya gerek de olmayabilir.
                        # her hangi bir turde imaj dosyasi yine jpg olarak kaydedilemez mi acaba.
                        if extension:
                            # This is for image imports from ggle search like pages.
                            # They dont have standart file name structure.
                            if len(extension) > 4:
                                basename = "image-from-web.jpg"
                            else:
                                basename = os.path.basename(imageFilePath)
                        else:
                            basename = "image-from-web.jpg"

                        imageSavePath = self.get_unique_path_for_embeded_image(basename)

                        try:
                            shutil.copy2(imageFilePath, imageSavePath)
                        except Exception as e:
                            self.parent().log(self.tr("Could not embeded! --> {}").format(e), level=3, toLogOnly=False)
                            return

                        pixMap = QPixmap(imageSavePath)
                        # print(imageSavePath)
                        # pixMap = QPixmap(image)
                        rect = QRectF(pixMap.rect())
                        imageItem = Image(imageSavePath, event.scenePos(), rect, self.yaziRengi, self.arkaPlanRengi,
                                          QPen(self.scenePen), self.font())

                        imageItem.isEmbeded = True

                        self.parent().increase_zvalue(imageItem)
                        undoRedo.undoableAddItem(self.undoStack,
                                                 description=self.tr("drag && drop image from mini browser"),
                                                 scene=self, item=imageItem)
                        imageItem.reload_image_after_scale()
                        self.unite_with_scene_rect(imageItem.sceneBoundingRect())

                        if event.mimeData().hasFormat("text/uri-list"):
                            imageItem.originalSourceFilePath = str(event.mimeData().data("text/uri-list"),
                                                                   encoding='utf-8')
                        return

            if imgPaths:
                if kutuphaneden_mi:
                    # kutuphaneden simdilik tek nesne tasiyoruz, bir cok nesn secilebilir olsada
                    # act_add_multiple_images kullansak da imgPaths(cogul) ile, tek nesne ekliyoruz sahneye
                    isEmbeded = self.parent().sahneKutuphane.suruklenmekte_olan_nesne.isEmbeded
                    self.parent().act_add_multiple_images(pos, imgPaths, isEmbeded)
                else:
                    self.parent().act_add_multiple_images(pos, imgPaths)
            elif defPaths:
                self.parent().import_def_files_into_current_def_file(defPaths)
            elif otherFilePaths:
                if kutuphaneden_mi:
                    # kutuphaneden simdilik tek nesne tasiyoruz, bir cok nesn secilebilir olsada
                    # act_add_multiple_images kullansak da imgPaths(cogul) ile, tek nesne ekliyoruz sahneye
                    isEmbeded = self.parent().sahneKutuphane.suruklenmekte_olan_nesne.isEmbeded
                    self.parent().act_ekle_bircok_dosya_nesnesi(pos, otherFilePaths, isEmbeded)
                else:
                    self.parent().act_ekle_bircok_dosya_nesnesi(pos, otherFilePaths)

            elif webUrl:
                # for webUrl in webUrlPaths:
                textItem = Text(event.scenePos(), self.yaziRengi, self.arkaPlanRengi, QPen(self.scenePen),
                                self.font())
                textItem.set_document_url(self.tempDirPath)
                self.parent().increase_zvalue(textItem)

                textItem.setPlainText(webUrl[0].toString())
                textItem.textItemFocusedOut.connect(lambda: self.is_text_item_empty(textItem))
                self.parent().increase_zvalue(textItem)
                undoRedo.undoableAddItem(self.undoStack, self.tr("drag && drop url as text"), self, textItem)
                textItem.setTextInteractionFlags(Qt.NoTextInteraction)
                cursor = textItem.textCursor()
                cursor.clearSelection()
                textItem.setTextCursor(cursor)
                self.unite_with_scene_rect(textItem.sceneBoundingRect())

        elif event.mimeData().hasHtml():
            textItem = Text(event.scenePos(), self.yaziRengi, self.arkaPlanRengi, QPen(self.scenePen), self.font())
            textItem.set_document_url(self.tempDirPath)
            self.parent().increase_zvalue(textItem)
            # bu ikisi bir onceki eventtek kalan modifieri donduruyor. o yuzden query kullaniyoruz.
            # if event.modifiers() & Qt.ShiftModifier:
            # if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            if QApplication.queryKeyboardModifiers() == Qt.ShiftModifier:
                textItem.setPlainText(event.mimeData().text())
                textItem.textItemFocusedOut.connect(lambda: self.is_text_item_empty(textItem))
                self.parent().increase_zvalue(textItem)
                undoRedo.undoableAddItem(self.undoStack, self.tr("drag && drop text"), self, textItem)
                textItem.setTextInteractionFlags(Qt.NoTextInteraction)
                cursor = textItem.textCursor()
                cursor.clearSelection()
                textItem.setTextCursor(cursor)
            else:
                textItem.isPlainText = False
                textItem.setHtml(event.mimeData().html())
                # self.act_convert_to_plain_text(textItem)
                # textItem.setPlainText(event.mimeData().text())
                textItem.textItemFocusedOut.connect(lambda: self.is_text_item_empty(textItem))
                self.parent().increase_zvalue(textItem)
                undoRedo.undoableAddItem(self.undoStack, self.tr("drag && drop text"), self, textItem)
                textItem.setTextInteractionFlags(Qt.NoTextInteraction)
                cursor = textItem.textCursor()
                cursor.clearSelection()
                textItem.setTextCursor(cursor)

            self.unite_with_scene_rect(textItem.sceneBoundingRect())

        elif event.mimeData().hasText():
            textItem = Text(event.scenePos(), self.yaziRengi, self.arkaPlanRengi, QPen(self.scenePen), self.font())
            textItem.set_document_url(self.tempDirPath)
            # textItem.update_resize_handles()
            self.parent().increase_zvalue(textItem)
            textItem.setPlainText(event.mimeData().text())
            textItem.textItemFocusedOut.connect(lambda: self.is_text_item_empty(textItem))
            self.parent().increase_zvalue(textItem)
            undoRedo.undoableAddItem(self.undoStack, self.tr("drag && drop text"), self, textItem)
            textItem.setTextInteractionFlags(Qt.NoTextInteraction)
            cursor = textItem.textCursor()
            cursor.clearSelection()
            textItem.setTextCursor(cursor)
            self.unite_with_scene_rect(textItem.sceneBoundingRect())

        # print(event.mimeData().formats())
        # for f in event.mimeData().formats():
        #     print(f, event.mimeData().data(f))

        if event.mimeData().hasFormat("application/octet-stream"):
            # image = QImage(event.mimeData().data("application/octet-stream"))
            image = QImage()
            image.loadFromData(event.mimeData().data("application/octet-stream"))
            # print(mimeData.imageData())
            # print(image.byteCount())
            # print(event.mimeData().data("application/octet-stream"))

            imageURL = str(event.mimeData().data("text/uri-list"), encoding='utf-8')
            # extension = os.path.splitext(internetName)[1][1:].lower()
            extension = os.path.splitext(imageURL)[1][1:]
            # (zaten kullanmiyoruz asagidaki firefox ile ilgili kisimdaki gibi uzantilari ama)
            # ayrica chrome da octet/streamden aldigimiz icin datayi, uzantiya gerek de olmayabilir.
            # her hangi bir turde imaj dosyasi yine jpg olarak kaydedilemez mi acaba.
            if extension:
                # This is for image imports from ggle search like pages. They dont have standart file name structure.
                if len(extension) > 4:
                    basename = "image-from-web.jpg"
                else:
                    basename = os.path.basename(imageURL)
            else:
                basename = "image-from-web.jpg"

            imageSavePath = self.get_unique_path_for_embeded_image(basename)

            # imagePath = self.get_unique_path_for_embeded_image()
            # burda, ve genel olarak get_unique_path_for_embeded_image kullanan yerlerde problem olmus.
            image.save(imageSavePath)
            # print(image.byteCount())

            pixMap = QPixmap(imageSavePath)
            # print(imageSavePath)
            # pixMap = QPixmap(image)
            rect = QRectF(pixMap.rect())
            imageItem = Image(imageSavePath, event.scenePos(), rect, self.yaziRengi, self.arkaPlanRengi,
                              QPen(self.scenePen), self.font())

            imageItem.isEmbeded = True

            self.parent().increase_zvalue(imageItem)
            undoRedo.undoableAddItem(self.undoStack, description=self.tr("drag && drop image from browser"), scene=self,
                                     item=imageItem)
            imageItem.reload_image_after_scale()
            self.unite_with_scene_rect(imageItem.sceneBoundingRect())

            if event.mimeData().hasFormat("text/uri-list"):
                imageItem.originalSourceFilePath = str(event.mimeData().data("text/uri-list"), encoding='utf-8')

        # this is for firefox, with chrome we use "application/octet-stream" and there for, we do not need to download
        # the image, but with firefox we need to download the dragged image.
        # using "text/uri-list" would be more convenient but chrome has that mime format too and, when we drag an image
        # from chrome, it will add that image twice. so...
        # if event.mimeData().hasFormat("text/uri-list"):
        #     print(str(event.mimeData().data("text/uri-list"), encoding='ascii'))
        if event.mimeData().hasFormat("_NETSCAPE_URL"):
            # image = QImage(event.mimeData().data("application/octet-stream"))
            # pix = QPixmap()
            # pix.loadFromData(event.mimeData().data("text/unicode"))
            # image = QImage(pix)
            # url = str(event.mimeData().data("_NETSCAPE_URL"), encoding='utf-8').split('\n')[0]
            imageURL = str(event.mimeData().data("text/uri-list"), encoding='utf-8')
            # str(QByteArray, encoding='ascii')

            # bazi path temizleme islmeleri -basla
            # from urllib.parse import urlparse
            # parsed = urlparse(imageURL)
            # par = parse.parse_qs(parsed.query)
            # print(imageURL)
            # print(parsed)
            # cleanedPath = os.path.join(parsed.netloc, parsed.path)
            # for ex: www.example.com/example.jpg?param=123
            # cleanedPath = "%s://%s%s" % (parsed.scheme, parsed.netloc, parsed.path)
            # print(cleanedPath)

            extension = os.path.splitext(imageURL)[1][1:].lower()
            # fakat chromeda ggledan drop edebiliyoruz..
            # ayrica uzantisi olmayan imajlari da drop edebiliyoruz. cunku mime data da gomulu imaj bilgisi var
            # ffoxta indirmek gerekiyor dosyayi.
            # denemek lazim aslinda uzantisi olmayan imaj dosyasi adresi ile ffox icin.
            # o zaman asagidaki kodun ilgili kismi tekrar aktive edilebilir.

            # if extension:
            #     # This is for image imports from ggle search like pages. They dont have standart file name structure.
            #     if len(extension) > 4:
            #         from urllib import parse
            #         # imageURL = parse.unquote(imageURL)
            #         # non-standart key : parse result below, needs a key with a ggle domain name.
            #         # different countries have different ggle adresses. so this is cancelled for now.
            #         yeniImageURL = parse.parse_qs(imageURL)["https://www.ggle.com/imgres?imgurl"]
            #         if yeniImageURL:
            #             imageURL = yeniImageURL
            #             basename = os.path.basename(imageURL)
            #         else:
            #             basename = "image-from-web.jpg"
            #
            #     else:
            #         basename = os.path.basename(imageURL)
            # else:
            #     basename = "image-from-web.jpg"

            if extension not in self.parent().supportedImageFormatList:
                self.parent().log(
                    "Could not load image: Could not find the direct link to the image or image type is unsupported.",
                    7000, 2)
                return None

            # print(mimeData.imageData())
            # print(image.byteCount())

            imageSavePath = self.get_unique_path_for_embeded_image(os.path.basename(imageURL))

            self.dThread = QThread()
            self.dWorker = DownloadWorker()
            self.dWorker.moveToThread(self.dThread)
            self.dWorker.finished.connect(self.dThread_finished)
            self.dWorker.failed.connect(self.dthread_clean)
            self.dWorker.log.connect(self.parent().log)

            self.dThread.start()
            self.dWorker.downloadWithThread.emit(imageURL, imageSavePath, event.scenePos())

        # TODO: this maybe unnecessary.
        if event.mimeData().hasImage():
            # if mimeData.imageData():

            # pixMap = QPixmap(item["filePath"]).scaled(rect.size().toSize(), Qt.KeepAspectRatio)
            # filePath = "/home/n00/CODE/pyCharm/Defter/imaaaj.jpg"

            #  burda QImage icine almak lazimi, yoksa image none olabiliyor, if mimeData.imageData()
            #  veya  if mimeData.hasImage() dogru dondursede QImage icine almazsak none oluyor image.
            image = QImage(event.mimeData().imageData())
            # print(mimeData.imageData())
            # print(image.byteCount())
            # imagePath = self.get_unique_path_for_embeded_image()
            imagePath = self.get_unique_path_for_embeded_image("image.jpg")
            image.save(imagePath)
            pixMap = QPixmap(imagePath)
            # pixMap = QPixmap(image)
            rect = QRectF(pixMap.rect())
            imageItem = Image(imagePath, event.scenePos(), rect, self.yaziRengi, self.arkaPlanRengi,
                              QPen(self.scenePen), self.font())

            imageItem.isEmbeded = True

            self.parent().increase_zvalue(imageItem)
            undoRedo.undoableAddItem(self.undoStack, description=self.tr("drag && drop image"), scene=self,
                                     item=imageItem)
            imageItem.reload_image_after_scale()
            self.unite_with_scene_rect(imageItem.sceneBoundingRect())

        event.accept()

        # super(Scene, self).dropEvent(event)

    # ---------------------------------------------------------------------
    @Slot(str, str, QPointF, QObject)
    def dThread_finished(self, url, imagePath, scenePos, worker):

        pixMap = QPixmap(imagePath)
        # pixMap = QPixmap(image)
        rect = QRectF(pixMap.rect())

        imageItem = Image(imagePath, scenePos, rect, self.yaziRengi, self.arkaPlanRengi,
                          QPen(self.scenePen), self.font())
        imageItem.originalSourceFilePath = url
        imageItem.isEmbeded = True

        self.parent().increase_zvalue(imageItem)
        undoRedo.undoableAddItem(self.undoStack, description=self.tr("drag && drop image from browser"), scene=self,
                                 item=imageItem)

        imageItem.reload_image_after_scale()
        # imageItem.update()
        self.unite_with_scene_rect(imageItem.sceneBoundingRect())

        self.dthread_clean()

    # ---------------------------------------------------------------------
    @Slot(QObject)
    def dthread_clean(self, worker):
        self.dThread.quit()
        self.dThread.deleteLater()
        self.dWorker.deleteLater()
        del self.dThread
        del self.dWorker
