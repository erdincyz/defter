# -*- coding: utf-8 -*-
# .


__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/27/16'

import os
import shutil

from shiboken6 import Shiboken
from PySide6.QtCore import Qt, QRectF, QPointF, Slot, Signal, QThread, QLineF, QObject
from PySide6.QtGui import QPixmap, QPen, QImage, QUndoStack, QColor, QFont
from PySide6.QtWidgets import QApplication, QGraphicsScene
from .arac import Arac
from .nesneler.yuvarlakFircaBoyutu import YuvarlakFircaBoyutu
from .treeView import TreeView
from .selectionQueue import SelectionQueue
from .nesneler.image import Image
from .nesneler.line import LineItem
from .nesneler.text import Text
from .nesneler.rect import Rect
from .nesneler.ellipse import Ellipse
from .nesneler.path import PathItem
from .nesneler.mirrorLine import MirrorLine
from .threadWorkers import DownloadWorker
from .yw.yuzenWidget import YuzenWidget
from . import undoRedoFonksiyonlar as undoRedo
from . import shared


########################################################################
class Scene(QGraphicsScene):
    # nesneTasindi = Signal(QGraphicsItem, QPointF)
    nesneTasindi = Signal(object, QPointF)

    # textItemSelected = Signal(QGraphicsTextItem)

    # ---------------------------------------------------------------------
    def __init__(self, tempDirPath, parent=None):
        super(Scene, self).__init__(parent)

        # gradient = QRadialGradient(0, 0, 10)
        # gradient.setSpread(QGradient.RepeatSpread)
        # self.setBackgroundBrush(gradient)

        # her belgede arac ozellikleri farkli olsun diye classta degil de burda tanimladik
        self.SecimAraci = Arac('secimAraci')
        self.OkAraci = Arac('okAraci')
        self.KutuAraci = Arac('kutuAraci')
        self.YuvarlakAraci = Arac('yuvarlakAraci')
        self.KalemAraci = Arac('kalemAraci')
        self.YaziAraci = Arac('yaziAraci')
        self.ResimAraci = Arac('resimAraci')
        self.VideoAraci = Arac('videoAraci')
        self.DosyaAraci = Arac('dosyaAraci')
        self.AynalaXAraci = Arac('aynalaXAraci')
        self.AynalaYAraci = Arac('aynalaYAraci')
        self.ResimKirpAraci = Arac('resimKirpAraci')

        self.araclar = (self.SecimAraci, self.OkAraci, self.KutuAraci, self.YuvarlakAraci, self.KalemAraci,
                        self.YaziAraci, self.ResimAraci, self.VideoAraci, self.DosyaAraci, self.AynalaXAraci,
                        self.AynalaYAraci, self.ResimKirpAraci)

        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        self.tempDirPath = tempDirPath
        # self.setFont(yaziTipi)

        self.sonZDeger = 0

        # self.tempDirPath = tempfile.TemporaryDirectory().name
        # self.tempDirPath = tempfile.TemporaryDirectory()

        # self.saveFilePath = None

        self.aktifArac = self.SecimAraci

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

        self.tasinanNesne = None
        self.tasinanNesnelerinListesi = []
        self.nesneTasindi.connect(self.sinyal_nesne_tasindi)

        self.activeItem = None
        self._acceptDrops = True

        self.undoRedo = undoRedo

        # DIKKAT: bu item tutuyor, bunu sildikten sonra bir de scene.clear()
        # (tum_nesneleri_sil() e gecildi sonrasinda clear() yerine) gerekti bellek sızıntısı olmamasi icin
        self._kimlik_nesne_sozluk = {}

    # ---------------------------------------------------------------------
    def tum_nesneleri_sil(self):
        # self.clear()
        for nesne in self.items():
            if Shiboken.isValid(nesne):
                Shiboken.delete(nesne)
                # print(Shiboken.isValid(nesne))
                # del nesne
        # print(len(self.items()))

    # ---------------------------------------------------------------------
    def get_properties_for_save(self):

        aracOzellikleriSozluk = {}
        for arac in self.araclar:
            aracOzellikleriSozluk[arac.tip] = arac.oku_ozellikler()

        view = self.views()[0]
        properties = {
            "sceneRect": self.sceneRect(),
            "sonZDeger": self.sonZDeger,
            # "embededImageCounter": self.embededImageCounter,
            "backgroundBrush": view.backgroundBrush(),
            "backgroundImagePath": view.backgroundImagePath,
            "backgroundImagePathIsEmbeded": view.backgroundImagePathIsEmbeded,
            # "viewMatrix": self.views()[0].matrix()
            "viewTransform": view.transform(),
            "viewHorizontalScrollBarValue": view.horizontalScrollBar().value(),
            "viewVerticalScrollBarValue": view.verticalScrollBar().value(),
            "aracOzellikleriSozluk": aracOzellikleriSozluk
        }
        return properties

    # ---------------------------------------------------------------------
    def arac_ozellikleri_yukle(self, aracOzellikleriSozluk):
        if aracOzellikleriSozluk:
            for arac in self.araclar:
                try:
                    arac.yaz_ozellikler(aracOzellikleriSozluk[arac.tip])
                except Exception as e:
                    pass

    # ---------------------------------------------------------------------
    def nesne_ozellikleri_guncelle(self):
        # self.parent().fircaDirektDegerGir(self.aktifArac.kalem.widthF())

        # self.parent()._pen = QPen(self.aktifArac.kalem)
        self.parent().change_line_style_options(self.aktifArac.kalem)
        # self.parent().cizgiRengi = self.cizgiRengi = self.aktifArac.cizgiRengi
        self.parent().degistir_cizgi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=False)

        # self.parent().currentFont = self.aktifArac.yaziTipi
        # self.setFont(self.aktifArac.yaziTipi)

        # self.parent().yaziRengi = self.yaziRengi = self.aktifArac.yaziRengi
        # self.parent().arkaPlanRengi = self.arkaPlanRengi = self.aktifArac.arkaPlanRengi

        self.parent().degistir_yazi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=False)
        self.parent().degistir_nesne_arkaplan_rengi_ikonu()
        self.parent().change_font_point_sizef_spinbox_value(self.aktifArac.yaziBoyutu)
        self.parent().change_line_style_options(self.aktifArac.kalem)
        self.parent().change_font_combobox_value(self.aktifArac.yaziTipi)

    # ---------------------------------------------------------------------
    def aktif_arac_degistir(self, aktifArac, itemText=None, dosyaYolu=None, pos=None):
        # parca bir cok yerde bunu kapatmaktansa basta kapatıp
        # asagida gerekirse aciyoruz
        # setMouseTracking kullanan araclardan sadece KalemAraci tekrar tekrar cizim yapiyor
        # digerleri tek islem yapiyor ve tooldan cikiyor yani aktif_arac_degistir yani burasi cagriliyor
        # DrawPathToolda surekli cizim yapabildiğimiz için kapatmaya gerek yok
        # aslında bunu da fircaBoyutuItem icin aciyoruz sadece (ilerde baska seylerde de kullanabiliriz)
        # GUNCELLEME: self.views()[0].hasMouseTracking(), False donduruyor ama tracking yapiyor!?
        # sonra self.views()[0].setMouseTracking(False) veya True dersek bu sefer hover eventler calismamaya basliyor
        # Fonksiyonallik devam etsin diye su an kapatıyoruz alt satırı
        # ve tum self.views()[0].setMouseTracking(False veya True) lari, derinlemesine bakmak lazim.
        # view da acik oldugu halde false dondurme ihtimali, fare tiklamadan da move event cagriliyor
        # self.views()[0].setMouseTracking(False)
        self.finish_interactive_tools()

        self.aktifArac = aktifArac
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

        # pixmap.setMask(pixmap.mask())
        # cursor = QCursor(pixmap.scaled(QSize(20, 20)))
        self.parent().setCursor(self.aktifArac.imlec)

        if aktifArac == self.SecimAraci:
            # finish_interactive_tools ta alt satir cagriliyor
            # self.parent().setCursor(Qt.ArrowCursor)
            return

        if aktifArac == self.OkAraci:
            # self.views()[0].setMouseTracking(True)
            self.drawLineItem = None
            self.nesne_ozellikleri_guncelle()
            return
        elif aktifArac == self.KalemAraci:
            # self.views()[0].setMouseTracking(True)
            self.pathItem = None
            self.nesne_ozellikleri_guncelle()
            return

        elif aktifArac == self.AynalaXAraci:
            r = self.views()[0].get_visible_rect()
            self.mirrorLineItem = MirrorLine(posFeedback=pos, axis="x")
            self.mirrorLineItem.setLine(pos.x(),
                                        r.top(),
                                        pos.x(),
                                        r.bottom())

            # self.views()[0].setMouseTracking(True)
            self.addItem(self.mirrorLineItem)
            self.mirrorLineItem.updateScale()
            return

        elif aktifArac == self.AynalaYAraci:
            r = self.views()[0].get_visible_rect()
            self.mirrorLineItem = MirrorLine(posFeedback=pos, axis="y")
            self.mirrorLineItem.setLine(r.left(),
                                        pos.y(),
                                        r.right(),
                                        pos.y())

            # self.views()[0].setMouseTracking(True)
            self.addItem(self.mirrorLineItem)
            self.mirrorLineItem.updateScale()
            return
        elif aktifArac == self.ResimKirpAraci:
            self.activeItem._isCropping = True
            return

        self.nesne_ozellikleri_guncelle()

    # ---------------------------------------------------------------------
    def unite_with_scene_rect(self, rect):
        # unitedRect = self.sceneRect().united(rect)
        unitedRect = rect | self.sceneRect()
        visRect = self.views()[0].get_visible_rect()
        if unitedRect.size().width() * unitedRect.size().height() > visRect.size().width() * visRect.size().height():
            # self.setSceneRect(visRect.united(unitedRect))
            self.setSceneRect(unitedRect)
        # else:
        #     self.setSceneRect(visRect)
        self.parent().act_yazici_sayfa_kenar_cizdir()

        # mouseRelease a koydugumuz icin iptal bu.
        # self.parent().tw_sayfa_guncelle()

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
                            "defterHtml-{}-{}-{}".format(self.parent().cModel.embededImageCounter,
                                                         shared.kim(kac_basamak=5),
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
        if item.type() == shared.GROUP_ITEM_TYPE:
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
    def sinyal_nesne_tasindi(self, movedItem, eskiPosition):
        # self.undoStack.push(UndoableMove(self.tr("Item moved"), movedItem, eskiPosition))
        undoRedo.undoableMove(self.undoStack, self.tr("Item moved"), movedItem, eskiPosition)

    # ---------------------------------------------------------------------
    def finish_interactive_tools(self, kapat=True):

        if self.mirrorLineItem:
            self.removeItem(self.mirrorLineItem)
            self.mirrorLineItem = None

        if self.aktifArac == self.KalemAraci:
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
                            if nesne.type() == shared.IMAGE_ITEM_TYPE:
                                ustuneCizilenResimNesnesi = nesne
                                break

                    if ustuneCizilenResimNesnesi:
                        self.undoStack.beginMacro(self.tr("draw on image"))
                        undoRedo.undoableAddItem(self.undoStack, description=self.tr("add path"), scene=self,
                                                 item=self.pathItem)
                        yeniPos = ustuneCizilenResimNesnesi.mapFromScene(self.pathItem.scenePos())
                        undoRedo.undoableParent(self.undoStack, self.tr("_parent"), self.pathItem,
                                                ustuneCizilenResimNesnesi, yeniPos)
                        self.undoStack.endMacro()
                    else:
                        undoRedo.undoableAddItem(self.undoStack, description=self.tr("add path"), scene=self,
                                                 item=self.pathItem)

                    self.pathItem = None
                else:
                    self.removeItem(self.pathItem)
                    self.pathItem = None

                return

        elif self.aktifArac == self.OkAraci:

            if self.drawLineItem:
                if self.drawLineItem.length() > 0:

                    self.removeItem(self.drawLineItem)
                    undoRedo.undoableAddItem(self.undoStack, description=self.tr("add line"), scene=self,
                                             item=self.drawLineItem)
                    self.drawLineItem = None
                else:
                    self.removeItem(self.drawLineItem)
                    self.drawLineItem = None

        elif self.aktifArac == self.ResimKirpAraci:
            # diger durumlar icin Image.hoverLeaveEvent() kullanildi.
            if self.activeItem and self.activeItem.type() == shared.IMAGE_ITEM_TYPE:
                self.activeItem.finish_crop()

        self.secim_aracina_gec()

    # ---------------------------------------------------------------------
    def secim_aracina_gec(self):
        # GUNCELLEME (set tool icindeki guncellemeye bakiniz)
        # Alt satir simdilik iptal
        # self.views()[0].setMouseTracking(False)
        self.aktifArac = self.SecimAraci
        self.parent().setCursor(Qt.CursorShape.ArrowCursor)
        # self.deleteLater()
        self.parent().actionSwitchToSelectionTool.setChecked(True)
        self.parent().aracIkonuEtiketi.setPixmap(self.parent().ikonSecimAraci)

    # ---------------------------------------------------------------------
    def _fircaBoyutuItem_olustur(self):
        rect = QRectF(-self.KalemAraci.kalem.widthF() / 2,
                      -self.KalemAraci.kalem.widthF() / 2,
                      self.KalemAraci.kalem.widthF(),
                      self.KalemAraci.kalem.widthF())
        pen = QPen(self.KalemAraci.kalem.color(), 1,
                   Qt.PenStyle.DashLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.fircaBoyutuItem = YuvarlakFircaBoyutu(self.fircaSonPos, rect, QColor.fromRgbF(0, 0, 0, 0),
                                                   # self.KalemAraci.kalem,
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
    #     if self.aktifArac == self.KalemAraci:
    #         if event.modifiers()== Qt.KeyboardModifier.ShiftModifier:
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
        if self.aktifArac == self.OkAraci:
            if angleDeltaY > 0:
                cap = self.parent().fircaBuyult()
            else:
                cap = self.parent().fircaKucult()

            self.drawLineItem.setCizgiKalinligi(cap)

        elif self.aktifArac == self.KalemAraci:

            if angleDeltaY > 0:
                cap = self.parent().fircaBuyult()
            else:
                cap = self.parent().fircaKucult()

            self.pathItem.setCizgiKalinligi(cap)

            if self.fircaBoyutuItem:
                rect = QRectF(-cap / 2, -cap / 2, cap, cap)
                self.fircaBoyutuItem.setRect(rect)

    # ---------------------------------------------------------------------
    def shift_drag_ile_firca_boyu_degistir(self, yariCap):
        if self.aktifArac == self.KalemAraci:

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
            if self.activeItem.type() == shared.TEXT_ITEM_TYPE:
                if not self.activeItem.hasFocus():
                    devam = True

            # bu ikisinde tempTextItem yok
            elif self.activeItem.type() == shared.GROUP_ITEM_TYPE:
                devam = True
            # bu ikisinde tempTextItem yok
            elif self.activeItem.type() == shared.LINE_ITEM_TYPE:
                devam = True
            # geri kalanlarda tempTextItem var, (nesne uzerine yazi yazdigimiz item bu)
            else:
                if not self.activeItem.tempTextItem:
                    devam = True

        # tek nesne icin, ne kadar secili nesne olursa olsun , yani self.activeItem icin
        # if devam:
        #     eskiPos = self.activeItem.pos()
        #     self.activeItem.moveBy(x, y)
        #     self.sinyal_nesne_tasindi(self.activeItem, eskiPos)

        # butun secili nesneler icin
        if devam:
            items = self.get_selected_top_level_items()

            self.undoStack.beginMacro(self.tr("Item(s) moved"))

            for item in items:
                eskiPos = item.pos()
                item.moveBy(x, y)
                self.sinyal_nesne_tasindi(item, eskiPos)

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
        textItem = Text(scenePos, self.YaziAraci.yaziRengi,
                        self.YaziAraci.arkaPlanRengi,
                        QPen(self.YaziAraci.kalem),
                        QFont(self.YaziAraci.yaziTipi))
        textItem.set_document_url(self.tempDirPath)
        textItem.textItemFocusedOut.connect(self.is_text_item_empty)
        self.parent().increase_zvalue(textItem)
        # textItem.textItemSelectedChanged.connect(self.textItemSelected)
        # self.addItem(textItem)
        undoRedo.undoableAddItem(self.undoStack, description=self.tr("add text"), scene=self, item=textItem)
        textItem.setFocus()
        textItem.setSelected(True)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:

            # drawlinetool kontrolune gerek yok esasen cunku ilk tiklamada cizgiyi bitirip sahneye ekliyor.
            # ama coklu cizgi eklenirse hatirlatma olsun diye..
            if not self.aktifArac == self.KalemAraci and not self.aktifArac == self.OkAraci:
                if not self.itemAt(event.scenePos(), self.views()[0].transform()):
                    # modifier yoksa olustur. cunku mesela ctrl basili ise yaiNesnesi olusturup,hemen yazi nesnesine
                    # gidiyor ciftTiklama o da miniWebGezgini aciyor ve yazi bos oldugu ici siliniyor
                    # sahneye ctrl veya ctrl+shift ile cift tiklayina miniWebGezgini acmis oluyoruz.
                    if event.modifiers() == Qt.KeyboardModifier.NoModifier:  # 0x00000000
                        self.create_empty_text_object_with_double_click(event.scenePos())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.views()[0].zoomToFit()
        super(Scene, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:

            if self.aktifArac == self.SecimAraci:
                # if event.modifiers() == Qt.KeyboardModifier.AltModifier:
                #     duplicateItem = self.itemAt(event.scenePos())
                #     self.parent().act_copy()
                #     self.parent().act_paste()
                #     self.set_modified(True)

                mousePos = event.buttonDownScenePos(Qt.MouseButton.LeftButton)
                self.tasinanNesne = self.itemAt(mousePos, self.views()[0].transform())
                if self.tasinanNesne:  # and event.button() == Qt.LeftButton
                    if self.tasinanNesne.type() == shared.TEMP_TEXT_ITEM_TYPE:
                        return QGraphicsScene.mousePressEvent(self, event)

                    while self.tasinanNesne.ustGrup:
                        self.tasinanNesne = self.tasinanNesne.ustGrup

                    # ustNesne = self.tasinanNesne.parentItem()
                    # if ustNesne:
                    #     if ustNesne.type() == shared.GROUP_ITEM_TYPE:
                    #         if self.tasinanNesne in ustNesne.allNonGroupGroupChildren:
                    #             self.tasinanNesne = ustNesne
                    self.eskiPosTasinanNesne = self.tasinanNesne.pos()
                    self.tasinanNesnelerinListesi = []
                    selectedItems = self.selectedItems()
                    # hic birsey secili degil iken, tek itema tiklayip tasiyinca, self.selectedItems
                    # bos donuyor. birden fazla item tasimak icin zaten onlar secili olmak durumunda.
                    # dolayisi ile normal calisiyor. bu yuzden manual ekliyoruz
                    # eger sahnede secili item yok ve de self.tasinanNesne var is demek ki,
                    # daha selection guncellenmemis oldugundan. gibi. neden guncellenmiyor
                    # cunku event daha yeni basliyor. qt itemlari secmek icin gerekli islemleri yapmamis oluyor.
                    # super kullandigimizda da problem oldu.
                    #  !!! bu safer de iki tane baska item secili mesela secili olmayan bir itemi tutup tasiyinca,
                    # hali hazirda secili olanlar undo edildi onlar da hareket ettirilmedikleri icin
                    # sahnede bir sey olmadi. yine dolayisi ile bir kontrol daha ekledik
                    # eger self.tasinanNesne selectedItemslar iceresinde yoksa diye.
                    if selectedItems:
                        if self.tasinanNesne in selectedItems:
                            for item in selectedItems:
                                self.tasinanNesnelerinListesi.append([item, item.pos()])
                        else:
                            self.tasinanNesnelerinListesi.append([self.tasinanNesne, self.tasinanNesne.pos()])
                    else:
                        self.tasinanNesnelerinListesi.append([self.tasinanNesne, self.tasinanNesne.pos()])

                return QGraphicsScene.mousePressEvent(self, event)

            elif self.aktifArac == self.KutuAraci:

                # rect = QRectF(event.scenePos(), self.itemSize).translated(-self.itemSize.width() / 2,
                #                                                           -self.itemSize.height() / 2)

                # rect = QRectF(event.scenePos(), QSizeF(1, 1))
                rect = QRectF(0, 0, 1, 1)
                item = Rect(event.scenePos(), rect, self.KutuAraci.yaziRengi, self.KutuAraci.arkaPlanRengi,
                            QPen(self.KutuAraci.kalem), QFont(self.KutuAraci.yaziTipi))
                self.parent().increase_zvalue(item)

                # if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                item.hide_resize_handles()
                self.lastItem = item
                # self.addItem(item)
                undoRedo.undoableAddItem(self.undoStack, description=self.tr("add rectangle"), scene=self, item=item)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.aktifArac == self.YuvarlakAraci:
                # rect = QRectF(event.scenePos(), self.itemSize).translated(-self.itemSize.width() / 2,
                #                                                           -self.itemSize.height() / 2)
                # rect = QRectF(event.scenePos(), QSizeF(1, 1))
                rect = QRectF(0, 0, 1, 1)
                item = Ellipse(event.scenePos(), rect, self.YuvarlakAraci.yaziRengi, self.YuvarlakAraci.arkaPlanRengi,
                               QPen(self.YuvarlakAraci.kalem),
                               QFont(self.YuvarlakAraci.yaziTipi))
                self.parent().increase_zvalue(item)
                item.hide_resize_handles()
                self.lastItem = item
                # self.addItem(item)
                undoRedo.undoableAddItem(self.undoStack, description=self.tr("add ellipse"), scene=self, item=item)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.aktifArac == self.YaziAraci:

                textItem = Text(event.scenePos(),
                                self.YaziAraci.yaziRengi,
                                self.YaziAraci.arkaPlanRengi,
                                QPen(self.YaziAraci.kalem),
                                QFont(self.YaziAraci.yaziTipi),
                                text=self.itemText)
                textItem.set_document_url(self.tempDirPath)
                self.parent().increase_zvalue(textItem)
                textItem.textItemFocusedOut.connect(self.is_text_item_empty)
                # textItem.textItemSelectedChanged.connect(self.textItemSelected)
                # self.addItem(textItem)
                undoRedo.undoableAddItem(self.undoStack, description=self.tr("add text"), scene=self, item=textItem)
                # self.itemText = None
                self.secim_aracina_gec()
                # self.aktifArac = self.SecimAraci
                # self.parent().setCursor(Qt.ArrowCursor)
                # self.parent().actionSwitchToSelectionTool.setChecked(True)
                return QGraphicsScene.mousePressEvent(self, event)

            # elif self.aktifArac == self.ResimAraci:
            #     pos = event.scenePos()
            #     pixMap = QPixmap(self.dosyaYolu).scaled(self.itemSize.toSize(), Qt.KeepAspectRatio)
            #     rect = QRectF(pixMap.rect())
            #     rect.moveTo(pos.x() - rect.width() / 2, pos.y() - rect.height() / 2)
            #     self.addItem(
            #         Image(self.dosyaYolu, pixMap, rect, self.ResimAraci.yaziRengi, self.ResimAraci.arkaPlanRengi,
            #               self.ResimAraci.kalem))
            #     pixMap = None
            #     # self.dosyaYolu = None

            elif self.aktifArac == self.ResimAraci:
                self.parent().lutfen_bekleyin_goster()
                self.parent().ekle_resim_direkt(self.dosyaYolu, event.scenePos())
                self.secim_aracina_gec()
                self.parent().lutfen_bekleyin_gizle()
                # self.aktifArac = self.SecimAraci
                # self.parent().setCursor(Qt.ArrowCursor)
                # self.parent().actionSwitchToSelectionTool.setChecked(True)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.aktifArac == self.VideoAraci:
                self.parent().lutfen_bekleyin_goster()
                self.parent().ekle_video_direkt(self.dosyaYolu, event.scenePos())
                self.secim_aracina_gec()
                self.parent().lutfen_bekleyin_gizle()
                # self.aktifArac = self.SecimAraci
                # self.parent().setCursor(Qt.ArrowCursor)
                # self.parent().actionSwitchToSelectionTool.setChecked(True)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.aktifArac == self.DosyaAraci:
                self.parent().lutfen_bekleyin_goster()
                self.parent().ekle_dosya_direkt(self.dosyaYolu, event.scenePos())
                self.secim_aracina_gec()
                self.parent().lutfen_bekleyin_gizle()
                # self.aktifArac = self.SecimAraci
                # self.parent().setCursor(Qt.ArrowCursor)
                # self.parent().actionSwitchToSelectionTool.setChecked(True)
                return QGraphicsScene.mousePressEvent(self, event)

            elif self.aktifArac == self.KalemAraci:
                self.views()[0].setDragModeNoDrag()
                if not self.pathItem:
                    self.pathItem = PathItem(event.scenePos(), self.KalemAraci.yaziRengi, self.KalemAraci.arkaPlanRengi,
                                             QPen(self.KalemAraci.kalem),
                                             QFont(self.KalemAraci.yaziTipi))
                    self.parent().increase_zvalue(self.pathItem)
                    # self.pathItem.move_start_point(event.scenePos())
                    self.pathItem.move_start_point()
                    self.addItem(self.pathItem)
                else:
                    if not self.pathItem.intersects:
                        # if event.modifiers() & Qt.ControlModifier:
                        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
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

            elif self.aktifArac == self.OkAraci:
                self.views()[0].setDragModeNoDrag()
                if not self.drawLineItem:
                    self.drawLineItem = LineItem(event.scenePos(), QPen(self.OkAraci.kalem),
                                                 yaziRengi=self.OkAraci.yaziRengi,
                                                 font=QFont(self.OkAraci.yaziTipi))
                    self.parent().increase_zvalue(self.drawLineItem)
                    # self.drawLineItem.move_start_point(event.scenePos())
                    self.drawLineItem.move_start_point()
                    self.addItem(self.drawLineItem)
                    ustuneOkCizilenItem = self.itemAt(event.scenePos(), self.views()[0].transform())
                    if ustuneOkCizilenItem:
                        enustGrup = ustuneOkCizilenItem.varsaEnUsttekiGrubuGetir()
                        if enustGrup:
                            ustuneOkCizilenItem = enustGrup
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
                        ustuneOkunIkinciNoktasiCizilenNesne = ustuneOkCizilenItemList[0]
                        enustGrup = ustuneOkunIkinciNoktasiCizilenNesne.varsaEnUsttekiGrubuGetir()
                        if enustGrup:
                            ustuneOkunIkinciNoktasiCizilenNesne = enustGrup
                        # okun iki noktasi da ayni nesne ustunde olacak ise
                        # burda ikinci noktayi koydugumuzda, okun  nesneye olan ilk bagini cozup
                        # sonra hiç bir noktasini baglamadan normal parent ediyoruz
                        # asagi tasindi
                        if self.drawLineItem in ustuneOkunIkinciNoktasiCizilenNesne.oklar_dxdy_nokta:
                            # undoRedo.undoableAddItem ile ekledikten sonra parent ediyoruz
                            # bu asamada yaparsak gecici oku parent etmis oluruz ki siliniyor zaten az sonra
                            oku_normal_parent_et = True

                        else:
                            # beklenen normal islem bu
                            # okun ilk noktasi boslukta ya da baska nesneye bagli
                            # burda da okun ikinci noktasini uzerine tikladigimiz nesneye bagliyoruz
                            ustuneOkunIkinciNoktasiCizilenNesne.ok_ekle(self.drawLineItem, event.scenePos(), 2)

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
                        ustuneOkunIkinciNoktasiCizilenNesne.ok_sil(self.drawLineItem)
                        # su an okun 2 noktasi da hic bir yere baglai degil, okta da baglanmis_nesneler = {}
                        yeniPos = ustuneOkunIkinciNoktasiCizilenNesne.mapFromScene(self.drawLineItem.scenePos())
                        undoRedo.undoableParent(self.undoStack, self.tr("_parent"), self.drawLineItem,
                                                ustuneOkunIkinciNoktasiCizilenNesne, QPointF(yeniPos))

                    self.drawLineItem = None

                    self.secim_aracina_gec()
                return QGraphicsScene.mousePressEvent(self, event)
                # super(Scene, self).mousePressEvent(event)

            elif self.aktifArac == self.AynalaXAraci:
                self.parent().act_mirror_x(event.scenePos())  # bu finish_interactive_toolsu da cagiriyor.

            elif self.aktifArac == self.AynalaYAraci:
                self.parent().act_mirror_y(event.scenePos())  # bu finish_interactive_toolsu da cagiriyor.

            # if not event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            # if not event.modifiers() == Qt.KeyboardModifier.AltModifier:
            #     if not self.aktifArac == self.KalemAraci:
            #         self.aktifArac = self.SecimAraci
            #         self.parent().setCursor(Qt.ArrowCursor)
            #
            #     self.pathItem = None
        super(Scene, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        if self.aktifArac == self.KalemAraci:
            self.fircaSonPos = event.scenePos()

        if self.pathItem and self.aktifArac == self.KalemAraci:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier and self.fircaBoyutuItem:

                # self.fircaBoyutuItem.setPos(QPointF(event.scenePos().x(), event.scenePos().y()))
                fark = QLineF(self.fircaBoyutuItem.pos(), event.scenePos()).length()
                # fark = sqrt((self.fircaBoyutuItem.pos().x() - event.scenePos().x()) ** 2
                #             + (event.scenePos().y() - self.fircaBoyutuItem.pos().y()) ** 2)

                # fark = math.hypot(x2 - x1, y2 - y1)
                self.shift_drag_ile_firca_boyu_degistir(fark / 2)
            else:
                # (eski bilgi) or'laniyor -> 0x00000000 = hicbiri , 0x00000001 sol , 0x00000002 sag  0x00000004 orta
                # burda event.button NoButton diyor , buttons lazim
                if event.buttons() == Qt.MouseButton.LeftButton:  # mouse sol tus basili
                    # self.pathItem.replace_last(event.scenePos())
                    self.pathItem.append(event.scenePos())
                    # self.pathItem.check_if_at_start(event.scenePos())
                    # event.accept()
                    # return QGraphicsScene.mouseMoveEvent(self, event)
                    event.ignore()

                else:
                    if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                        # self.pathItem.replace_last(event.scenePos())
                        self.pathItem.temp_append_and_replace_last(event.scenePos())
                        self.pathItem.check_if_at_start(event.scenePos())
                        # event.accept()
                        # return QGraphicsScene.mouseMoveEvent(self, event)
                        return
                    else:
                        return

        if self.drawLineItem and self.aktifArac == self.OkAraci:
            self.drawLineItem.temp_append(event.scenePos())
            # self.drawLineItem.line().setP2(event.scenePos())
            # self.drawLineItem.setLine(QLineF(self.line.line().p1(), mouseEvent.scenePos()))

            # return QGraphicsScene.mouseMoveEvent(self, event)
            return

        if self.aktifArac == self.AynalaXAraci:
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

        if self.aktifArac == self.AynalaYAraci:
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

        self.parent().tw_sayfa_guncelle()

        if event.button() == Qt.MouseButton.LeftButton:
            self.views()[0].setDragModeRubberBandDrag()
            # if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            #     if self.aktifArac == self.KutuAraci or self.aktifArac == self.YuvarlakAraci:
            #         self.aktifArac = self.SecimAraci
            #         self.parent().setCursor(Qt.ArrowCursor)
            if self.aktifArac == self.KalemAraci:
                # # return QGraphicsScene.mousePressEvent(self, event)
                # if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                #     return QGraphicsScene.mouseReleaseEvent(self, event)
                # else:
                #     if self.pathItem:
                #         self.finish_interactive_tools(kapat=False)
                #     return QGraphicsScene.mouseReleaseEvent(self, event)

                if not event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    self.finish_interactive_tools(kapat=False)
                return QGraphicsScene.mouseReleaseEvent(self, event)
                # return

            if self.aktifArac == self.OkAraci:
                return QGraphicsScene.mouseReleaseEvent(self, event)

            elif self.aktifArac == self.KutuAraci or self.aktifArac == self.YuvarlakAraci:
                self.lastItem.show_resize_handles()
                # if not event.modifiers() == Qt.KeyboardModifier.AltModifier:
                if not self.space_tusu_su_an_basili:
                    # self.aktifArac = self.SecimAraci
                    # self.parent().setCursor(Qt.ArrowCursor)
                    # self.parent().actionSwitchToSelectionTool.setChecked(True)
                    self.secim_aracina_gec()
                self.lastItem = None
                # return QGraphicsScene.mousePressEvent(self, event)
                return QGraphicsScene.mouseReleaseEvent(self, event)

            # if self.tasinanNesne:  # and event.button() == Qt.LeftButton:
            #     if not self.eskiPosTasinanNesne == self.tasinanNesne.pos():
            #         self.nesneTasindi.emit(self.tasinanNesne, self.eskiPosTasinanNesne)
            #     self.tasinanNesne = None

            # this one also handles, sceneRect adaptation for repositioned items.
            if self.tasinanNesne:  # and event.button() == Qt.LeftButton:
                if not self.eskiPosTasinanNesne == self.tasinanNesne.pos():
                    tasinanNesnelerinBoundingRect = QRectF()  # sceneRect adaptation
                    self.undoStack.beginMacro("move {} item(s)".format(len(self.tasinanNesnelerinListesi)))
                    for nesneVeEskiPos in self.tasinanNesnelerinListesi:
                        self.nesneTasindi.emit(nesneVeEskiPos[0], nesneVeEskiPos[1])
                        # v - sceneRect adaptation - v
                        tasinanNesnelerinBoundingRect = tasinanNesnelerinBoundingRect.united(
                            nesneVeEskiPos[0].sceneBoundingRect())
                    self.undoStack.endMacro()
                    self.unite_with_scene_rect(tasinanNesnelerinBoundingRect)
                self.tasinanNesne = None

        super(Scene, self).mouseReleaseEvent(event)
        # print(self.selectionQueue)

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Space:
            self.space_tusu_su_an_basili = True

        if event.key() == Qt.Key.Key_Delete \
                or event.key() == Qt.Key_Backspace:
            if self.aktifArac == self.KalemAraci:
                if self.pathItem:
                    if self.pathItem.path().elementCount() > 1:
                        self.pathItem.sonNoktaSil()
                    # else:
                    #     self.finish_interactive_tools()

        if event.key() == Qt.Key.Key_Escape:
            self.finish_interactive_tools(kapat=False)

        if event.key() == Qt.Key.Key_Enter \
                or event.key() == Qt.Key.Key_Return:

            if self.aktifArac == self.AynalaXAraci:
                self.parent().act_mirror_x(
                    self.parent().get_mouse_scene_pos())  # bu finish_interactive_toolsu da cagiriyor.

            elif self.aktifArac == self.AynalaYAraci:
                self.parent().act_mirror_y(
                    self.parent().get_mouse_scene_pos())  # bu finish_interactive_toolsu da cagiriyor.

        if event.key() == Qt.Key.Key_Enter \
                or event.key() == Qt.Key.Key_Return:
            self.finish_interactive_tools(kapat=True)

        # if event.key() == Qt.Key.Key_Up:
        #     pass
        # if event.key() == Qt.Key.Key_Down:
        #     pass
        # if event.key() == Qt.Key.Key_Right:
        #     self.focusNextPrevChild(True)
        # if event.key() == Qt.Key.Key_Left:
        #     self.focusNextPrevChild(False)

        # if event.key() == Qt.Key.Key_Space:
        #     print(self.selectionQueue)

        ########################################################################

        # # TODO: movelara undo , ayrica sahnede diger nesneye gecmek muhtemelen modifersiz olsun.
        # # dolayisiyla tek birim hareket de alt tusuna falan mi atasak.

        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            if event.key() == Qt.Key.Key_Up:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(0, -10)
            if event.key() == Qt.Key.Key_Down:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(0, 10)
            if event.key() == Qt.Key.Key_Right:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(10, 0)
            if event.key() == Qt.Key.Key_Left:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(-10, 0)

            if event.key() == Qt.Key.Key_Shift:

                if self.aktifArac == self.KalemAraci:
                    if not self.fircaBoyutuItem:
                        self._fircaBoyutuItem_olustur()

        # elif event.modifiers() & Qt.ControlModifier:
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # ctrl ok ve ctrl + shift oklar kisa yol olarak ana pencerede atanmis durumda
            # burda tum ctrl hareketlerini iptal ediyoruz
            return QGraphicsScene.keyPressEvent(self, event)

        else:
            if event.key() == Qt.Key.Key_Up:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(0, -1)
            if event.key() == Qt.Key.Key_Down:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(0, 1)
            if event.key() == Qt.Key.Key_Right:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(1, 0)
            if event.key() == Qt.Key.Key_Left:
                self.yazi_yazilmiyorsa_nesneyi_kaydir(-1, 0)

            # event.accept()

        super(Scene, self).keyPressEvent(event)

    # ---------------------------------------------------------------------
    def keyReleaseEvent(self, event):

        if event.key() == Qt.Key.Key_Space:
            self.space_tusu_su_an_basili = False

        # if event.key() == Qt.Key_Alt:
        #     if self.aktifArac == self.KutuAraci or self.aktifArac == self.YuvarlakAraci:
        #         self.aktifArac = self.SecimAraci
        #         self.parent().setCursor(Qt.ArrowCursor)

        if self.aktifArac == self.KalemAraci:
            if event.key() == Qt.Key.Key_Shift:
                if self.fircaBoyutuItem:
                    self.removeItem(self.fircaBoyutuItem)
                    self.fircaBoyutuItem = None

        super(Scene, self).keyReleaseEvent(event)

    # ---------------------------------------------------------------------
    def dragEnterEvent(self, event):
        # self.parent().tabWidget.currentWidget().setFocus()
        # !! burda bir onceki eventin modifierini dikkate aliyor.
        # if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
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
        # if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
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

        if type(event.source()) == YuzenWidget:
            event.source().parent().parent().yw_yuzdur(event.source())

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
                    # surukle birakla pdf doya olarak eklensin, resim olarak degil.
                    # pdf ayni zamanda supportedImageFormatList icinde de var,
                    # o listeden pdf silmiyoruz cunku resim ekle menusunden pdfi resim olarak secebilsin.
                    if extension == "pdf":
                        otherFilePaths.append(filePath)
                        continue
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

                        # pixMap = QPixmap(imageSavePath)
                        # print(imageSavePath)
                        # pixMap = QPixmap(image)
                        # rectf = QRectF(pixMap.rect())
                        imageItem = Image(imageSavePath, event.scenePos(), None, None, self.ResimAraci.yaziRengi,
                                          self.ResimAraci.arkaPlanRengi,
                                          QPen(self.ResimAraci.kalem), QFont(self.ResimAraci.yaziTipi))

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
                textItem = Text(event.scenePos(), self.YaziAraci.yaziRengi, self.YaziAraci.arkaPlanRengi,
                                QPen(self.YaziAraci.kalem),
                                QFont(self.YaziAraci.yaziTipi))
                textItem.set_document_url(self.tempDirPath)
                self.parent().increase_zvalue(textItem)

                textItem.setPlainText(webUrl[0].toString())
                textItem.textItemFocusedOut.connect(lambda: self.is_text_item_empty(textItem))
                self.parent().increase_zvalue(textItem)
                undoRedo.undoableAddItem(self.undoStack, self.tr("drag && drop url as text"), self, textItem)
                textItem.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
                cursor = textItem.textCursor()
                cursor.clearSelection()
                textItem.setTextCursor(cursor)
                self.unite_with_scene_rect(textItem.sceneBoundingRect())

        elif event.mimeData().hasHtml():
            textItem = Text(event.scenePos(), self.YaziAraci.yaziRengi, self.YaziAraci.arkaPlanRengi,
                            QPen(self.YaziAraci.kalem),
                            QFont(self.YaziAraci.yaziTipi))
            textItem.set_document_url(self.tempDirPath)
            self.parent().increase_zvalue(textItem)
            # bu ikisi bir onceki eventtek kalan modifieri donduruyor. o yuzden query kullaniyoruz.
            # if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            # if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            if QApplication.queryKeyboardModifiers() == Qt.KeyboardModifier.ShiftModifier:
                textItem.setPlainText(event.mimeData().text())
                textItem.textItemFocusedOut.connect(lambda: self.is_text_item_empty(textItem))
                self.parent().increase_zvalue(textItem)
                undoRedo.undoableAddItem(self.undoStack, self.tr("drag && drop text"), self, textItem)
                textItem.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
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
                textItem.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
                cursor = textItem.textCursor()
                cursor.clearSelection()
                textItem.setTextCursor(cursor)

            self.unite_with_scene_rect(textItem.sceneBoundingRect())

        elif event.mimeData().hasText():
            textItem = Text(event.scenePos(), self.YaziAraci.yaziRengi, self.YaziAraci.arkaPlanRengi,
                            QPen(self.YaziAraci.kalem),
                            QFont(self.YaziAraci.yaziTipi))
            textItem.set_document_url(self.tempDirPath)
            # textItem.update_resize_handles()
            self.parent().increase_zvalue(textItem)
            textItem.setPlainText(event.mimeData().text())
            textItem.textItemFocusedOut.connect(lambda: self.is_text_item_empty(textItem))
            self.parent().increase_zvalue(textItem)
            undoRedo.undoableAddItem(self.undoStack, self.tr("drag && drop text"), self, textItem)
            textItem.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
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

            # pixMap = QPixmap(imageSavePath)
            # print(imageSavePath)
            pixMap = QPixmap(image)
            rectf = QRectF(pixMap.rect())
            imageItem = Image(imageSavePath, event.scenePos(), rectf, pixMap, self.ResimAraci.yaziRengi,
                              self.ResimAraci.arkaPlanRengi,
                              QPen(self.ResimAraci.kalem), QFont(self.ResimAraci.yaziTipi))

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
            # pixMap = QPixmap(imagePath)
            pixMap = QPixmap(image)
            rectf = QRectF(pixMap.rect())
            imageItem = Image(imagePath, event.scenePos(), rectf, pixMap, self.ResimAraci.yaziRengi,
                              self.ResimAraci.arkaPlanRengi,
                              QPen(self.ResimAraci.kalem), QFont(self.ResimAraci.yaziTipi))

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

        # pixMap = QPixmap(imagePath)
        # pixMap = QPixmap(image)
        # rectf = QRectF(pixMap.rect())

        imageItem = Image(imagePath, scenePos, None, None,
                          self.ResimAraci.yaziRengi,
                          self.ResimAraci.arkaPlanRengi,
                          QPen(self.ResimAraci.kalem),
                          QFont(self.ResimAraci.yaziTipi))
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
