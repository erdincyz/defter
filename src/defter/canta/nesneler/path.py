# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtCore import Qt, QRectF, QSizeF, QPointF, Slot, QBuffer, QIODevice
from PySide6.QtGui import QPainterPath, QPainterPathStroker, QPen, QBrush, QColor, QTransform, QTextOption, QPainter
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QGraphicsItem, QStyle
from .. import shared
from ..nesneler.tempTextItem import TempTextItem


########################################################################
class PathItem(QGraphicsItem):
    Type = shared.PATH_ITEM_TYPE

    def __init__(self, pos, yaziRengi, arkaPlanRengi, pen, font, path=None, parent=None):
        super(PathItem, self).__init__(parent)

        self._kim = shared.kim(kac_basamak=16)
        self.setAcceptHoverEvents(True)

        self.setPos(pos)

        self._rect = QRectF()

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

        self.isPathClosed = False

        self.cizgi_basitlestirme_miktari = 10  # moveCenterda kullanildigi icin yarisi aslinda

        self.initialFlags = self.flags()
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

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
        self.setBrush(Qt.BrushStyle.NoBrush)
        # self.setBrush(arkaPlanRengi)

        self.cosmeticSelect = False
        self.isActiveItem = False
        self._isPinned = False
        self.ustGrup = None

        self._text = ""
        self._command = {}

        self.editMode = False

        self.tempTextItem = None
        self.tempEskiText = ""

        self.textPadding = 20

        self.painterTextOption = QTextOption()
        self.painterTextOption.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.painterTextOption.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.oklar_dxdy_nokta = {}

        self._resizing = False
        self.handleSize = 10
        self.resizeHandleSize = QSizeF(self.handleSize, self.handleSize)
        self.boundingRectTasmaDegeri = self.handleSize / 2

        self.painterTextRect = QRectF(self.boundingRect())

        self.update_resize_handles()

    # ---------------------------------------------------------------------
    def setRect(self, rect):
        if self._rect == rect:
            return
        # self.prepareGeometryChange()
        self._rect = rect
        self.update_resize_handles()
        # self.update()

    # ---------------------------------------------------------------------
    def rect(self):
        return self._rect

    # ---------------------------------------------------------------------
    def update_resize_handles(self):
        self.prepareGeometryChange()

        if self.scene():
            resizeHandleSize = self.resizeHandleSize / self.scene().views()[0].transform().m11()
        else:
            resizeHandleSize = self.resizeHandleSize

        self.topLeftHandle = QRectF(self._rect.topLeft(), resizeHandleSize)
        self.topRightHandle = QRectF(self._rect.topRight(), resizeHandleSize)
        self.bottomRightHandle = QRectF(self._rect.bottomRight(), resizeHandleSize)
        self.bottomLeftHandle = QRectF(self._rect.bottomLeft(), resizeHandleSize)

        self.topLeftHandle.moveCenter(self._rect.topLeft())
        self.topRightHandle.moveCenter(self._rect.topRight())
        self.bottomRightHandle.moveCenter(self._rect.bottomRight())
        self.bottomLeftHandle.moveCenter(self._rect.bottomLeft())

    # ---------------------------------------------------------------------
    def hide_resize_handles(self):
        self.isPinned = True

    # ---------------------------------------------------------------------
    def show_resize_handles(self):
        self.isPinned = False

    # ---------------------------------------------------------------------
    def type(self):
        return PathItem.Type

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      # "painterPath": self._path,
                      "kim": self._kim,
                      "painterPathAsList": self.toList(),
                      "isPathClosed": self.isPathClosed,
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "zValue": self.zValue(),
                      "pen": self._pen,
                      "font": self._font,
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "yaziHiza": int(self.painterTextOption.alignment()),
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "command": self._command,
                      }
        return properties

    # ---------------------------------------------------------------------
    @property
    def isPinned(self):
        return self._isPinned

    # ---------------------------------------------------------------------
    @isPinned.setter
    def isPinned(self, value):
        if value:
            self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                          # | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                          #  | QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
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

    # # ---------------------------------------------------------------------
    # def isPathClosed(self):
    #     poly = self._path.toSubpathPolygons()
    #     return poly[0].isClosed()

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):
        # if change == self.ItemPositionChange:
        # if change == self.ItemSelectedChange:
        # if change == self.ItemSelectedHasChanged:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
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
        # if not event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        #     self.scene().clearSelection()
        self.setSelected(True)

        # self.scene().parent().item_context_menu(self, event.screenPos())
        self.scene().parent().on_nesne_sag_menu_about_to_show(self)
        self.scene().parent().nesneSagMenu.popup(event.screenPos())

        event.accept()

    # ---------------------------------------------------------------------
    def sceneCenter(self):
        if self.parentItem():
            return self.mapToParent(self._path.controlPointRect().center())
        return self.mapToScene(self._path.controlPointRect().center())

    # ---------------------------------------------------------------------
    def sceneWidth(self):
        return self.sceneRight() - self.sceneLeft()

    # ---------------------------------------------------------------------
    def sceneHeight(self):
        return self.sceneBottom() - self.sceneTop()

    # ---------------------------------------------------------------------
    def sceneRight(self):

        path = self.mapToScene(self._path)
        liste = self.toList(path)
        right = liste[0]
        for _ in range(path.elementCount()):
            right = max(liste, key=lambda e: e[0])

        return right[0]

    # ---------------------------------------------------------------------
    def sceneLeft(self):

        path = self.mapToScene(self._path)
        liste = self.toList(path)
        left = liste[0]
        for _ in range(path.elementCount()):
            left = min(liste, key=lambda e: e[0])

        return left[0]

    # ---------------------------------------------------------------------
    def sceneTop(self):
        path = self.mapToScene(self._path)
        liste = self.toList(path)
        top = liste[1]
        for _ in range(path.elementCount()):
            top = min(liste, key=lambda e: e[1])

        return top[1]

    # ---------------------------------------------------------------------
    def sceneBottom(self):
        path = self.mapToScene(self._path)
        liste = self.toList(path)
        bottom = liste[1]
        for _ in range(path.elementCount()):
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
            path = self._path
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
            self.isPathClosed = True
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
                                       Qt.PenStyle.DashLine,
                                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.selectionPenBottomIfAlsoActiveItem = QPen(_activeItemLineColor,
                                                       self.secili_nesne_kalem_kalinligi,
                                                       Qt.PenStyle.DashLine,
                                                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

        if col.value() > 245:
            self.handleBrush = shared.handleBrushKoyu
        else:
            self.handleBrush = shared.handleBrushAcik
        self.update()

    # ---------------------------------------------------------------------
    def setYaziRengi(self, col):
        self.yaziRengi = col
        self.update()

    # ---------------------------------------------------------------------
    def setCizgiKalinligi(self, width):
        self._pen.setWidthF(width)
        self.boundingRectTasmaDegeri = self.handleSize / 2
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
        if not self._brush == Qt.BrushStyle.NoBrush:
            self.setBrush(QBrush(col))

    # ---------------------------------------------------------------------
    def setText(self, text):
        self._text = text
        # self.update()
        self.update_painter_text_rect()

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
        font.setBold(self._font.bold())
        font.setItalic(self._font.italic())
        font.setUnderline(self._font.underline())
        font.setStrikeOut(self._font.strikeOut())
        font.setOverline(self._font.overline())
        font.setPointSizeF(self._font.pointSizeF())
        self._font = font
        self.update()

    # ---------------------------------------------------------------------
    def font(self):
        return self._font

    # ---------------------------------------------------------------------
    def setFontPointSizeF(self, fontPointSizeF):
        self._font.setPointSizeF(fontPointSizeF)
        self.update()

    # ---------------------------------------------------------------------
    def fontPointSizeF(self):
        return self._font.pointSizeF()

    # ---------------------------------------------------------------------
    def ver_yazi_hizasi(self):
        return self.painterTextOption.alignment()

    # ---------------------------------------------------------------------
    def kur_yazi_hizasi(self, hizalama):
        self.painterTextOption.setAlignment(hizalama | Qt.AlignmentFlag.AlignVCenter)
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

        mirroredPath = self._path * mirrorMatrix
        # mirroredPath = mirrorMatrix.map(self._path)
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
        path = QPainterPath(self._path)
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
        path = QPainterPath(self._path)
        path.lineTo(point)
        self.lastPath = QPainterPath(path)
        self.setPath(path)
        self.realCount = path.elementCount()

    # ---------------------------------------------------------------------
    def temp_append_and_replace_last(self, point):
        point = self.mapFromScene(point)
        path = QPainterPath(self._path)
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
        # path = QPainterPath(self._path)
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
            self.isPathClosed = True
            self.setBrush(self.arkaPlanRengi)
        self.basitlestir()
        # basitlestir() -> self.setPath yapiyor
        # self.setPath(self.lastPath)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.intersects = False
        # self.setSelected(True)

        # update pos - bu onemli
        crect = self._path.controlPointRect()
        crect = self.mapRectToScene(crect)
        # cunku pos noktasi merkezde
        diff = self.scenePos() - crect.center()
        self.setPos(crect.center())
        self._path.translate(diff)
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
        if self.lastPath.elementCount() > 3:
            liste = []
            # ilk noktayi basitlestirilmis cizgiye dahil ediyoruz
            liste.append([self.lastPath.elementAt(1).x, self.lastPath.elementAt(1).y])
            self.arama_kutusu = QRectF(0, 0, self.cizgi_basitlestirme_miktari, self.cizgi_basitlestirme_miktari)
            self.arama_kutusu.moveCenter(QPointF(liste[0][0], liste[0][1]))
            try:
                for i in range(self.lastPath.elementCount()):
                    if self.arama_kutusu.contains(self.lastPath.elementAt(i).x, self.lastPath.elementAt(i).y):
                        continue
                    else:
                        liste.append([self.lastPath.elementAt(i).x, self.lastPath.elementAt(i).y])
                        self.arama_kutusu.moveCenter(QPointF(liste[-1][0], liste[-1][1]))

                # son noktayi basitlestirilmis cizgiye dahil ediyoruz
                liste.append([self.lastPath.elementAt(self.lastPath.elementCount() - 1).x,
                              self.lastPath.elementAt(self.lastPath.elementCount() - 1).y])
            #
            except Exception as e:
                print(e)
            # print(self.lastPath.elementCount(), len(liste))
            self.fromList(liste, self.isPathClosed)

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
    #         painter.drawPath(self._path)
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
        r = self.shape().controlPointRect()
        return r

        # return self._path.controlPointRect()

        # if self._boundingRect.isNull():
        #     if self.pen().widthF() == 0.0:
        #         self._boundingRect = self._path.controlPointRect()
        #     else:
        #         self._boundingRect = self.shape().controlPointRect()
        #
        # return self._boundingRect

    # ---------------------------------------------------------------------
    def shape(self):
        p = self.qt_graphicsItem_shapeFromPath(QPainterPath(self._path), self.pen())
        r = p.controlPointRect()
        if not self._resizing:
            self.setRect(QRectF(r))
        r.adjust(-self.boundingRectTasmaDegeri, -self.boundingRectTasmaDegeri,
                 self.boundingRectTasmaDegeri, self.boundingRectTasmaDegeri)
        p.addRect(r)
        return p

    # ---------------------------------------------------------------------
    def update_painter_text_rect(self):
        r = QRectF(self.boundingRect())
        size = self.boundingRect().size()
        size.setWidth(self.sceneWidth() - self.textPadding)
        r.moveCenter(self.boundingRect().center())
        self.painterTextRect = r

    # ---------------------------------------------------------------------
    def hoverEnterEvent(self, event):
        # event propagationdan dolayi bos da olsa burda implement etmek lazim
        # mousePress,release,move,doubleclick de bu mantıkta...
        # baska yerden baslayip mousepress ile , mousemove baska, mouseReleas baska widgetta gibi
        # icinden cikilmaz durumlara sebep olabiliyor.
        # ayrica override edince accept() de edilmis oluyor mouseeventler
        super(PathItem, self).hoverEnterEvent(event)

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

        super(PathItem, self).hoverMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverLeaveEvent(self, event):
        # if self.isSelected():
        # self.setCursor(self.saved_cursor)
        if not self.ustGrup:
            self.scene().parent().setCursor(self.scene().parent().imlec_arac, gecici_mi=True)

        super(PathItem, self).hoverLeaveEvent(event)

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):
        # factor = 1.41 ** (event.delta() / 240.0)

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
            self.scaleItemByScalingPath(event.delta())

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
        #     self.scaleItemByScalingPath(event.delta())

        if not self.isDrawingFinished:
            self.scene().tekerlek_ile_firca_boyu_degistir(event.delta())

        else:
            super(PathItem, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def changeFontSizeF(self, delta):

        if self.tempTextItem:
            return

        # font = self.font()
        size = self.fontPointSizeF()

        if delta > 0:
            # font.setPointSizeF(size + 1)
            size += 1

        else:
            if size > 10:
                # font.setPointSizeF(size - 1)
                size -= 1
            else:
                # undolari biriktermesin diye donuyoruz,
                # yoksa zaten ayni size de yeni bir undolu size komutu veriyor.
                return

        # self.setFont(font)
        if self.childItems():
            self.scene().undoStack.beginMacro("change text size")
            self.scene().undoRedo.undoableSetFontSizeF(self.scene().undoStack, "change text size", self, size)
            for c in self.childItems():
                c.changeFontSizeF(delta)
            self.scene().undoStack.endMacro()
        else:
            self.scene().undoRedo.undoableSetFontSizeF(self.scene().undoStack, "change text size", self, size)

    # ---------------------------------------------------------------------
    def scaleItemByScalingPath(self, delta):

        if self.tempTextItem:
            return

        scaleFactor = 1.1
        if delta < 0:
            scaleFactor = 1 / scaleFactor

        scaleMatrix = QTransform()
        scaleMatrix.scale(scaleFactor, scaleFactor)
        scaledPath = self._path * scaleMatrix
        # self.setPath(scaledPath)
        self.scene().undoRedo.undoableScalePathItemByScalingPath(self.scene().undoStack, "scale", self,
                                                                 scaledPath, scaleFactor)

        # self.scene().unite_with_scene_rect(self.sceneBoundingRect())

        # self.setTransformOriginPoint(self.boundingRect().center())

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
        if not self.isDrawingFinished:
            return

        # self.setTransformOriginPoint(self.boundingRect().center())
        if delta > 0:
            # self.setRotation(self.rotation() + 5)
            self.scene().undoRedo.undoableRotate(self.scene().undoStack, "Rotate", self, self.rotation() + 5)
        else:
            # self.setRotation(self.rotation() - 5)
            self.scene().undoRedo.undoableRotate(self.scene().undoStack, "Rotate", self, self.rotation() - 5)
        # self.update_painter_text_rect()
        # self.update()

    # ---------------------------------------------------------------------
    def changeBackgroundColorAlpha(self, delta):

        if self.tempTextItem:
            return

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

        if self.tempTextItem:
            return

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

        if self.tempTextItem:
            return

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

    # # ---------------------------------------------------------------------
    # def mouseDoubleClickEvent(self, event):
    #     self.editMode = not self.editMode
    #     self.update()
    #     super(PathItem, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
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
                # print(self.secilen_nokta.x, self.secilen_nokta.y)
                self.movedPointsList.append((self.secilen_nokta_idx, self.secilen_nokta.x, self.secilen_nokta.y))
                self.update()

        else:
            self._resizing = False  # we could use "self._resizingFrom = 0" instead, but self._resizing is more explicit.
            self._fixedResizePoint = None
            self._resizingFrom = None
            self._eskiRectBeforeResize = None

            self._eskiPosBeforeResize = self.pos()
            self._ilk_tik_event_pos = event.pos()
            # self._eskiPosBeforeResize = self.scenePos()

            if self.topLeftHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self._rect.bottomRight()
                self._resizingFrom = 1
            elif self.topRightHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self._rect.bottomLeft()
                self._resizingFrom = 2
            elif self.bottomRightHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self._rect.topLeft()
                self._resizingFrom = 3
            elif self.bottomLeftHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self._rect.topRight()
                self._resizingFrom = 4
            self._eskiRectBeforeResize = self._rect

        super(PathItem, self).mousePressEvent(event)

        # TODO: bu kozmetik amacli, sadece release de olunca gecikmeli seciyormus hissi oluyor
        if self.isSelected() and self.childItems():
            self.scene().select_all_children_recursively(self, cosmeticSelect=True)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        if self.editMode:
            if self.secilen_nokta:
                path = QPainterPath(self._path)
                path.setElementPositionAt(self.secilen_nokta_idx, event.pos().x(), event.pos().y())
                self._path.swap(path)

                self.update()
                return

        elif self._resizing:

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

            rect = QRectF(topLeft, bottomRight)

            c = self._rect.center()

            # Alt Key - to resize around center.
            # if event.modifiers() & Qt.AltModifier:
            if event.modifiers() == Qt.KeyboardModifier.AltModifier:
                rect.moveCenter(c)

            # ---------------------------------------------------------------------
            #  Ctrl Key - to keep aspect ratio while resizing.
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                tl = self._rect.topLeft()
                tr = self._rect.topRight()
                br = self._rect.bottomRight()
                bl = self._rect.bottomLeft()
                c = self._rect.center()

                yeniSize = rect.size()
                eskiSize = self._rect.size()
                # eskiSize.scale(yeniSize, Qt.KeepAspectRatio)
                eskiSize.scale(yeniSize.height(), yeniSize.height(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
                # eskiSize.scale(yeniSize.height(), yeniSize.height(), Qt.KeepAspectRatio)

                # if not eskiSize.isNull():
                if not eskiSize.isEmpty():
                    self.yedekSize = QSizeF(eskiSize)

                else:
                    eskiSize = QSizeF(self.yedekSize)

                rect.setSize(eskiSize)
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
                if event.modifiers() == Qt.KeyboardModifier.AltModifier:
                    rect.moveCenter(c)

            # ---------------------------------------------------------------------
            # Shift Key - to make square (equals width and height)
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
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
                if event.modifiers() == Qt.KeyboardModifier.AltModifier:
                    rect.moveCenter(c)

            # fark = event.pos() - self._ilk_tik_event_pos

            # self.setRect(rect)
            # self.setPos(newPos)
            # TODO : alt calismiyor move to 0,0 dan dolayi
            self._resize(rect)  # mouse release eventten gonderiyoruz undoya
            # self.setRect(rect)  # mouse release eventten gonderiyoruz undoya
            self.update_resize_handles()
            self.scene().parent().change_transform_box_values(self)
            # self.setPos(x, y)
            # return QGraphicsItem.mouseMoveEvent(self, event)

            return

        super(PathItem, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):

        super(PathItem, self).mouseReleaseEvent(event)

        if self.secilen_nokta:
            if event.modifiers() == Qt.KeyboardModifier.AltModifier:
                self.secilen_noktalari_sil()
            else:
                self.secilen_noktalari_tasi()

            self.movedPointsList = []
            # TODO: bu yukarda for dongusu ve macro yokmus gib su an tek nesne varmis gibi secilen nokta none diyor
            # bir cok nokta secmek ozelligi eklenirse bunu degistirmek lazim
            # self.secilen_nokta = None
            # self.update()

        elif self._resizing:

            devam, scaledPath, yeniPos = self._yeni_path_ve_pos_hesapla(yeniRect=self._rect)
            if devam:
                # self.setPos(yeniPos)
                # self.setPath(scaledPath)
                self.scene().undoRedo.undoableResizePathItem(self.scene().undoStack,
                                                             "resize",
                                                             self,
                                                             scaledPath,
                                                             yeniPos)
            self._resizing = False

            # super(PathItem, self).mouseReleaseEvent(event)

            # self.update_painter_text_rect()

        self.scene().unite_with_scene_rect(self.sceneBoundingRect())

        if self.childItems():
            if self.isSelected():
                self.scene().select_all_children_recursively(self, cosmeticSelect=False, topmostParent=True)
            else:
                self.scene().select_all_children_recursively(self, cosmeticSelect=False)

    # ---------------------------------------------------------------------
    def _yeni_path_ve_pos_hesapla(self, yeniRect, eskiRect=None,
                                  scaleFactorX=None,
                                  scaleFactorY=None,
                                  merkez=False):
        try:
            if not eskiRect:
                eskiRect = self._eskiRectBeforeResize

            if not scaleFactorX:
                scaleFactorX = yeniRect.width() / eskiRect.width()
            if not scaleFactorY:
                scaleFactorY = yeniRect.height() / eskiRect.height()

            yeniPos = self.mapToScene(yeniRect.center())
            if self.parentItem():
                yeniPos = self.mapToParent(yeniRect.center())

            scaleMatrix = QTransform()
            scaleMatrix.scale(scaleFactorX, scaleFactorY)
            scaledPath = self._path * scaleMatrix

            if merkez:
                fark = self.scenePos() - yeniPos
                scaledPath.translate(2 * fark)

            return True, scaledPath, yeniPos

        except ZeroDivisionError:
            # scaleFactorX = scaleFactorY = 1
            return False, None, None

    # ---------------------------------------------------------------------
    def _resize(self, yeniRect):
        self.setRect(yeniRect)
        # if self._rect == yeniRect:
        return

        # devam, scaledPath, yeniPos = self._yeni_path_ve_pos_hesapla(yeniRect=self._rect)
        # if devam:
        #     self.setPos(yeniPos)
        #     self.setPath(scaledPath)

    # ---------------------------------------------------------------------
    def secilen_noktalari_tasi(self):
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

    # ---------------------------------------------------------------------
    def secilen_noktalari_sil(self):
        """Deneysel, ilk versiyon"""
        # TODO: bas ve son noktalar, ve de bunlara bagli degisebilecek isPathClosed durumu
        # print("noktalar", secilenNoktalar)

        # 2 for , slice ile, iflerden kurtulunulabilir
        secilenNoktalar = [idx[0] for idx in self.movedPointsList]
        yeniPath = QPainterPath()
        e0 = self._path.elementAt(0)
        yeniPath.moveTo(e0.x, e0.y)
        for i in range(self._path.elementCount()):
            if i not in secilenNoktalar:
                e = self._path.elementAt(i)
                yeniPath.lineTo(e.x, e.y)
        if self.isPathClosed:
            yeniPath.closeSubpath()
            self.setBrush(self.arkaPlanRengi)

        self.scene().undoRedo.undoableDeletePathPoint(undoStack=self.scene().undoStack,
                                                      description=self.scene().tr("Path point deleted"),
                                                      item=self,
                                                      eskiPath=self._path,
                                                      yeniPath=yeniPath)

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

            painter.setBrush(Qt.BrushStyle.NoBrush)

            # if self.pixmap.isNull():
            if self.editMode:
                painter.setPen(selectionPenBottom)
                painter.drawPath(self._path)

                # painter.setPen(self.selectionPenTop)
                # painter.drawPath(self._path)

                path = self._path
                # painter.setPen(QPen(self.cizgiRengi, 5))
                painter.setPen(QPen(Qt.GlobalColor.white, 5))
                for i in range(path.elementCount()):
                    painter.drawPoint(QPointF(path.elementAt(i).x, path.elementAt(i).y))
                if self.secilen_nokta:
                    painter.setPen(QPen(Qt.GlobalColor.red, 10))
                    painter.drawPoint(
                        QPointF(path.elementAt(self.secilen_nokta_idx).x, path.elementAt(self.secilen_nokta_idx).y))

            else:
                painter.setPen(selectionPenBottom)
                painter.drawRect(self._rect)

        # if option.state & QStyle.StateFlag.State_MouseOver:
        #     painter.setBrush(Qt.BrushStyle.NoBrush)
        #     painter.setPen(self.selectionPenBottom)
        #     painter.drawPath(self._path)

        # painter.setPen(self.selectionPenTop)
        # painter.drawRect(self.boundingRect())

        # if self.editMode:
        #     # for a future release, draw points
        #     path = self._path
        #     painter.setPen(QPen(self.cizgiRengi, 10))
        #     for i in range(path.elementCount()):
        #         painter.drawPoint(QPointF(path.elementAt(i).x, path.elementAt(i).y))

        # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self.boundingRect(), "{},  {}\n{},  {}".format(p.x(), p.y(), s.x(), s.y()))
        # # painter.setPen(QPen(Qt.green, 12))
        # painter.setPen(QPen(Qt.red, 16))
        # painter.drawPoint(self.mapFromScene(p))
        # painter.setPen(QPen(Qt.blue, 12))
        # painter.drawPoint(self.mapFromScene(s))
        # painter.drawPoint(self.mapFromScene(self.sceneBoundingRect().center()))
        # painter.drawRect(self.boundingRect())
        # painter.drawRect(p.x(),p.y(),100,100)
        # painter.drawRect(s.x(),s.y(),100,100)
        # painter.drawRect(0,0,15,15)
        # painter.drawRect(self._path.controlPointRect())
        # painter.drawRect(self.boundingRect())
        # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):

        rect = self.sceneBoundingRect()
        w = rect.width()
        h = rect.height()

        x = rect.left()
        y = rect.top()

        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = x - xs
        y = y - ys

        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)

        generator = QSvgGenerator()
        # generator.setFileName("dosya.svg")
        generator.setOutputDevice(buffer)
        # generator.setResolution(72)

        # generator.setSize(QSize(w, h))  # kaymalara sebep oluyor
        generator.setViewBox(QRectF(-w / 2, -h / 2, w, h))
        generator.setTitle(self._kim)
        generator.setDescription("")
        # painter = QPainter(generator)
        painter = QPainter()
        painter.begin(generator)
        painter.setPen(self._pen)
        painter.setBrush(self._brush)

        painter.rotate(self.rotation())
        painter.drawPath(self._path)
        painter.rotate(-self.rotation())

        if self._text:
            # painter.setWorldMatrixEnabled(False)
            painter.save()
            painter.setFont(self._font)
            # painter.setPen(self.textPen)
            painter.setPen(self.yaziRengi)
            painter.translate(self.boundingRect().center())
            painter.rotate(-self.rotation())
            painter.translate(-self.boundingRect().center())
            painter.drawText(self.painterTextRect, self._text, self.painterTextOption)
            painter.restore()
            # painter.setWorldMatrixEnabled(True)

        painter.end()

        svg_string = buffer.data().data().decode("utf-8")

        # background: rgba{self.arkaPlanRengi.toTuple()};\n
        div_str = f"""
                    <div style="
                     position:absolute;
                     z-index:{int(self.zValue() * 10) if self.zValue() else 0};
                     width:{w}px;
                     height:{h}px;
                     top:{y}px;
                     left:{x}px;" id="{self._kim}">{svg_string}</div>\n

            """

        # return svg_string
        return div_str
