# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '3/28/16'

import uuid
from PySide6.QtCore import (Qt, QRectF, QSizeF, QPointF, Slot)
from PySide6.QtGui import (QPainterPath, QPainterPathStroker, QPen, QBrush, QColor, QTransform, QTextOption)
from PySide6.QtWidgets import (QGraphicsItem, QStyle)
from canta import shared
from canta.nesneler.tempTextItem import TempTextItem


########################################################################
class PathItem(QGraphicsItem):
    Type = shared.PATH_ITEM_TYPE

    def __init__(self, pos, yaziRengi, arkaPlanRengi, pen, font, path=None, parent=None):
        super(PathItem, self).__init__(parent)

        self._kim = uuid.uuid4().hex

        self.setPos(pos)

        if path:
            self._path = path
        else:
            self._path = QPainterPath()
            # self.append(pos)  # buna gerek yok..

        # self.pixmap = QPixmap()
        self.secilen_nokta = None

        self.movedPointsList = []

        # cizim icin False baslamak dogru olabilirdi ama
        # kopyalama ve dosyadan yukleme gibi durumlarda bu false kalıyor
        # o yuzden True baslayip, cizim de ilk noktada(move_start_point) False ediyoruz
        self.isDrawingFinished = True
        self.realCount = 0
        self.lastPath = QPainterPath()

        self.startPointRect = QRectF()
        self.searchBoxSize = QSizeF(15, 15)
        self.intersects = False

        self.cizgi_basitlestirme_miktari = 10  # moveCenterda kullanildigi icin yarisi aslinda

        self.initialFlags = self.flags()
        self.setFlags(self.ItemIsSelectable |
                      self.ItemIsMovable |
                      self.ItemIsFocusable)

        self.secili_nesne_kalem_kalinligi = 0

        self._pen = pen
        self._brush = QBrush()
        self._font = font

        self.activeItemLineColor = shared.activeItemLineColor
        self.cizgiRengi = pen.color()
        self.setCizgiRengi(self.cizgiRengi)  # also sets self._pen
        self.yaziRengi = yaziRengi
        self.setYaziRengi(yaziRengi)
        self.setArkaPlanRengi(arkaPlanRengi)  # also sets self._brush

        # we override bg brush for drawing.
        self.setBrush(Qt.NoBrush)
        # self.setBrush(arkaPlanRengi)

        self.cosmeticSelect = False
        self.isActiveItem = False
        self.isFrozen = False
        self._isPinned = False

        self._text = ""
        self._command = {}

        self.editMode = False

        self.tempTextItem = None
        self.tempEskiText = ""

        self.textPadding = 20

        self.painterTextOption = QTextOption()
        self.painterTextOption.setAlignment(Qt.AlignCenter)
        self.painterTextOption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        self.painterTextScale = 1
        self.painterTextRect = QRectF(self.boundingRect())

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
    def type(self):
        return PathItem.Type

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
        # filtering out pathItem type is an another option but,
        # we may add resize functions to the PathItem object in the future.
        # so ...
        pass

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      # "painterPath": self.path(),
                      "kim": self._kim,
                      "painterPathAsList": self.toList(),
                      "isPathClosed": self.isPathClosed(),
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "scale": self.scale(),
                      "zValue": self.zValue(),
                      "pen": self._pen,
                      "font": self._font,
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "isFrozen": self.isFrozen,
                      "command": self._command,
                      }
        return properties

    # ---------------------------------------------------------------------
    def isPathClosed(self):
        poly = self._path.toSubpathPolygons()
        return poly[0].isClosed()

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):
        # if change == self.ItemPositionChange:
        # if change == self.ItemSelectedChange:
        # if change == self.ItemSelectedHasChanged:
        if change == self.ItemSelectedChange:
            if value:
                self.scene().parent().path_item_selected(self)
            else:
                self.scene().parent().item_deselected(self)

        # return QGraphicsRectItem.itemChange(self, change, value)
        return value
        # super(Rect, self).itemChange(change, value)

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
    def sceneCenter(self):
        return self.mapToScene(self.path().controlPointRect().center())

    # ---------------------------------------------------------------------
    def sceneWidth(self):
        return self.sceneRight() - self.sceneLeft()

    # ---------------------------------------------------------------------
    def sceneHeight(self):
        return self.sceneBottom() - self.sceneTop()

    # ---------------------------------------------------------------------
    def sceneRight(self):

        path = self.mapToScene(self.path())
        liste = self.toList(path)
        right = liste[0]
        for i in range(path.elementCount()):
            right = max(liste, key=lambda e: e[0])

        return right[0]

    # ---------------------------------------------------------------------
    def sceneLeft(self):

        path = self.mapToScene(self.path())
        liste = self.toList(path)
        left = liste[0]
        for i in range(path.elementCount()):
            left = min(liste, key=lambda e: e[0])

        return left[0]

    # ---------------------------------------------------------------------
    def sceneTop(self):
        path = self.mapToScene(self.path())
        liste = self.toList(path)
        top = liste[1]
        for i in range(path.elementCount()):
            top = min(liste, key=lambda e: e[1])

        return top[1]

    # ---------------------------------------------------------------------
    def sceneBottom(self):
        path = self.mapToScene(self.path())
        liste = self.toList(path)
        bottom = liste[1]
        for i in range(path.elementCount()):
            bottom = max(liste, key=lambda e: e[1])

        return bottom[1]

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
    def path(self):
        return self._path

    # ---------------------------------------------------------------------
    def setPath(self, path):
        if self._path == path:
            return
        self.prepareGeometryChange()
        self._path = path
        self._boundingRect = QRectF()
        self.update()

    # ---------------------------------------------------------------------
    def toList(self, path=None):
        if not path:
            path = self.path()
        liste = []
        for i in range(path.elementCount()):
            element = path.elementAt(i)
            liste.append((element.x, element.y))
        return liste

    # ---------------------------------------------------------------------
    def fromList(self, pathElementsList, closePath=False):
        path = QPainterPath()
        path.moveTo(*pathElementsList[0])
        for e in pathElementsList[1:]:
            path.lineTo(*e)
        if closePath:
            path.closeSubpath()
            self.setBrush(self.arkaPlanRengi)
        self.setPath(path)

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
                                       Qt.DashLine,
                                       Qt.RoundCap, Qt.RoundJoin)
        self.selectionPenBottomIfAlsoActiveItem = QPen(_activeItemLineColor,
                                                       self.secili_nesne_kalem_kalinligi,
                                                       Qt.DashLine,
                                                       Qt.RoundCap, Qt.RoundJoin)

        self.update()

    # ---------------------------------------------------------------------
    def setYaziRengi(self, col):

        # drawing text after drawing rect does not apply alpha
        # we need to reconstruct the color with same values.
        self.yaziRengi = col
        # self.textPen = QPen(QColor().fromRgb(col.red(), col.green(), col.blue(), col.alpha()))
        # self.textPen = QPen(col)
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
    def update(self, rect=QRectF()):
        # self.pathi_pixmap_yap()
        super(PathItem, self).update(rect)

    # ---------------------------------------------------------------------
    def setArkaPlanRengi(self, col):
        self.arkaPlanRengi = col
        # burda nesne kapali mi degil mi kontrolu yapiyoruz
        # daha iyi olabilir bu kontrol
        if not self._brush == Qt.NoBrush:
            self.setBrush(QBrush(col))

    # ---------------------------------------------------------------------
    def setText(self, text):
        self._text = text
        # self.update()

    # ---------------------------------------------------------------------
    def text(self):
        return self._text

    # ---------------------------------------------------------------------
    def setCommand(self, title, command):
        self._command["title"] = title
        self._command["command"] = command

    # ---------------------------------------------------------------------
    def command(self):
        return self._command

    # ---------------------------------------------------------------------
    def setFont(self, font):
        self._font = font
        self.update()

    # ---------------------------------------------------------------------
    def font(self):
        return self._font

    # ---------------------------------------------------------------------
    def setFontPointSize(self, fontPointSize):
        self._font.setPointSize(fontPointSize)
        self.update()

    # ---------------------------------------------------------------------
    def fontPointSize(self):
        return self._font.pointSize()

    # ---------------------------------------------------------------------
    def ver_yazi_hizasi(self):
        return self.painterTextOption.alignment()

    # ---------------------------------------------------------------------
    def kur_yazi_hizasi(self, hizalama):
        self.painterTextOption.setAlignment(hizalama | Qt.AlignVCenter)
        # self.painterTextOption.setAlignment(hizalama)
        self.update()

    # ---------------------------------------------------------------------
    def ver_karakter_bicimi(self):
        # return self._font.bold | self._font.italic | self._font.under | self._font.strikeout
        return {"b": self._font.bold(),
                "i": self._font.italic(),
                "u": self._font.underline(),
                "s": self._font.strikeOut(),
                "o": self._font.overline(),
                }

    # ---------------------------------------------------------------------
    def kur_karakter_bicimi(self, sozluk):
        self._font.setBold(sozluk["b"])
        self._font.setItalic(sozluk["i"])
        self._font.setUnderline(sozluk["u"])
        self._font.setStrikeOut(sozluk["s"])
        self._font.setOverline(sozluk["o"])
        self.update()

    # ---------------------------------------------------------------------
    def setPen(self, pen):

        if self._pen == pen:
            return
        self.prepareGeometryChange()
        self._pen = pen
        self._boundingRect = QRectF()
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
    def mirror(self, x, y):
        if not x and not y:
            return
        # mirrorMatrix = QMatrix()
        # PyQt5 de matrix yok, onun yerine qtransform..
        mirrorMatrix = QTransform()
        if x:
            if y:
                mirrorMatrix.scale(-1, -1)
            else:
                mirrorMatrix.scale(-1, 1)
        else:
            if y:
                mirrorMatrix.scale(1, -1)

        mirroredPath = self.path() * mirrorMatrix
        # mirroredPath = mirrorMatrix.map(self.path())
        self.setPath(mirroredPath)

    # ---------------------------------------------------------------------
    def flipHorizontal(self, mposx):
        self.mirror(x=True, y=False)
        ipos = self.scenePos()
        # ipos.setX(ipos.x() + 2 * (mposx - ipos.x()))
        ipos.setX((2 * mposx) - ipos.x())
        if self.parentItem():
            # ipos = (ipos - self.parentItem().scenePos())
            ipos = (self.parentItem().mapFromScene(ipos))

        self.setPos(ipos)
        if self.rotation():
            self.rotateWithOffset(360 - self.rotation())

        eskiRot = self.rotation()
        if eskiRot:
            self.setRotation(0)
        for c in self.childItems():
            c.flipHorizontal(self.sceneCenter().x())
        if eskiRot:
            self.setRotation(eskiRot)

    # ---------------------------------------------------------------------
    def flipVertical(self, mposy):
        self.mirror(x=False, y=True)
        ipos = self.scenePos()
        # ipos.setX(ipos.x() + 2 * (mposx - ipos.x()))
        ipos.setY((2 * mposy) - ipos.y())
        if self.parentItem():
            # ipos = (ipos - self.parentItem().scenePos())
            ipos = (self.parentItem().mapFromScene(ipos))

        self.setPos(ipos)
        if self.rotation():
            self.rotateWithOffset(360 - self.rotation())

        eskiRot = self.rotation()
        if eskiRot:
            self.setRotation(0)
        for c in self.childItems():
            c.flipVertical(self.sceneCenter().y())
        if eskiRot:
            self.setRotation(eskiRot)

    # ---------------------------------------------------------------------
    def move_start_point(self):
        # point = self.mapFromScene(point)
        self.isDrawingFinished = False
        point = QPointF(0, 0)
        path = QPainterPath(self.path())
        if not path.elementCount():
            path.moveTo(point)
            self.realCount = path.elementCount()
            self.startPointRect = QRectF(point, self.searchBoxSize)
            self.startPointRect.moveCenter(point)
            self.setPath(path)
            self.setFlags(self.initialFlags)

    # ---------------------------------------------------------------------
    def append(self, point):
        point = self.mapFromScene(point)
        path = QPainterPath(self.path())
        path.lineTo(point)
        self.lastPath = QPainterPath(path)
        self.setPath(path)
        self.realCount = path.elementCount()

    # ---------------------------------------------------------------------
    def temp_append_and_replace_last(self, point):
        point = self.mapFromScene(point)
        path = QPainterPath(self.path())
        # print(path.elementCount(), self.realCount)
        # if path.elementCount() == 0:
        #     path.lineTo(point)
        #
        # elif path.elementCount() == self.realCount:
        #     path.lineTo(point)
        #
        # elif path.elementCount() < self.realCount:
        #     path.lineTo(point)

        # realcount 0 basliyor zaten <= esiti 0 esitligini sagliyor, ileriye referans olabilir usttekiler kalsin
        if path.elementCount() <= self.realCount:
            path.lineTo(point)

        # bu replace last kismi, else icinde cunku mouse sabitken birden fazla nokta silinirse,
        # cizili kalan son noktayi,  temp nokta  gibi algilayip bir nokta daha eksiltmis oluyordu.
        else:
            path.setElementPositionAt(path.elementCount() - 1, point.x(), point.y())

        self.setPath(path)

    # ---------------------------------------------------------------------
    def sonNoktaSil(self):
        # path = QPainterPath(self.path())
        nokta_listesi = self.toList()
        self.fromList(nokta_listesi[:-1], closePath=False)
        self.realCount = len(nokta_listesi) - 1

    # ---------------------------------------------------------------------
    def check_if_at_start(self, pos):
        pos = self.mapFromScene(pos)
        if self.realCount > 1:
            currentPosRect = QRectF(pos, self.searchBoxSize)
            currentPosRect.moveCenter(pos)

            if currentPosRect.intersects(self.startPointRect):
                self.intersects = True
            else:
                self.intersects = False
        else:
            self.intersects = False

    # ---------------------------------------------------------------------
    def close_path(self, kapat):
        if kapat:
            self.lastPath.closeSubpath()
            self.setBrush(self.arkaPlanRengi)
        self.basitlestir()
        # basitlestir() -> self.setPath yapiyor
        # self.setPath(self.lastPath)
        self.setFlags(self.ItemIsSelectable |
                      self.ItemIsMovable |
                      self.ItemIsFocusable)
        self.intersects = False
        # self.setSelected(True)

        # update pos - bu onemli
        crect = self.path().controlPointRect()
        crect = self.mapRectToScene(crect)
        diff = self.scenePos() - crect.center()
        self.setPos(crect.center())
        self.path().translate(diff)
        self.update_painter_text_rect()
        self.isDrawingFinished = True

        # self.pathi_pixmap_yap()

        # print(self.isPathClosed())
        self.scene().unite_with_scene_rect(self.sceneBoundingRect())

    # # ---------------------------------------------------------------------
    # def basitlestir_1(self):
    #     liste = []
    #     try:
    #         for i in range(self.lastPath.elementCount()):
    #             # a = self.lastPath.elementAt(i).x + self._path.elementAt(i).y
    #             # b = self.lastPath.elementAt(i+1).x + self._path.elementAt(i+1).y
    #             # if abs(a-b) > 2:
    #
    #             # a = abs(self.lastPath.elementAt(i).x - self._path.elementAt(i+1).x)
    #             # b = abs(self.lastPath.elementAt(i).y - self._path.elementAt(i + 1).y)
    #             # if a + b > 2:
    #             #     liste.append([self.lastPath.elementAt(i).x, self.lastPath.elementAt(i).y])
    #
    #             a = abs(self.lastPath.elementAt(i).x - self._path.elementAt(i + 1).x)
    #             if a < 2:
    #                 b = abs(self.lastPath.elementAt(i).y - self._path.elementAt(i + 1).y)
    #                 if b < 2:
    #                     liste.append([self.lastPath.elementAt(i).x, self.lastPath.elementAt(i).y])
    #                 else:
    #                     i += 1
    #
    #     except Exception as e:
    #         pass
    #     print(self.lastPath.elementCount(), len(liste))
    #     self.fromList(liste, self.isPathClosed())

    # ---------------------------------------------------------------------
    def basitlestir(self):
        liste = []
        # ilk noktayi basitlestirilmis cizgiye dahil ediyoruz
        liste.append([self.lastPath.elementAt(1).x, self.lastPath.elementAt(1).y])
        self.arama_kutusu = QRectF(0, 0, self.cizgi_basitlestirme_miktari, self.cizgi_basitlestirme_miktari)
        self.arama_kutusu.moveCenter(QPointF(liste[0][0], liste[0][1]))
        try:
            for i in range(self.lastPath.elementCount()):
                if self.arama_kutusu.contains(self.lastPath.elementAt(i).x,self.lastPath.elementAt(i).y):
                    continue
                else:
                    liste.append([self.lastPath.elementAt(i).x, self.lastPath.elementAt(i).y])
                    self.arama_kutusu.moveCenter(QPointF(liste[-1][0], liste[-1][1]))

            # son noktayi basitlestirilmis cizgiye dahil ediyoruz
            liste.append([self.lastPath.elementAt(self.lastPath.elementCount()-1).x,
                          self.lastPath.elementAt(self.lastPath.elementCount()-1).y])
        #
        except Exception as e:
            print(e)
        # print(self.lastPath.elementCount(), len(liste))
        self.fromList(liste, self.isPathClosed())

    # # ---------------------------------------------------------------------
    # def pathi_pixmap_yap(self):
    #     # self.pixmap.setSize(self.boundingRect().size())
    #     # TODO bunu iptal edebiliriz, performans sagliyor mu acaba pixmape cevirmek
    #     # > 1 idi, gecici iptal ve test icin 10000 yaptik
    #     # TODO:2 saglamiyor gozukuyor. cok daha yavas, belli bir nokta sayisi uzerinde de yavaş
    #     if self._path.elementCount() > 50000:
    #         # TODO burda sizeF te size donusturmede ve de asaigdaki -self.boundingRect().topLeft() kismida
    #         #  kusurat kaybindan ufak kaymalar var
    #         pix = QPixmap(self.boundingRect().size().toSize())
    #         pix.fill(Qt.transparent)
    #         painter = QPainter(pix)
    #         # painter.setRenderHint(QPainter.Antialiasing)
    #         painter.setPen(self._pen)
    #         painter.setBrush(self._brush)
    #         # if not painter.begin(self.pixmap):
    #         #     print("hata")
    #         painter.setRenderHint(QPainter.Antialiasing)
    #         # painter.scale(.3, .3)
    #         painter.translate(-self.boundingRect().topLeft())
    #         painter.drawPath(self.path())
    #         self.pixmap = pix
    #         painter.end()
    #         painter = None
    #         del painter

    # ---------------------------------------------------------------------
    def qt_graphicsItem_shapeFromPath(self, path, pen):

        # We unfortunately need this hack as QPainterPathStroker will set a width of 1.0
        # if we pass a value of 0.0 to QPainterPathStroker.setWidth()
        penWidthZero = 0.00000001
        if path == QPainterPath():
            return path
        ps = QPainterPathStroker()
        ps.setCapStyle(pen.capStyle())

        if pen.widthF() <= 0:
            ps.setWidth(penWidthZero)
        else:
            ps.setWidth(pen.widthF())
        ps.setJoinStyle(pen.joinStyle())
        ps.setMiterLimit(pen.miterLimit())
        # to include connection indicator circle
        # path.addRect(self.startPointRect)
        path.addEllipse(self.startPointRect)
        p = ps.createStroke(path)  # returns QPainterPath
        p.addPath(path)
        return p

    # ---------------------------------------------------------------------
    def boundingRect(self):
        return self.shape().controlPointRect()
        # return self.path().controlPointRect()

        # if self._boundingRect.isNull():
        #     if self.pen().widthF() == 0.0:
        #         self._boundingRect = self._path.controlPointRect()
        #     else:
        #         self._boundingRect = self.shape().controlPointRect()
        #
        # return self._boundingRect

    # ---------------------------------------------------------------------
    def shape(self):
        return self.qt_graphicsItem_shapeFromPath(QPainterPath(self.path()), self.pen())
        # return self.qt_graphicsItem_shapeFromPath(self._path, self.pen())

    # # ---------------------------------------------------------------------
    # def update_painter_text_scale(self):
    #     if self.parentItem():
    #         a = self.parentItem().scale()
    #     else:
    #         a = 1
    #     self.painterTextScale = 1 / self.scale() / a
    #
    # # ---------------------------------------------------------------------
    # def update_painter_text_rect(self):
    #     r = QRectF(self._rect)
    #     size = self._rect.size()
    #     size.setWidth(self.sceneWidth() - self.textPadding)
    #     # r.setSize(self._rect.size() / scale)
    #     r.setSize(size / self.painterTextScale)
    #     r.moveCenter(self._rect.center())
    #     self.painterTextRect = r

    # ---------------------------------------------------------------------
    def update_painter_text_scale(self):
        if self.parentItem():
            a = self.parentItem().scale()
        else:
            a = 1
        self.painterTextScale = 1 / self.scale() / a

    # ---------------------------------------------------------------------
    def update_painter_text_rect(self):
        r = QRectF(self.boundingRect())
        size = self.boundingRect().size()
        size.setWidth(self.sceneWidth() - self.textPadding)
        # r.setSize(self._rect.size() / scale)
        r.setSize(size / self.painterTextScale)
        r.moveCenter(self.boundingRect().center())
        self.painterTextRect = r

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawPath(self._path)

        # if self.pixmap.isNull():
        #     painter.setPen(self._pen)
        #     painter.setBrush(self._brush)
        #     painter.drawPath(self._path)
        # else:
        #     painter.drawPixmap(self.boundingRect().toRect(), self.pixmap)

        if self._text:
            # painter.setWorldMatrixEnabled(False)
            painter.save()
            painter.setFont(self._font)
            # painter.setPen(self.textPen)
            painter.setPen(self.yaziRengi)
            painter.translate(self.boundingRect().center())
            painter.rotate(-self.rotation())
            painter.scale(self.painterTextScale, self.painterTextScale)
            painter.translate(-self.boundingRect().center())
            # metrics = painter.fontMetrics()
            # text = metrics.elidedText(self.text(), Qt.ElideRight, self.boundingRect().width())
            # TODO: self.boundingRect().width() calismadi, sceneWidth() de biraz maliyetli, optimize edilebilir.
            # txt = metrics.elidedText(self._text, Qt.ElideRight, self.sceneWidth() / scale)
            # painter.drawText(self.boundingRect(), Qt.AlignCenter | Qt.AlignVCenter, txt)
            painter.drawText(self.painterTextRect, self._text, self.painterTextOption)
            painter.restore()
            # painter.setWorldMatrixEnabled(True)

        if self.intersects:
            pen = QPen(self._pen)
            pen.setColor(self.arkaPlanRengi)
            painter.setPen(pen)
            painter.setBrush(self.arkaPlanRengi)
            # self.startPointRect.setSize(self.startPointRect.size() * self._pen.width())
            painter.drawEllipse(self.startPointRect)

        if option.state & QStyle.State_Selected or self.cosmeticSelect:

            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
            else:
                selectionPenBottom = self.selectionPenBottom

            painter.setBrush(Qt.NoBrush)

            # if self.pixmap.isNull():
            if self.editMode:
                painter.setPen(selectionPenBottom)
                painter.drawPath(self._path)

                # painter.setPen(self.selectionPenTop)
                # painter.drawPath(self._path)

                path = self.path()
                painter.setPen(QPen(self.cizgiRengi, 5))
                for i in range(path.elementCount()):
                    painter.drawPoint(QPointF(path.elementAt(i).x, path.elementAt(i).y))
                if self.secilen_nokta:
                    painter.setPen(QPen(Qt.red, 10))
                    painter.drawPoint(
                        QPointF(path.elementAt(self.secilen_nokta_idx).x, path.elementAt(self.secilen_nokta_idx).y))

            else:
                painter.setPen(selectionPenBottom)
                painter.drawRect(self.boundingRect())

                # painter.setPen(self.selectionPenTop)
                # painter.drawRect(self.boundingRect())

            # if self.editMode:
            #     # for a future release, draw points
            #     path = self.path()
            #     painter.setPen(QPen(self.cizgiRengi, 10))
            #     for i in range(path.elementCount()):
            #         painter.drawPoint(QPointF(path.elementAt(i).x, path.elementAt(i).y))

        # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self.boundingRect(), "{},  {}\n{},  {}".format(p.x(),p.y(),s.x(), s.y()))
        # painter.drawRect(self.boundingRect())
        # painter.drawRect(p.x(),p.y(),100,100)
        # painter.drawRect(s.x(),s.y(),100,100)
        # painter.drawRect(0,0,15,15)
        # painter.drawRect(self.path().controlPointRect())
        # painter.drawRect(self.boundingRect())
        # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):
        # factor = 1.41 ** (event.delta() / 240.0)
        # self.scale(factor, factor)

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
                super(PathItem, self).wheelEvent(event)

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            if not self.isFrozen:
                self.rotateItem(event.delta())
            else:
                super(PathItem, self).wheelEvent(event)

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
        #         self.scaleItemByScalingPath(event.delta())
        #     else:
        #         super(PathItem, self).wheelEvent(event)
        else:
            super(PathItem, self).wheelEvent(event)

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
            self.scene().undoStack.beginMacro("change text size")
            self.scene().undoRedo.undoableSetFontSize(self.scene().undoStack, "change text size", self, size)
            for c in self.childItems():
                c.changeFontSize(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetFontSize(self.scene().undoStack, "change text size", self, size)

    # ---------------------------------------------------------------------
    def scaleItemByScalingPath(self, delta):

        # self.setTransformOriginPoint(self.boundingRect().center())

        # TODO : size sıfır olmasin kontrolu

        # scaleFactor = 1.1 * self.scale()
        # center = self.boundingRect().center()
        if delta > 0:
            # scaleFactor = 1.1 * self.scale()
            scaleFactor = 1.1 * self.transform().m11()  # m11:vertical scale factor , m:22 horizontal scale factor
            # self.setTransform(QTransform.fromScale(sx, sy), true)
            # self.setTransform(QTransform.fromScale(scaleFactor, scaleFactor))
            # self.setScale(scaleFactor)
            # self.scene().undoableScale("Scale", self, scaleFactor)

            # scaleMatrix = QMatrix()
            scaleMatrix = QTransform()
            scaleMatrix.scale(scaleFactor, scaleFactor)
            scaledPath = self.path() * scaleMatrix
            # self.setPath(scaledPath)
            self.scene().undoRedo.undoableScalePathItemByScalingPath(self.scene().undoStack, "scale", self,
                                                                     scaledPath)
            self.scene().unite_with_scene_rect(self.sceneBoundingRect())
        else:
            if self.path().controlPointRect().width() < 5:
                return
            # TODO: bounding rect degismiyor, o yuzden asagidaki if kontrolu anlamsiz
            # if not self.boundingRect().width() < 0.1 or not self.boundingRect().height() < 0.1:
            # scaleFactor = 1 / 1.1 * self.scale()
            scaleFactor = 1 / 1.1 * self.transform().m11()  # m11:vertical scale factor , m22: horizontal scale factor
            # self.setTransform(QTransform.fromScale(scaleFactor, scaleFactor))
            # self.setScale(scaleFactor)
            # self.scene().undoableScale("Scale", self, scaleFactor)
            # scaleMatrix = QMatrix()
            scaleMatrix = QTransform()
            scaleMatrix.scale(scaleFactor, scaleFactor)
            scaledPath = self.path() * scaleMatrix
            # self.setPath(scaledPath)
            self.scene().undoRedo.undoableScalePathItemByScalingPath(self.scene().undoStack, "scale", self,
                                                                     scaledPath)

            # bunu undoableScalePathItemByScalingPath icinden cagiriyoruz
            # self.item.update_painter_text_rect()

        # self.setTransformOriginPoint(self.boundingRect().center())

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

        # undoableScale  scaleWithOffset i cagiriyor. orda guncelliyoruz alttakileri.
        # self.update_painter_text_scale()
        # self.update_painter_text_rect()

    # ---------------------------------------------------------------------
    def scaleWithOffset(self, scale):
        cEski = self.sceneCenter()
        self.setScale(scale)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())
        # self.updateBoundingRect()
        self.update_painter_text_scale()
        self.update_painter_text_rect()

    # ---------------------------------------------------------------------
    def rotateWithOffset(self, angle):
        cEski = self.sceneCenter()
        self.setRotation(angle)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())
        self.update_painter_text_rect()

    # ---------------------------------------------------------------------
    def rotateItem(self, delta):

        # self.setTransformOriginPoint(self.boundingRect().center())
        if delta > 0:
            # self.setRotation(self.rotation() + 5)
            self.scene().undoRedo.undoableRotate(self.scene().undoStack, "Rotate", self, self.rotation() + 5)
        else:
            # self.setRotation(self.rotation() - 5)
            self.scene().undoRedo.undoableRotate(self.scene().undoStack, "Rotate", self, self.rotation() - 5)
        self.update_painter_text_rect()
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

        col = shared.calculate_alpha(delta, self._pen.color())

        # self.scene().undoableSetLineOrTextColorAlpha("Change item's line alpha", self, col)
        if self.childItems():
            self.scene().undoStack.beginMacro("change items' line alpha")
            self.scene().undoRedo.undoableSetLineColorAlpha(self.scene().undoStack,
                                                            "_change item's line alpha", self, col)
            for c in self.childItems():
                c.changeLineColorAlpha(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetLineColorAlpha(self.scene().undoStack,
                                                            "change item's line alpha", self, col)

    # ---------------------------------------------------------------------
    def changeTextColorAlpha(self, delta):

        col = shared.calculate_alpha(delta, self.yaziRengi)

        if self.childItems():
            self.scene().undoStack.beginMacro("change items' text alpha")
            self.scene().undoRedo.undoableSetTextColorAlpha(self.scene().undoStack,
                                                            "_change item's text alpha", self, col)
            for c in self.childItems():
                c.changeTextColorAlpha(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetTextColorAlpha(self.scene().undoStack,
                                                            "change item's text alpha", self, col)

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

    # # ---------------------------------------------------------------------
    # def mouseDoubleClickEvent(self, event):
    #     self.editMode = not self.editMode
    #     self.update()
    #     super(PathItem, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):

        if event.modifiers() & Qt.ControlModifier:
            self.editMode = not self.editMode
            self.update()
            # super(PathItem, self).mouseDoubleClickEvent(event)
            return

        # eger cizim yapiyorken , yani daha sahneye resmi olarak eklemedik
        # o zaman cizimibitirmeden cift tiklarsak cokgen nesnesinin yazi yazma kutucugu aciliyor
        # ama sonrasi problem, o yuzden asagidaki yazi yazma ozelligini eger parent yoksa demekki sahneye eklenmemis
        # diye dusunerek aktif etmiyoruz.
        # AYRICA SANHE DOUBLE CLICK inde, normal text nesnesi eklemse ile ilgili durum kontrol ediliyor.
        if self.isDrawingFinished:
            if not self.tempTextItem:
                self.tempTextItem = TempTextItem(self.sceneWidth() - self.textPadding,
                                                 self._font,
                                                 self.yaziRengi,
                                                 parent=self)
                self.tempTextItem.setParentItem(self)

            self.tempTextItem.setPlainText(self.text())
            self.tempEskiText = self.text()
            self.setText("")
            self.tempTextItem.setRotation(360 - self.rotation())
            # self.tempTextItem.scaleWithOffset(1 / self.scale())
            # self.tempTextItem.rotateWithOffset(360 - self.rotation())
            self.tempTextItem.setCenter(self.boundingRect().center())
            self.tempTextItem.setFocus()

            # !! burda lambda kullanmazsak, self.is_temp_text_item_empty ,self daha olsumadigi icin,
            # selfi null olarak goruyor ve baglanti kuramiyor.
            self.tempTextItem.textItemFocusedOut.connect(lambda: self.is_temp_text_item_empty())

        super(PathItem, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    @Slot()
    def is_temp_text_item_empty(self):
        tmpText = self.tempTextItem.toPlainText()
        self.scene().undoRedo.undoableItemSetText(self.scene().undoStack, "change text", self,
                                                  self.tempEskiText, tmpText)
        # if not tmpText:
        self.scene().removeItem(self.tempTextItem)
        self.tempTextItem.deleteLater()
        self.tempTextItem = None

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):

        if self.editMode:
            liste = []
            for i in range(self._path.elementCount()):
                liste.append(
                    abs(self._path.elementAt(i).x - event.pos().x()) + abs(self._path.elementAt(i).y - event.pos().y()))
            en_yakin_nokta_degeri = min(liste)
            if en_yakin_nokta_degeri < 7:
                self.secilen_nokta_idx = liste.index(en_yakin_nokta_degeri)
                self.secilen_nokta = self._path.elementAt(self.secilen_nokta_idx)
                print(self.secilen_nokta.x, self.secilen_nokta.y)
                self.movedPointsList.append((self.secilen_nokta_idx, self.secilen_nokta.x, self.secilen_nokta.y))
                self.update()

        super(PathItem, self).mousePressEvent(event)

        # TODO: bu kozmetik amacli, sadece release de olunca gecikmeli seciyormus hissi oluyor
        if self.isSelected() and self.childItems():
            self.scene().select_all_children_recursively(self, cosmeticSelect=True)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        if self.editMode:
            if self.secilen_nokta:
                path = QPainterPath(self.path())
                path.setElementPositionAt(self.secilen_nokta_idx, event.pos().x(), event.pos().y())
                self._path.swap(path)

                self.update()
                return

        super(PathItem, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):

        super(PathItem, self).mouseReleaseEvent(event)

        if self.secilen_nokta:

            self.scene().undoStack.beginMacro("move {} point(s)".format(len(self.movedPointsList)))
            for secilen_nokta_idx, eskiX, eskiY in self.movedPointsList:
                self.scene().undoRedo.undoableMovePathPoint(undoStack=self.scene().undoStack,
                                                            description=self.scene().tr("Path point moved"),
                                                            item=self,
                                                            movedPointIndex=secilen_nokta_idx,
                                                            eskiPosTuple=(eskiX, eskiY),
                                                            yeniPosTuple=(self._path.elementAt(secilen_nokta_idx).x,
                                                                          self._path.elementAt(secilen_nokta_idx).y)
                                                            )
            self.scene().undoStack.endMacro()

            # TODO: bu yukarda for dongusu ve macro yokmus gib su an tek nesne varmis gibi secilen nokta none diyor
            # bir cok nokta secmek ozelligi eklenirse bunu degistirmek lazim

            self.movedPointsList = []
            self.secilen_nokta = None
            # self.update()

        self.scene().unite_with_scene_rect(self.sceneBoundingRect())

        if self.childItems():
            if self.isSelected():
                self.scene().select_all_children_recursively(self, cosmeticSelect=False, topmostParent=True)
            else:
                self.scene().select_all_children_recursively(self, cosmeticSelect=False)
