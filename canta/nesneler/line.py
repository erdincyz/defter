# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '02/Nov/2018'
__author__ = 'Erdinç Yılmaz'

import math
from PySide6.QtCore import Qt, QRectF, QSizeF, QPointF, QLineF, QBuffer, QIODevice, QSize
from PySide6.QtGui import QPainterPath, QPainterPathStroker, QPen, QColor, QTransform, QPolygonF, QTextOption, QBrush, \
    QPainter
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QGraphicsItem, QStyle
from canta import shared
from canta.nesneler.tempTextItem import TempTextItem


########################################################################
class LineItem(QGraphicsItem):
    Type = shared.LINE_ITEM_TYPE

    def __init__(self, pos, pen, yaziRengi=None, font=None, line=None, parent=None):
        super(LineItem, self).__init__(parent)

        self._kim = shared.kim(kac_basamak=16)

        self.setAcceptHoverEvents(True)

        # cizim icin False baslamak dogru olabilirdi ama
        # kopyalama ve dosyadan yukleme gibi durumlarda bu false kalıyor
        # o yuzden True baslayip, cizim de ilk noktada(move_start_point) False ediyoruz
        self.isDrawingFinished = True

        self.okBoyutu = pen.widthF() * 3
        self.ok_polygon = QPolygonF()
        # self.ok_polygon << QPoint(-5, 0) << QPoint(5, 0) << QPoint(0, 5) << QPoint(-5, 0)

        self._line = QLineF()

        self.setPos(pos)

        self.secili_nesne_kalem_kalinligi = 0

        self.handleSize = 25
        self.resizeHandleSize = QSizeF(self.handleSize, self.handleSize)
        self.create_resize_handles()

        if line:
            self.setLine(line)

        self.initialFlags = self.flags()
        self.setFlags(self.ItemIsSelectable |
                      self.ItemIsMovable |
                      self.ItemIsFocusable)

        self._pen = pen
        self._font = font

        self.activeItemLineColor = shared.activeItemLineColor
        self.cizgiRengi = pen.color()
        self.setCizgiRengi(self.cizgiRengi)  # also sets self._pen
        self.yaziRengi = yaziRengi
        self.setYaziRengi(yaziRengi)

        self.tempTextItem = None
        self.tempEskiText = ""
        self.textPadding = 2

        self.painterTextOption = QTextOption()
        self.painterTextOption.setAlignment(Qt.AlignCenter)
        self.painterTextOption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        self.painterTextScale = 1
        self.painterTextRect = QRectF()

        self.cosmeticSelect = False
        self.isActiveItem = False
        self._isPinned = False

        self._text = ""
        self._command = {}

        # self.editMode = False

        self.baglanmis_nesneler = {}
        self.oklar_dxdy_nokta = {}

    # ---------------------------------------------------------------------
    def type(self):
        return LineItem.Type

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      # "painterPath": self.path(),
                      "kim": self._kim,
                      "line": self._line,
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "scale": self.scale(),
                      "zValue": self.zValue(),
                      "pen": self._pen,
                      "font": self._font,
                      "yaziHiza": int(self.painterTextOption.alignment()),
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "command": self._command,
                      "baglanmis_nesneler": self.baglanmis_nesneler,
                      }
        return properties

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
    def varsaEnUsttekiGrubuGetir(self):
        parentItem = self.parentItem()
        while parentItem:
            if parentItem.type() == shared.GROUP_ITEM_TYPE:
                return parentItem
            parentItem = parentItem.parentItem()
        return None

    # ---------------------------------------------------------------------
    def move_start_point(self):
        self.isDrawingFinished = False
        # point = self.mapFromScene(point)
        point = QPointF(0, 0)
        self.line().setP1(point)

    # ---------------------------------------------------------------------
    def temp_prepend(self, point):
        point = self.mapFromScene(point)
        line = QLineF(self._line)
        line.setP1(point)
        self.setLine(line)
        self.update_resize_handles()

    # ---------------------------------------------------------------------
    def temp_append(self, point):
        point = self.mapFromScene(point)
        line = QLineF(self._line)
        line.setP2(point)
        self.setLine(line)
        self.update_resize_handles()
        sahne_acisi = f"\u2220  {((self._line.angle() - self.rotation()) % 360):.1f}\N{DEGREE SIGN}"
        self.scene().parent().log(txt=sahne_acisi, toStatusBarOnly=True)

    # ---------------------------------------------------------------------
    def create_resize_handles(self):
        self.p1Handle = QRectF(self._line.p1(), self.resizeHandleSize)
        self.p2Handle = QRectF(self._line.p2(), self.resizeHandleSize)

        # initial move
        self.p2Handle.moveCenter(self._line.p2())
        # self.bottomRightHandle.moveBottomRight(self.rect().bottomRight())
        # self.bottomLeftHandle.moveBottomLeft(self.rect().bottomLeft())

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

            self.p1Handle.setSize(self.resizeHandleSize)
            self.p2Handle.setSize(self.resizeHandleSize)

        self.p1Handle.moveCenter(self._line.p1())
        self.p2Handle.moveCenter(self._line.p2())

    # ---------------------------------------------------------------------
    def hide_resize_handles(self):
        self.isPinned = True

    # ---------------------------------------------------------------------
    def show_resize_handles(self):
        self.isPinned = False

    # ---------------------------------------------------------------------
    def setArkaPlanRengi(self, col):
        # dummy method
        pass

    # ---------------------------------------------------------------------
    def brush(self):
        # bu nesnede brush kullanmiyoruz ama diger nesnelerin ilgili methodlariyla uyumlu olsun diye
        # ekliyoruz, setArkaplanRengi de bu minvalde
        # return Qt.NoBrush
        return QBrush()

    # ---------------------------------------------------------------------
    def is_temp_text_item_empty(self):
        tmpText = self.tempTextItem.toPlainText()
        self.scene().undoRedo.undoableItemSetText(self.scene().undoStack, "change text", self,
                                                  self.tempEskiText, tmpText)
        # if not tmpText:
        self.scene().removeItem(self.tempTextItem)
        self.tempTextItem.deleteLater()
        self.tempTextItem = None

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
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
            self.update_painter_text_rect()

        super(LineItem, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):

        self._resizing = False  # we could use "self._resizingFrom = 0" instead, but self._resizing is more explicit.
        self._fixedResizePoint = None
        self._resizingFrom = None
        self._eskiLineBeforeResize = None

        self._eskiPosBeforeResize = self.pos()

        if self.p1Handle.contains(event.pos()):
            self._resizing = True
            self._fixedResizePoint = self._line.p2()
            self._resizingFrom = 1
        elif self.p2Handle.contains(event.pos()):
            self._resizing = True
            self._fixedResizePoint = self._line.p1()
            self._resizingFrom = 2
        self._eskiLineBeforeResize = self.line()

        super(LineItem, self).mousePressEvent(event)

        # TODO: bu kozmetik amacli, sadece release de olunca gecikmeli seciyormus hissi oluyor
        if self.isSelected() and self.childItems():
            self.scene().select_all_children_recursively(self, cosmeticSelect=True)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if self._resizing:
            # sahneye ilk cizim kontrolu,(undoya eklemesin diye)
            if not self._eskiLineBeforeResize.length() == 0:
                line = self.line()
                self.scene().undoRedo.undoableResizeLineItem(self.scene().undoStack,
                                                             "resize",
                                                             self,
                                                             # yeniRect=self.rect(),
                                                             yeniLine=line,
                                                             eskiLine=self._eskiLineBeforeResize,
                                                             eskiPos=self._eskiPosBeforeResize,
                                                             degisenNokta=self._resizingFrom)
            # # TODO: bu satir eger cizim disari tasarsa, scene recti ona uygun ayarlamak icin
            # fakat eger cizim disari tasarsa evet uyarliyor ama bazen de çizilen itemin geometrisini degistiriyor.
            # o yuzden simdilik iptal.
            # self.scene().unite_with_scene_rect(self.sceneBoundingRect())
            self._resizing = False
            self.scene().unite_with_scene_rect(self.sceneBoundingRect())
            self.update_painter_text_rect()

        super(LineItem, self).mouseReleaseEvent(event)

        if self.childItems():
            if self.isSelected():
                self.scene().select_all_children_recursively(self, cosmeticSelect=False, topmostParent=True)
            else:
                self.scene().select_all_children_recursively(self, cosmeticSelect=False)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        if self._resizing:

            if self._resizingFrom == 1:
                p1 = event.pos()
                p2 = self._fixedResizePoint

            elif self._resizingFrom == 2:
                p1 = self._fixedResizePoint
                p2 = event.pos()

            line = QLineF(p1, p2)

            # shift ile kullaniyoruz
            eski_aci = self._eskiLineBeforeResize.angle()

            # Alt Key - to resize around center.
            if event.modifiers() & Qt.AltModifier:
                # burda da orta nokta sabit
                # c = self.line().center() # ile
                # ve de eski aci ile, belki bir cizgi hareket eden noktadan merkeze
                # sonra da length *2, tabi hangi nokta tutuldu ise p2, p2 ona gore ayarlanmali ok icin
                pass

            # ---------------------------------------------------------------------
            #  Ctrl Key - 45 derece ve katlarina kilitlemek icin
            if event.modifiers() & Qt.ControlModifier:
                if self._resizingFrom == 1:
                    line = QLineF(line.p2(), line.p1())

                if line.dx():  # zero division error
                    yeni_aci = 0
                    aci = math.atan2(-line.dy(), line.dx())
                    # print(aci)
                    aci = aci * 180 / math.pi
                    # print(aci)

                    if -180 <= aci < -165:
                        yeni_aci = 180
                    elif -165 <= aci < -120:
                        yeni_aci = 225
                    elif -120 <= aci < -75:
                        yeni_aci = 270
                    elif -75 <= aci < -30:
                        yeni_aci = 315
                    if -30 <= aci < 30:
                        yeni_aci = 0
                    elif 30 <= aci < 75:
                        yeni_aci = 45
                    elif 75 <= aci < 120:
                        yeni_aci = 90
                    elif 120 <= aci < 165:
                        yeni_aci = 135
                    elif aci >= 165:
                        yeni_aci = 180

                    line.setAngle(yeni_aci)

                    if self._resizingFrom == 1:
                        line = QLineF(line.p2(), line.p1())

            # ---------------------------------------------------------------------
            # Shift Key - cizgi uzunlugu değiştiriken açıyı değiştirmek için
            if event.modifiers() & Qt.ShiftModifier:
                if self._resizingFrom == 1:
                    line = QLineF(line.p2(), line.p1())
                    line.setAngle(180 + eski_aci)
                    line = QLineF(line.p2(), line.p1())
                elif self._resizingFrom == 2:
                    line.setAngle(eski_aci)

            self.setLine(line)  # mouse release eventten gonderiyoruz undoya
            self.update_resize_handles()
            self.update_painter_text_rect()
            self.scene().parent().change_transform_box_values(self)

            # TODO: self.rotation() degeri, self._line.angle() ile degissin, yani setPos ile
            # pozisyonu da ayarlamak lazım.

            sahne_acisi = f"\u2220  {((self._line.angle() - self.rotation()) % 360):.1f}\N{DEGREE SIGN}"
            self.scene().parent().log(txt=sahne_acisi, toStatusBarOnly=True)
            # self.setPos(x, y)
            # return QGraphicsItem.mouseMoveEvent(self, event)

        # event.accept()
        else:
            super(LineItem, self).mouseMoveEvent(event)

        # super(BaseItem, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverEnterEvent(self, event):
        # event propagationdan dolayi bos da olsa burda implement etmek lazim
        # mousePress,release,move,doubleclick de bu mantıkta...
        # baska yerden baslayip mousepress ile , mousemove baska, mouseReleas baska widgetta gibi
        # icinden cikilmaz durumlara sebep olabiliyor.
        # ayrica override edince accept() de edilmis oluyor mouseeventler
        super(LineItem, self).hoverEnterEvent(event)

    # ---------------------------------------------------------------------
    def hoverMoveEvent(self, event):
        # self.sagUstKare.hide()

        # cursor = self.scene().parent().cursor()

        # if self.isSelected():
        if self.scene().toolType == self.scene().NoTool:
            if self.p1Handle.contains(event.pos()) or self.p2Handle.contains(event.pos()):
                self.scene().parent().setCursor(Qt.SizeAllCursor, gecici_mi=True)
            else:
                self.scene().parent().setCursor(self.scene().parent().imlec_arac, gecici_mi=True)

        super(LineItem, self).hoverMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverLeaveEvent(self, event):

        self.scene().parent().setCursor(self.scene().parent().imlec_arac, gecici_mi=True)

        super(LineItem, self).hoverLeaveEvent(event)

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
    def itemChange(self, change, value):
        # if change == self.ItemPositionChange:
        # if change == self.ItemSelectedChange:
        # if change == self.ItemSelectedHasChanged:
        if change == self.ItemSelectedChange:
            if value:
                self.scene().parent().line_item_selected(self)
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
        return self.mapToScene(self.line().center())

    # ---------------------------------------------------------------------
    def sceneWidth(self):
        return self.sceneRight() - self.sceneLeft()

    # ---------------------------------------------------------------------
    def sceneHeight(self):
        return self.sceneBottom() - self.sceneTop()

    # ---------------------------------------------------------------------
    def sceneRight(self):

        # p1 = self.mapToScene(self._line.p1())
        # p2 = self.mapToScene(self._line.p2())
        # return max(p1.x(), p2.x())

        # kalem ve ok ucu kalingligi dahil edildi
        rect = self.mapRectToScene(self.shape().controlPointRect())
        return rect.right()

    # ---------------------------------------------------------------------
    def sceneLeft(self):

        # p1 = self.mapToScene(self._line.p1())
        # p2 = self.mapToScene(self._line.p2())
        # return min(p1.x(), p2.x())

        # kalem ve ok ucu kalingligi dahil edildi
        rect = self.mapRectToScene(self.shape().controlPointRect())
        return rect.left()

    # ---------------------------------------------------------------------
    def sceneTop(self):
        # p1 = self.mapToScene(self._line.p1())
        # p2 = self.mapToScene(self._line.p2())
        # return min(p1.y(), p2.y())

        # kalem ve ok ucu kalingligi dahil edildi
        rect = self.mapRectToScene(self.shape().controlPointRect())
        return rect.top()

    # ---------------------------------------------------------------------
    def sceneBottom(self):
        # p1 = self.mapToScene(self._line.p1())
        # p2 = self.mapToScene(self._line.p2())
        # return max(p1.y(), p2.y())

        # kalem ve ok ucu kalingligi dahil edildi
        rect = self.mapRectToScene(self.shape().controlPointRect())
        return rect.bottom()

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
    def length(self):
        return self._line.length()

    # ---------------------------------------------------------------------
    def line(self):
        return self._line

    # ---------------------------------------------------------------------
    def setLine(self, line):
        if self._line == line:
            return
        self._line = line
        self._boundingRect = QRectF()
        self.ok_ucu_guncelle()
        self.prepareGeometryChange()
        self.update()

    # ---------------------------------------------------------------------
    def ok_ucu_guncelle(self):
        # line = self._line
        line = QLineF(self._line)
        try:
            angle = math.acos(line.dx() / line.length())
        except ZeroDivisionError:
            return

        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        # line.setLength(line.length() + self.okBoyutu * .87)
        line.setLength(line.length() + self.okBoyutu * 0.45)

        okP1 = line.p2() - QPointF(math.sin(angle + math.pi / 3.0) * self.okBoyutu,
                                   math.cos(angle + math.pi / 3.0) * self.okBoyutu)
        okP2 = line.p2() - QPointF(math.sin(angle + math.pi - math.pi / 3.0) * self.okBoyutu,
                                   math.cos(angle + math.pi - math.pi / 3.0) * self.okBoyutu)

        self.ok_polygon.clear()
        for point in [line.p2(), okP1, okP2]:
            self.ok_polygon.append(point)
        self.update_resize_handles()

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
    def setCizgiKalinligi(self, width):
        self._pen.setWidthF(width)
        self.okBoyutu = width * 3
        self.ok_ucu_guncelle()
        # self.textPen.setWidthF(width)

        # self.selectionPenBottom.setWidthF(width)
        # self.selectionPenBottomIfAlsoActiveItem.setWidthF(width)
        # self.selectionPenTop.setWidthF(width)

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
    def update_painter_text_scale(self):
        if self.parentItem():
            a = self.parentItem().scale()
        else:
            a = 1
        self.painterTextScale = 1 / self.scale() / a

    # ---------------------------------------------------------------------
    def update_painter_text_rect(self):
        r = QRectF()
        r.setWidth(self._line.length())
        # r.setWidth(max(self._line.length(), self.fontPointSize()))
        # r.setHeight(self.fontPointSize()- self.textPadding)
        # r.setHeight(self.fontPointSize() + 30)
        # fontPixelSize = self.fontPointSize() / 72 * self.scene().parent().dpi
        r.setHeight(self.fontPointSize())
        # r.setSize(size / self.painterTextScale)
        # r.moveCenter(self.boundingRect().center())
        yeniOrtaNokta = self._line.center()
        yeniOrtaNokta.setY(yeniOrtaNokta.y() - self._pen.widthF())
        # yeniOrtaNokta.setY(yeniOrtaNokta.y() - r.height())
        r.moveCenter(yeniOrtaNokta)
        self.painterTextRect = r

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
    def flipHorizontal(self, mposx):
        lc = self.mapToScene(self._line.center())
        diff = mposx - lc.x()
        ipos = self.scenePos()
        ipos.setX(ipos.x() + 2 * diff)

        p1 = self._line.p1()
        p2 = self._line.p2()
        eskiP1x = p1.x()
        p1.setX(p2.x())
        p2.setX(eskiP1x)
        self.setLine(QLineF(p1, p2))

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
        lc = self.mapToScene(self._line.center())
        diff = mposy - lc.y()
        ipos = self.scenePos()
        ipos.setY(ipos.y() + 2 * diff)

        p1 = self._line.p1()
        p2 = self._line.p2()
        eskiP1y = p1.y()
        p1.setY(p2.y())
        p2.setY(eskiP1y)
        self.setLine(QLineF(p1, p2))

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
        p = ps.createStroke(path)  # returns QPainterPath
        p.addPath(path)
        return p

    # ---------------------------------------------------------------------
    def boundingRect(self):

        """
        QRectF QGraphicsLineItem::boundingRect() const
        {
            Q_D(const QGraphicsLineItem);
            if (d->pen.widthF() == 0.0) {
                const qreal x1 = d->line.p1().x();
                const qreal x2 = d->line.p2().x();
                const qreal y1 = d->line.p1().y();
                const qreal y2 = d->line.p2().y();
                qreal lx = qMin(x1, x2);
                qreal rx = qMax(x1, x2);
                qreal ty = qMin(y1, y2);
                qreal by = qMax(y1, y2);
                return QRectF(lx, ty, rx - lx, by - ty);
            }
            return shape().controlPointRect();
        }

        """
        rect = self.shape().controlPointRect()
        return rect

    # ---------------------------------------------------------------------
    def shape(self):

        path = QPainterPath()
        if self.line() == QLineF():
            return path
        path.moveTo(self._line.p1())
        path.lineTo(self._line.p2())
        path.addPolygon(self.ok_polygon)
        path.addRect(self.p1Handle)
        path.addRect(self.p2Handle)

        if self._text:
            # path addText kullanmadik, ok uzunlugu kısalınca yazının hepsini gostermese de kareye ekliyor.
            # painterTextRecti okla beraber dondurup donmus dortgenin boundinRectini alip ekliyoruz
            # c = self._line.center()
            # t = QTransform().translate(c.x(), c.y()).rotate(- self._line.angle()).translate(-c.x(), -c.y())
            # self.rpoly = t.mapToPolygon(self.painterTextRect.toRect())
            # path.addRect(self.rpoly.boundingRect())

            path.addRect(self.painterTextRect)

        # kalem kalinligini da ekliyoruz
        path = self.qt_graphicsItem_shapeFromPath(path, self.pen())
        return path

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
            self.scaleItem(event.delta())

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            self.rotateItem(event.delta())

        # elif event.modifiers() & Qt.AltModifier:
        elif toplam == alt:
            # self.changeBackgroundColorAlpha(event.delta())
            self.changeLineColorAlpha(event.delta())

        elif toplam == ctrlAlt:
            self.changeTextColorAlpha(event.delta())

        elif toplam == ctrlAltShift:
            self.changeFontSize(event.delta())

        elif toplam == altShift:
            if self.isDrawingFinished:
                self._cizgi_kalinligi_degistir_undo_ile(event.delta())
            # else:
            # self.scene().tekerlek_ile_firca_boyu_degistir(event.delta())

        if not self.isDrawingFinished:
            self.scene().tekerlek_ile_firca_boyu_degistir(event.delta())

        # elif toplam == ctrlAltShift:
        #     self.scaleItemByScalingPath(event.delta())

        else:
            super(LineItem, self).wheelEvent(event)

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
            self.scene().undoableScaleLineItemByScalingPath("scale", self, scaledPath)
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
            self.scene().undoableScaleLineItemByScalingPath("scale", self, scaledPath)

            # bunu undoableScaleLineItemByScalingPath icinden cagiriyoruz

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
        # self.updateBoundingRect()
        self.update_painter_text_scale()

    # ---------------------------------------------------------------------
    def rotateWithOffset(self, angle):
        cEski = self.sceneCenter()
        self.setRotation(angle)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())

    # ---------------------------------------------------------------------
    def rotateItem(self, delta):
        if not self.isDrawingFinished:
            return

        # self.setTransformOriginPoint(self.boundingRect().center())
        if delta > 0:
            # self.setRotation(self.rotation() + 5)
            # bu p1 den rotate ediyor
            # self.scene().undoableRotate("Rotate", self, self.rotation() + 5)
            self.scene().undoRedo.undoableRotateWithOffset(self.scene().undoStack, "rotate", self, self.rotation() + 5)
        else:
            # self.setRotation(self.rotation() - 5)
            # bu p1 den rotate ediyor
            # self.scene().undoableRotate("Rotate", self, self.rotation() - 5)
            self.scene().undoRedo.undoableRotateWithOffset(self.scene().undoStack, "rotate", self, self.rotation() - 5)
        # self.update()
        self.update_painter_text_rect()

    # # ---------------------------------------------------------------------
    # def changeBackgroundColorAlpha(self, delta):
    #
    #     col = shared.calculate_alpha(delta, QColor(self.arkaPlanRengi))
    #
    #     # self.setBrush(self.arkaPlanRengi)
    #     # self.update()
    #     # self.scene().undoableSetItemBackgroundColorAlpha("Change item's background alpha", self, col)
    #
    #     if self.childItems():
    #         self.scene().undoStack.beginMacro("change items' background alpha")
    #         self.scene().undoRedo.undoableSetItemBackgroundColorAlpha(self.scene().undoStack,
    #                                                                   "_change item's background alpha",
    #                                                                   self, col)
    #         for c in self.childItems():
    #             c.changeBackgroundColorAlpha(delta)
    #         self.scene().undoStack.endMacro()
    #     else:
    #         self.scene().undoRedo.undoableSetItemBackgroundColorAlpha(self.scene().undoStack,
    #                                                                   "change item's background alpha",
    #                                                                   self, col)
    # ---------------------------------------------------------------------
    def _cizgi_kalinligi_degistir_undo_ile(self, delta):

        if delta > 0:
            cap = self.scene().parent().fircaBuyult()
        else:
            cap = self.scene().parent().fircaKucult()

        self.scene().undoRedo.undoableSetLineWidthF(self.scene().undoStack, "change item's line width", self,
                                                    cap)

    # ---------------------------------------------------------------------
    def changeLineColorAlpha(self, delta):

        col = shared.calculate_alpha(delta, self._pen.color())

        # self.scene().undoableSetLineOrTextColorAlpha("Change item's line alpha", self, col)
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
    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.drawLine(self._line)
        painter.setBrush(self._pen.color())
        # painter.drawEllipse(self._line.p1(), 5,5)

        painter.setPen(Qt.NoPen)
        painter.drawConvexPolygon(self.ok_polygon)
        # painter.drawPolygon(self.ok_polygon)
        # painter.drawText(20,20,str(self._line.angle()))

        # drawlines, polygon, polyline

        # path = QPainterPath()
        # path.moveTo(20, 80)
        # path.lineTo(20, 30)
        # path.cubicTo(80, 0, 50, 50, 80, 80)
        #
        # painter.drawPath(path)
        # painter.drawPath(self.shape())
        # painter.drawRect(self.boundingRect())

        if self._text:
            # painter.setWorldMatrixEnabled(False)
            painter.save()
            painter.setFont(self._font)
            # painter.setPen(self.textPen)
            painter.setPen(self.yaziRengi)
            painter.translate(self.line().center())
            # aci = math.atan2(-self._line.dy(), self._line.dx())
            # aci = aci * 180 / math.pi
            # painter.rotate(- aci)
            painter.rotate(- self._line.angle())
            painter.scale(self.painterTextScale, self.painterTextScale)
            painter.translate(-self.line().center())
            # painter.drawText(self.boundingRect(), Qt.AlignCenter | Qt.AlignVCenter, self._text)
            # painter.drawText(self.boundingRect(), self._text, self.painterTextOption)
            painter.drawText(self.painterTextRect, self._text, self.painterTextOption)
            painter.restore()
            # painter.setWorldMatrixEnabled(True)

        if option.state & QStyle.State_Selected or self.cosmeticSelect:

            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
            else:
                selectionPenBottom = self.selectionPenBottom

            painter.setBrush(Qt.NoBrush)

            painter.setPen(selectionPenBottom)
            painter.drawLine(self._line)

            ########################################################################
            # !!! simdilik iptal, gorsel fazlalik olusturmakta !!!
            ########################################################################
            if not self.isPinned and self.isActiveItem:
                # painter.setPen(self.handlePen)
                painter.drawEllipse(self.p1Handle)
                painter.drawEllipse(self.p2Handle)
            ########################################################################

            # painter.setPen(self.selectionPenTop)
            # painter.drawLine(self._line)

            # if self.editMode:
            #     # for a future release, draw points
            #     path = self.path()
            #     painter.setPen(QPen(self.cizgiRengi, 10))
            #     for i in range(path.elementCount()):
            #         painter.drawPoint(QPointF(path.elementAt(i).x, path.elementAt(i).y))

        # # # # # # # debug start - pos() # # # # #
        # painter.setBrush(Qt.NoBrush)
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self.boundingRect(), "{},  {}\n{},  {}".format(p.x(),p.y(),s.x(), s.y()))
        # painter.setPen(QPen(Qt.green,12))
        # painter.drawPoint(self.mapFromScene(self.sceneBoundingRect().center()))
        # # # # painter.drawRect(self.boundingRect())
        # painter.setPen(Qt.green)
        # painter.drawRect(self.boundingRect())
        # painter.drawRect(self.painterTextRect)
        # painter.setPen(Qt.yellow)
        # # painter.drawPolygon(self.rpoly)
        # painter.drawRect(p.x(),p.y(),100,100)
        # painter.setPen(Qt.red)
        # painter.drawRect(s.x(),s.y(),100,100)
        # # painter.drawRect(0,0,15,15)
        # # painter.drawRect(self.path().controlPointRect())
        # painter.setPen(Qt.blue)
        # painter.drawRect(self.boundingRect())
        # # # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):

        rect = self.sceneBoundingRect()
        xr = rect.left()
        yr = rect.top()
        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = xr - xs
        y = yr - ys

        w = rect.width()
        h = rect.height()

        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)

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
        painter.save()

        diff = self.scenePos() - rect.center()
        cizilecekLine = QLineF(self._line)
        cizilecekTextRect = QRectF(self.painterTextRect)
        cizilecekOkPolygon = QPolygonF(self.ok_polygon)

        cizilecekLine.translate(diff)
        cizilecekOkPolygon.translate(diff)
        painter.setPen(self._pen)

        painter.translate(diff)
        painter.rotate(self.rotation())
        painter.translate(-diff)
        painter.drawLine(cizilecekLine)
        painter.setBrush(self._pen.color())
        painter.setPen(Qt.NoPen)
        painter.drawConvexPolygon(cizilecekOkPolygon)
        # painter.drawRect(cizilecekTextRect)
        # painter.drawText(cizilecekTextRect, self._text, self.painterTextOption)
        painter.restore()
        if self._text:
            painter.save()
            painter.setFont(self._font)
            # painter.setPen(self.textPen)
            painter.setPen(self.yaziRengi)
            diff = (-cizilecekLine.p1())

            cizilecekTextRect.moveBottomLeft(cizilecekLine.p1())

            painter.translate(-diff)
            painter.rotate((self.rotation() - self._line.angle()) % 360)
            painter.translate(diff)
            painter.scale(self.painterTextScale, self.painterTextScale)
            # painter.drawText(cizilecekLine.p1(), self._text)
            painter.drawText(cizilecekTextRect, self._text, self.painterTextOption)

            painter.restore()
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
