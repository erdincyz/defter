# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '3/28/16'

import uuid
from PySide6.QtGui import (QPen, QBrush, QPainterPath, QPainterPathStroker, QColor, QTextOption)
from PySide6.QtWidgets import (QGraphicsItem, QStyle)
from PySide6.QtCore import (QRectF, Qt, QSizeF, QPointF, Slot)
from canta.nesneler.tempTextItem import TempTextItem
from canta import shared


########################################################################
class BaseItem(QGraphicsItem):
    Type = shared.BASE_ITEM_TYPE

    def __init__(self, pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent=None):
        super(BaseItem, self).__init__(parent)
        # QGraphicsItem.__init__(self, parent,scene)

        self._kim = uuid.uuid4().hex

        self.setPos(pos)
        self._rect = rect
        self._boundingRect = QRectF()

        self.setAcceptHoverEvents(True)

        self._eskiRectBeforeResize = None
        self._eskiPosBeforeResize = None

        self.secili_nesne_kalem_kalinligi = 0

        self.handleSize = 10
        self.resizeHandleSize = QSizeF(self.handleSize, self.handleSize)
        self.create_resize_handles()

        self.setFlags(self.ItemIsSelectable |
                      self.ItemIsMovable |
                      self.ItemIsFocusable)

        # self.setFiltersChildEvents(True)
        # self.setHandlesChildEvents(True)

        self._pen = pen
        self._brush = QBrush()
        self._font = font

        self.painterTextOption = QTextOption()
        self.painterTextOption.setAlignment(Qt.AlignCenter)
        self.painterTextOption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        self.painterTextScale = 1
        self.painterTextRect = QRectF(self._rect)

        self.activeItemLineColor = shared.activeItemLineColor
        self.cizgiRengi = pen.color()
        self.setCizgiRengi(self.cizgiRengi)  # also sets self._pen
        self.yaziRengi = yaziRengi
        self.setYaziRengi(yaziRengi)
        self.setArkaPlanRengi(arkaPlanRengi)  # also sets self._brush

        self.cosmeticSelect = False
        self.isActiveItem = False
        self.isFrozen = False
        self._isPinned = False

        self._text = ""
        self._command = {}

        self.tempTextItem = None
        self.tempEskiText = ""

        self.textPadding = 20

        # bagli_oklarin_dxdysi_ve_okun_hangi_noktasi_bagli_sozluk
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

        # self.setText(" ".join(a._kim for a in self.oklar_dxdy_nokta.keys()))

    # ---------------------------------------------------------------------
    def ok_sil(self, ok):
        del self.oklar_dxdy_nokta[ok]
        del ok.baglanmis_nesneler[self._kim]
        # self.setText(" ".join(a._kim for a in self.oklar_dxdy_nokta.keys()))

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
        # Enable the use of qgraphicsitem_cast with this item.
        return BaseItem.Type

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
    def sceneCenter(self):
        return self.mapToScene(self.rect().center())

    # ---------------------------------------------------------------------
    def sceneWidth(self):
        return self.sceneRight() - self.sceneLeft()

    # ---------------------------------------------------------------------
    def sceneHeight(self):
        return self.sceneBottom() - self.sceneTop()

    # # ---------------------------------------------------------------------
    # def sceneRight(self):
    #     return max(self.mapToScene(self.rect().topRight()).x(),
    #                self.mapToScene(self.rect().bottomRight()).x())
    #
    # # ---------------------------------------------------------------------
    # def sceneLeft(self):
    #     return min(self.mapToScene(self.rect().topLeft()).x(),
    #                self.mapToScene(self.rect().bottomLeft()).x())

    # # ---------------------------------------------------------------------
    # def sceneTop(self):
    #     return min(self.mapToScene(self.rect().topLeft()).y(),
    #                self.mapToScene(self.rect().topRight()).y())
    #
    # # ---------------------------------------------------------------------
    # def sceneBottom(self):
    #     return max(self.mapToScene(self.rect().bottomRight()).y(),
    #                self.mapToScene(self.rect().bottomLeft()).y())

    # ---------------------------------------------------------------------
    def sceneRight(self):
        return max(self.mapToScene(self.rect().topLeft()).x(),
                   self.mapToScene(self.rect().topRight()).x(),
                   self.mapToScene(self.rect().bottomRight()).x(),
                   self.mapToScene(self.rect().bottomLeft()).x())

    # ---------------------------------------------------------------------
    def sceneLeft(self):
        return min(self.mapToScene(self.rect().topLeft()).x(),
                   self.mapToScene(self.rect().topRight()).x(),
                   self.mapToScene(self.rect().bottomRight()).x(),
                   self.mapToScene(self.rect().bottomLeft()).x())

    # ---------------------------------------------------------------------
    def sceneTop(self):
        return min(self.mapToScene(self.rect().topLeft()).y(),
                   self.mapToScene(self.rect().topRight()).y(),
                   self.mapToScene(self.rect().bottomRight()).y(),
                   self.mapToScene(self.rect().bottomLeft()).y())

    # ---------------------------------------------------------------------
    def sceneBottom(self):
        return max(self.mapToScene(self.rect().topLeft()).y(),
                   self.mapToScene(self.rect().topRight()).y(),
                   self.mapToScene(self.rect().bottomRight()).y(),
                   self.mapToScene(self.rect().bottomLeft()).y())

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

    # # ---------------------------------------------------------------------
    # def setVerticalCenterWhenParented(self, vcenter):
    #     self.setX(vcenter + self.scenePos().x() - self.sceneCenter().x() - self.parentItem().pos().x())

    # ---------------------------------------------------------------------
    def flipHorizontal(self, mposx):
        rc = self.mapToScene(self.rect().center())
        diff = mposx - rc.x()
        ipos = self.scenePos()
        ipos.setX(ipos.x() + 2 * diff)

        if self.parentItem():
            # eger self parented ise, parented degilmis gibi dusunup
            # sahne pozisyonlari ile mposxe gore yeni mirror pos unu bulup
            # buldugumuzdan sahne pos unu cıkarıp set ediyoruz.
            # bu methodu grup cagirdiginda, donusunde grup icinde bounding rect
            # tekrar hesaplandigi icin, Hamd Olsun islem tamam oluyor.
            # (ayrica grup rotation sifir degilse gecici olarak sifir yapiliyor.
            # burdaki islemler sifir rotationda oluyor. sonra bitince 360- origRot
            # ile grup flipped rotationa donduruluyor)
            # dolayısı ile burda grubun pos u ile ilgili baska bir isleme gerek kalmiyor.
            # ya da grup icersinde. yani grubu icerige giydiriyoruz. islem bitince.

            # self.setScale(self.parentItem().scale())
            # ipos = (ipos - self.parentItem().scenePos())
            # pass
            ipos = (self.parentItem().mapFromScene(ipos))
            # ipos = self.parentItem().transform().map(ipos)

        self.setPos(ipos)
        if self.rotation():
            self.rotateWithOffset(360 - self.rotation())

        eskiRot = self.rotation()
        if eskiRot:
            self.rotateWithOffset(0)
        # eger item parent ise, icindekileri de flip etmek icin,
        # oncesinde yine item rotationu sifirladik, icindekileri flip edince, yine eski rotationa donduruyoruz.
        # bu bi anlamda recursive bir method, neden yukardaki if self.parentItem() i kullanmadik
        # az sonra cagirdigimizda yine bu fonksiyonu, yani child itemin rotation hesaplamalari icin,
        # cunku burda yapmak daha basit ve daha hizli, bu halde iken hesaplamalari c++ yapiyor, eger az once
        # bahsedilen yerde yapilirsa her item icin python yapacak.
        for c in self.childItems():
            c.flipHorizontal(self.sceneCenter().x())
        if eskiRot:
            self.rotateWithOffset(eskiRot)

    # ---------------------------------------------------------------------
    def flipVertical(self, mposy):
        rc = self.mapToScene(self.rect().center())
        diff = mposy - rc.y()
        ipos = self.scenePos()
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
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "pen": self._pen,
                      "font": self._font,
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "isFrozen": self.isFrozen,
                      "command": self._command,
                      }
        # print(properties["scale"])
        return properties

    # ---------------------------------------------------------------------
    def create_resize_handles(self):
        self.topLeftHandle = QRectF(self.rect().topLeft(), self.resizeHandleSize)
        self.topRightHandle = QRectF(self.rect().topRight(), self.resizeHandleSize)
        self.bottomRightHandle = QRectF(self.rect().bottomRight(), self.resizeHandleSize)
        self.bottomLeftHandle = QRectF(self.rect().bottomLeft(), self.resizeHandleSize)

        # initial move
        self.topRightHandle.moveTopRight(self.rect().topRight())
        self.bottomRightHandle.moveBottomRight(self.rect().bottomRight())
        self.bottomLeftHandle.moveBottomLeft(self.rect().bottomLeft())

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

        self.topLeftHandle.moveTopLeft(self.rect().topLeft())
        self.topRightHandle.moveTopRight(self.rect().topRight())
        self.bottomRightHandle.moveBottomRight(self.rect().bottomRight())
        self.bottomLeftHandle.moveBottomLeft(self.rect().bottomLeft())

    # ---------------------------------------------------------------------
    def hide_resize_handles(self):
        self.isPinned = True

    # ---------------------------------------------------------------------
    def show_resize_handles(self):
        self.isPinned = False

    # ---------------------------------------------------------------------
    def setRect(self, rect):
        if self._rect == rect:
            return
        self.prepareGeometryChange()
        self._rect = rect
        self._boundingRect = QRectF()
        self.update()

    # ---------------------------------------------------------------------
    def rect(self):
        return self._rect

    # ---------------------------------------------------------------------
    def setText(self, text):
        self._text = text
        self.update()

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
    def setCizgiRengi(self, col):
        # selectionLineBgColor = QColor(
        #     # 127,
        #                               0 if col.red() > 127 else 255,
        #                               0 if col.green() > 127 else 255,
        #                               0 if col.blue() > 127 else 255
        #                               )
        # selectionLineBgColor = QColor(
        #                               # 20 if max(col.value(),col.saturation()) < 185 else 200,
        #                               20 if col.value() < 215 else 220,
        #                               25 if col.value() < 128 else 220,
        #                               40 if col.value() < 185 else 255
        #                               )

        # selectionLineBgColor.setHsv()
        # selectionLineBgColor = QColor.fromHsl((col.hue() + 180) % 360,
        #                                       col.saturation(),
        #                                       255 - col.lightness())

        # selectionLineFgColor = QColor(
        #     255 if selectionLineBgColor.red() < 128 else 0,
        #     255 if selectionLineBgColor.green() < 128 else 0,
        #     255 if selectionLineBgColor.blue() < 128 else 0
        # )

        _selectionLineBgColor = QColor.fromHsv(col.hue(),
                                              0,
                                              20 if col.value() > 127 else 250)

        _activeItemLineColor = QColor(self.activeItemLineColor)
        if col.hue() > 300 or col.hue() < 30:
            _activeItemLineColor.setHsv((col.hue() + 150) % 360,
                                            self.activeItemLineColor.saturation(),
                                            self.activeItemLineColor.value())


        # selectionLineFgColor = QColor.fromHsv(col.hue(),
        #                                       0,
        #                                       20 if col.value() < 127 else 240)

        self._pen.setColor(col)
        self.cizgiRengi = col

        # drawing text after drawing rect does not apply alpha
        # we need to reconstruct the color with same values.
        # self.textPen = QPen(QColor().fromRgb(col.red(), col.green(), col.blue(), col.alpha()))

        self.selectionPenBottom = QPen(_selectionLineBgColor,
                                       self.secili_nesne_kalem_kalinligi,
                                       Qt.DashLine,
                                       Qt.RoundCap, Qt.RoundJoin)
        self.selectionPenBottomIfAlsoActiveItem = QPen(_activeItemLineColor,
                                                       self.secili_nesne_kalem_kalinligi,
                                                       Qt.DashLine,
                                                       Qt.RoundCap, Qt.RoundJoin)
        # self.selectionPenTop = QPen(col,
        #                             self.secili_nesne_kalem_kalinligi,
        #                             Qt.DashLine,
        #                             Qt.FlatCap, Qt.RoundJoin)

        # cizgi kalinligi zoomla artmasin istersek
        # self._pen.setCosmetic(True)
        # self.selectionPenBottom.setCosmetic(True)
        # self.selectionPenBottomIfAlsoActiveItem.setCosmetic(True)
        # self.selectionPenTop.setCosmetic(True)

        # self.handlePen = QPen(self.cizgiRengi, self.cizgiKalinligi, Qt.DashLine)

        self.update()

    # ---------------------------------------------------------------------
    def setYaziRengi(self, col):

        # drawing text after drawing rect does not apply alpha
        # we need to reconstruct the color with same values.
        self.yaziRengi = col
        # self.textPen = QPen(QColor().fromRgb(col.red(), col.green(), col.blue(), col.alpha()))
        self.textPen = QPen(col)
        self.update()

    # ---------------------------------------------------------------------
    def setCizgiKalinligi(self, width):
        self._pen.setWidthF(width)
        self.textPen.setWidthF(width)
        # self.selectionPenBottom.setWidthF(width)
        # self.selectionPenBottomIfAlsoActiveItem.setWidthF(width)
        # self.selectionPenTop.setWidthF(width)

        self.update()

    # ---------------------------------------------------------------------
    def setArkaPlanRengi(self, col):
        self.arkaPlanRengi = col
        self.setBrush(QBrush(col))

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
    def boundingRectt(self):
        # TODO: burda ince bir durum var ama. neyse .  simdilik asagidaki ile devam.
        if self._boundingRect.isNull():
            halfpw = self.pen().widthF() / 2.0
            self._boundingRect = QRectF(self.rect())
            if halfpw:
                return self._boundingRect.adjusted(-halfpw, -halfpw, halfpw, halfpw)
        return self._boundingRect

    # ---------------------------------------------------------------------
    def boundingRect(self):
        # TODO: kare gruplandiginda bu padding belli oluyor.
        # cunku self.rect ile paint ediyoruz. ellipsete yok bu problem.
        pad = self.pen().widthF() / 2 + self.handleSize
        self._boundingRect = QRectF(self.rect())
        return self._boundingRect.adjusted(-pad, -pad, pad, pad)

        # path = QPainterPath()
        # path.addRect(self.rect())
        # # path.moveTo(0,0)
        # return path.boundingRect()

    # ---------------------------------------------------------------------
    def shape(self):
        path = QPainterPath()
        # path.addRect(self.rect)
        path.addRect(self._rect)
        return self.qt_graphicsItem_shapeFromPath(path, self._pen)

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
        p = ps.createStroke(path)  # return type: QPainterPath
        p.addPath(path)
        return p

    # ---------------------------------------------------------------------
    # TODO: maybe: to: self.paint(): if option.state & QStyle.State_Selected:
    # const QRectF murect = painter->transform().mapRect(QRectF(0, 0, 1, 1));
    # if (qFuzzyIsNull(qMax(murect.width(), murect.height())))
    #     return;
    #
    # const QRectF mbrect = painter->transform().mapRect(item->boundingRect());
    # if (qMin(mbrect.width(), mbrect.height()) < qreal(1.0))
    #     return;

    # ---------------------------------------------------------------------
    def update_painter_text_scale(self):
        if self.parentItem():
            a = self.parentItem().scale()
        else:
            a = 1
        self.painterTextScale = 1 / self.scale() / a

    # ---------------------------------------------------------------------
    def update_painter_text_rect(self):
        r = QRectF(self._rect)
        size = self._rect.size()
        size.setWidth(self.sceneWidth() - self.textPadding)
        # r.setSize(self._rect.size() / scale)
        r.setSize(size / self.painterTextScale)
        r.moveCenter(self._rect.center())
        self.painterTextRect = r

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):

        # painter.setClipRect(option.exposedRect)
        # painter.setClipRegion(QRegion(option.exposedRect.toRect()))

        if not self._pen.width():
            painter.setPen(Qt.NoPen)
        else:
            painter.setPen(self._pen)
        # painter.setPen(QPen(self.cizgiRengi))
        painter.setBrush(self._brush)
        # !! eger kareyi burda cizersek, az sonra cizilen textin alphasinda problem oluyor.
        #   alphayi azalttikca yazi siyahlasiyor, en sonda 0 olunca kayboluyor.
        #   -- o yuzden texti cidikten sonra ciziyoruz bu kareyi deyip bunu iptal etmistik--
        #   ama self.cizgiRengini, QColor().fromrgb ile teker teker aynen yeniden olsuturunca
        #   ve bu yeni kopya renk ile pen olusturunca calısıyor. self.setCizgRengi nde bu islem,
        painter.drawRect(self._rect)

        if self._text:
            # painter.setWorldMatrixEnabled(False)
            painter.save()
            painter.setFont(self._font)
            painter.setPen(
                self.textPen)  # we recreate textPen from same exact color. otherwise, color's alpha not working.
            painter.translate(self._rect.center())
            painter.rotate(-self.rotation())

            painter.scale(self.painterTextScale, self.painterTextScale)
            painter.translate(-self._rect.center())

            # ---------------------------------------------------------------------
            # --  basla --  elided text cizmek icin --
            # ---------------------------------------------------------------------
            # metrics = painter.fontMetrics()
            # txt = metrics.elidedText(self._text, Qt.ElideRight, self._rect.width() / scale)
            # # Qt.AlignCenter hem AlignVCenter hem de AlignHCenter icin yeterli
            # # ayrica en fazla iki tane kullanilabiliyormus, ve AlignCenter 2 tane sayiliyormus.
            # # painter.drawText(self._rect, Qt.AlignCenter | Qt.AlignVCenter, txt)
            # painter.drawText(self._rect, Qt.AlignCenter, txt)
            # ---------------------------------------------------------------------
            # ---  bitir --- elided text cizmek icin --
            # ---------------------------------------------------------------------

            # painter.drawRect(r)
            # painter.drawText(self._rect, self._text, self.painterTextOption)
            painter.drawText(self.painterTextRect, self._text, self.painterTextOption)

            # painter.drawText(10,10, txt)
            painter.restore()
            # painter.setWorldMatrixEnabled(True)

        # if option.state & QStyle.State_MouseOver:
        if option.state & QStyle.State_Selected or self.cosmeticSelect:
            # painter.setPen(QPen(option.palette.windowText(), 0, Qt.DashLine))
            # painter.setPen(QPen(option.palette.highlight(), 0, Qt.DashLine))

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
            # if not self.isPinned and not self.isFrozen and self.isActiveItem:
            #     # painter.setPen(self.handlePen)
            #     painter.drawRect(self.topLeftHandle)
            #     painter.drawRect(self.topRightHandle)
            #     painter.drawRect(self.bottomRightHandle)
            #     painter.drawRect(self.bottomLeftHandle)
            ########################################################################

        # font = painter.font()
        # font.setPointSize(self.fontPointSize)
        # painter.setFont(font)

        # # karenin altina yazsin yaziyi amcli ama bounding bozu degistirmek lazim.
        # # klasin simdilik.
        # # metrics.size() # this is metrics.boundingRect() size.
        # rect = metrics.boundingRect(self.text)
        # rect.moveTop(brect.bottom())
        # painter.drawText(rect, Qt.AlignCenter, self.text)

        # # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self.rect(), "{0:.2f},  {1:.2f}\n{2:.2f},  {3:.2f}".format(p.x(), p.y(), s.x(), s.y()))
        # # t = self.transformOriginPoint()
        # # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self.rect().topLeft())
        # painter.drawText(self.rect().x(), self.rect().y(), "{0:.2f}  {1:.2f}".format(mapped.x(), mapped.y()))
        # r = self.textItem.boundingRect()
        # r = self.mapRectFromItem(self.textItem, r)
        # painter.drawRect(r)
        # painter.drawText(self.rect().center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):
        # if change == self.ItemPositionChange:
        # if change == self.ItemSelectedChange:
        # if change == self.ItemSelectedHasChanged:
        if change == self.ItemSelectedChange:
            if value:
                self.scene().parent().item_selected(self)
            else:
                self.scene().parent().item_deselected(self)

        # if change == self.ItemSceneChange:
        #     print(value, "eveeeet")
        # elif change == self.ItemParentChange:
        #     if value:
        #         if value.type() == QGraphicsItem.UserType + 7:  # this is Group's custom type value,
        #             print("evet")

        # return QGraphicsRectItem.itemChange(self, change, value)
        return value
        # super(Rect, self).itemChange(change, value)

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
    def mouseDoubleClickEvent(self, event):
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
        self.tempTextItem.setCenter(self.rect().center())
        self.tempTextItem.setFocus()

        # !! burda lambda kullanmazsak, self.is_temp_text_item_empty ,self daha olsumadigi icin,
        # selfi null olarak goruyor ve baglanti kuramiyor.
        self.tempTextItem.textItemFocusedOut.connect(lambda: self.temp_text_item_focused_out())

        super(BaseItem, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    @Slot()
    def temp_text_item_focused_out(self):
        tmpText = self.tempTextItem.toPlainText()
        self.scene().undoRedo.undoableItemSetText(self.scene().undoStack, "change text", self,
                                                  self.tempEskiText, tmpText)
        # if not tmpText:
        self.scene().removeItem(self.tempTextItem)
        self.tempTextItem.deleteLater()
        self.tempTextItem = None

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):

        # item ok tuslari ile hareket scene icinde

        # if event.modifiers() & Qt.ControlModifier:
        #     if event.key() == Qt.Key_Up:
        #         self.moveBy(0, -10)
        #     if event.key() == Qt.Key_Down:
        #         self.moveBy(0, 10)
        #     if event.key() == Qt.Key_Right:
        #         self.moveBy(10, 0)
        #     if event.key() == Qt.Key_Left:
        #         self.moveBy(-10, 0)

        super(BaseItem, self).keyPressEvent(event)

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
                self._fixedResizePoint = self.rect().bottomRight()
                self._resizingFrom = 1
            elif self.topRightHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self.rect().bottomLeft()
                self._resizingFrom = 2
            elif self.bottomRightHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self.rect().topLeft()
                self._resizingFrom = 3
            elif self.bottomLeftHandle.contains(event.pos()):
                self._resizing = True
                self._fixedResizePoint = self.rect().topRight()
                self._resizingFrom = 4
            self._eskiRectBeforeResize = self.rect()

        super(BaseItem, self).mousePressEvent(event)

        # TODO: bu kozmetik amacli, sadece release de olunca gecikmeli seciyormus hissi oluyor
        if self.isSelected() and self.childItems():
            self.scene().select_all_children_recursively(self, cosmeticSelect=True)

        # self.scene().deactivate_item(self)
        # self.scene().activate_item(self)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if self._resizing:
            # sahneye ilk cizim kontrolu,(undoya eklemesin diye)
            if not self._eskiRectBeforeResize.size() == QSizeF(1, 1):
                rect = self.rect()
                self.setPos(self.mapToScene(rect.topLeft()))
                rect.moveTo(0, 0)
                self.scene().undoRedo.undoableResizeBaseItem(self.scene().undoStack,
                                                             "resize",
                                                             self,
                                                             # yeniRect=self.rect(),
                                                             yeniRect=rect,
                                                             eskiRect=self._eskiRectBeforeResize,
                                                             eskiPos=self._eskiPosBeforeResize)
            # TODO: bu satir eger cizim disari tasarsa, scene recti ona uygun ayarlamak icin
            # fakat eger cizim disari tasarsa evet uyarliyor ama bazen de çizilen itemin geometrisini degistiriyor.
            # o yuzden simdilik iptal.
            # self.scene().unite_with_scene_rect(self.sceneBoundingRect())
            self._resizing = False

            self.update_painter_text_rect()
            self.scene().unite_with_scene_rect(self.sceneBoundingRect())
        super(BaseItem, self).mouseReleaseEvent(event)

        if self.childItems():
            if self.isSelected():
                self.scene().select_all_children_recursively(self, cosmeticSelect=False, topmostParent=True)
            else:
                self.scene().select_all_children_recursively(self, cosmeticSelect=False)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        # TODO: burda QRectF().normalized da kullanilabilir belki..

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
                eskiSize = self.rect().size()
                # eskiSize.scale(yeniSize, Qt.KeepAspectRatio)
                eskiSize.scale(yeniSize.height(), yeniSize.height(), Qt.KeepAspectRatioByExpanding)
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

            self.setRect(rect)  # mouse release eventten gonderiyoruz undoya
            self.update_resize_handles()
            self.scene().parent().change_transform_box_values(self)
            # self.setPos(x, y)
            # return QGraphicsItem.mouseMoveEvent(self, event)

            self.update_painter_text_rect()

        # event.accept()
        else:
            super(BaseItem, self).mouseMoveEvent(event)

        # super(BaseItem, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverEnterEvent(self, event):
        # TODO: bu hoverlarda bu kareler yerine mouse icon
        # degisse koselere ykenarlar ayaklastikca
        # TODO: bu saved cursor olmadi tam.
        # if self.isSelected() and not self.isFrozen:
        self.saved_cursor = self.scene().parent().cursor()

        super(BaseItem, self).hoverEnterEvent(event)

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

        super(BaseItem, self).hoverMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverLeaveEvent(self, event):
        # self.sagUstKare.hide()
        if self.isSelected() and not self.isFrozen:
            # self.scene().parent().setCursor(Qt.ArrowCursor)
            self.scene().parent().setCursor(self.saved_cursor)

        super(BaseItem, self).hoverLeaveEvent(event)

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
                super(BaseItem, self).wheelEvent(event)

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            if not self.isFrozen:
                self.rotateItem(event.delta())
            else:
                super(BaseItem, self).wheelEvent(event)

        # elif event.modifiers() & Qt.AltModifier:
        elif toplam == alt:
            self.changeBackgroundColorAlpha(event.delta())

        elif toplam == ctrlAlt:
            self.changeTextColorAlpha(event.delta())

        elif toplam == ctrlAltShift:
            self.changeFontSize(event.delta())
        #
        elif toplam == altShift:
            # self.changeImageItemTextBackgroundColorAlpha(event.delta())
            self.changeLineColorAlpha(event.delta())
        #
        # elif toplam == ctrlAltShift:
        #     if not self.isFrozen:
        #         self.scaleItemByResizing(event.delta())
        #     else:
        #         super(BaseItem, self).wheelEvent(event)

        else:
            super(BaseItem, self).wheelEvent(event)

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
    def scaleItemByResizing(self, delta):
        # TODO : size sıfır olmasin kontrolu

        scaleFactor = 1.1
        center = self.rect().center()
        if delta > 0:
            rect = QRectF(self.rect().topLeft(), self.rect().size() * scaleFactor)
            rect.moveCenter(center)
            # self.setPos(self.mapToScene(rect.topLeft()))
            # rect.moveTo(0,0)
            # self.setRect(rect)
            self.scene().undoRedo.undoableScaleBaseItemByResizing(self.scene().undoStack, "scale by resizing",
                                                                  self, rect)
            self.scene().unite_with_scene_rect(self.sceneBoundingRect())

        else:
            rect = QRectF(self.rect().topLeft(), self.rect().size() * 1 / scaleFactor)
            rect.moveCenter(center)
            # self.setRect(rect)

            self.scene().undoRedo.undoableScaleBaseItemByResizing(self.scene().undoStack, "scale by resizing",
                                                                  self, rect)

        # bunu undoableScaleBaseItemByResizing icinden cagiriyoruz.
        self.update_painter_text_rect()

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
    def repositionChildItems(self, diff):
        # TODO: item rotation 0 olmadigi durumlarda calismiyor , kaymalar oluyor.
        for c in self.childItems():
            c.moveBy(-diff.x(), -diff.y())

    # ---------------------------------------------------------------------
    def scaleWithOffset(self, scale):
        cEski = self.sceneCenter()
        self.setScale(scale)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())
        # self.update_resize_handles() # TODO: we use this because of scaled group's ungroup.
        self.update_painter_text_scale()
        self.update_painter_text_rect()

    # ---------------------------------------------------------------------
    def setScale(self, scale):
        super(BaseItem, self).setScale(scale)
        self.update_resize_handles()

    # ---------------------------------------------------------------------
    def rotateWithOffset(self, angle):
        # 1Million thanks to this guy.
        # https://stackoverflow.com/a/32734103
        # ayrica bu rotate with offsetlerde mod 360 yapmiyoruz
        # cunku buraya gelen illaki modlanmis geliyor.
        # bunu niye yazdim. undoya gitmeden rotate olabiliyor bununla,
        # (undoRotatelerde mod var.)
        cEski = self.sceneCenter()
        self.setRotation(angle)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())
        self.update_painter_text_rect()

    # ---------------------------------------------------------------------
    def rotateItem(self, delta):
        # transform = QTransform()
        # transform.rotate(5)
        # self.setTransformOriginPoint(self.rect().center())
        # self.setTransform(transform)
        # print(self.transformOriginPoint())
        # self.setRotation(self.rotation() + 5)

        # x = self.rect().center().x()
        # y = self.rect().center().y()
        # self.setTransform(QTransform().translate(x, y).rotate(45).translate(-x, -y))

        # self.translate(x,y)
        # self.setRotation(self.rotation() + 5)
        # self.translate(-x,-y)
        # self.setTransformOriginPoint(self.rect().center())
        if delta > 0:
            # self.setRotation(self.rotation() + 5)
            self.scene().undoRedo.undoableRotateBaseItem(self.scene().undoStack, "rotate", self,
                                                         self.rotation() + 5)
            # self.rotateWithOffset(self.rotation() + 5, self)

        else:
            # self.setRotation(self.rotation() - 5)
            self.scene().undoRedo.undoableRotateBaseItem(self.scene().undoStack, "rotate", self,
                                                         self.rotation() - 5)
            # self.rotateWithOffset(self.rotation() - 5, self)
        self.update_painter_text_rect()
        # self.update()

    # ---------------------------------------------------------------------
    def changeBackgroundColorAlpha(self, delta):

        col = shared.calculate_alpha(delta, QColor(self.arkaPlanRengi))

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
                                                                      "change item's background alpha",
                                                                      self, col)

    # ---------------------------------------------------------------------
    def changeLineColorAlpha(self, delta):

        # col = shared.calculate_alpha(delta, self._pen.color())
        col = shared.calculate_alpha(delta, self.cizgiRengi)

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
