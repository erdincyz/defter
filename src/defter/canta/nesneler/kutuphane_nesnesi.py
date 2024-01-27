# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '28/Oct/2018'
__author__ = 'Erdinç Yılmaz'
__license__ = 'GPLv3'

import os
from PySide6.QtGui import (QPen, QBrush, QPainterPath, QPainterPathStroker, QColor, QTextOption, QPixmap, QFont, QDrag)
from PySide6.QtWidgets import (QGraphicsItem, QStyle, QGraphicsPixmapItem, QFileIconProvider)
from PySide6.QtCore import (QRectF, Qt, QMimeData, QUrl, QFileInfo, QSize)
from .. import shared


########################################################################
class KutuphaneNesnesi(QGraphicsItem):
    Type = shared.KUTUPHANE_NESNESI

    def __init__(self, pos, tip, dosya_adresi, sahnede_kullaniliyor_mu=True,
                 belgede_kullaniliyor_mu=True,
                 isEmbeded=True,
                 isHtmlImage=False,
                 parent=None):
        super(KutuphaneNesnesi, self).__init__(parent)
        # QGraphicsItem.__init__(self, parent,scene)

        self.sahnede_kullaniliyor_mu = sahnede_kullaniliyor_mu
        self.belgede_kullaniliyor_mu = belgede_kullaniliyor_mu
        self.isEmbeded = isEmbeded
        self.isHtmlImage = isHtmlImage

        self.tip = tip

        self.dosya_adresi = dosya_adresi

        if os.path.isfile(dosya_adresi):
            self.filePathForDraw = dosya_adresi
        else:
            self.filePathForDraw = ':icons/warning.png'

        self._pixmap_olustur()

        rectf = QRectF(self.pixmap.rect())

        self.onizlemePixmapItem = None

        self.setPos(pos)
        self._rect = rectf
        self._boundingRect = QRectF()

        self.setAcceptHoverEvents(True)

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # self.setFlags(QGraphicsItem.ItemIsSelectable |
        #               # QGraphicsItem.ItemIsMovable |
        #               QGraphicsItem.ItemIsFocusable)

        # self.setFiltersChildEvents(True)
        # self.setHandlesChildEvents(True)

        self._pen = QPen()
        self._brush = QBrush()
        # TODO: fonta gerek var mi
        self._font = QFont()
        self._font.setBold(True)
        # self._font.setPointSize(12)
        # self._text = dosya_adresi

        self.painterTextOption = QTextOption()
        self.painterTextOption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.painterTextOption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        self.activeItemLineColor = shared.activeItemLineColor
        # self.cizgiRengi = pen.color()
        # self.setCizgiRengi(self.cizgiRengi)  # also sets self._pen
        self.setCizgiRengi(QColor(Qt.GlobalColor.red))
        # self.yaziRengi = yaziRengi
        # self.setYaziRengi(yaziRengi)
        self.setYaziRengi(QColor(Qt.GlobalColor.black))
        self.setArkaPlanRengi(QColor(Qt.GlobalColor.transparent))  # also sets self._brush # veya nobrush

        self.setToolTip(f'{dosya_adresi}\n\n -- Press "Alt" to preview"')

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return KutuphaneNesnesi.Type

        # ---------------------------------------------------------------------
    def _pixmap_olustur(self):

        if self.tip == shared.VIDEO_ITEM_TYPE or self.tip == shared.DOSYA_ITEM_TYPE:
            iconProvider = QFileIconProvider()
            self.ikon = iconProvider.icon(QFileInfo(self.dosya_adresi))
            # self.pixmap = self.ikon.pixmap(self._rect.toRect().size())
            self.pixmap = self.ikon.pixmap(QSize(45, 45))
        else:
            self.pixmap = QPixmap(self.filePathForDraw).scaledToWidth(45, Qt.TransformationMode.FastTransformation)


    # # ---------------------------------------------------------------------
    # def _pixmap_olustur_eski(self):
    #
    #
    #     # # self.pixmap = pixmap
    #     # self.pixmap = QPixmap()
    #     # if not QPixmapCache.find(self.filePathForDraw, self.pixmap):
    #     #     self.pixmap = QPixmap(self.filePathForDraw)
    #     #     QPixmapCache.insert(self.filePathForDraw, self.pixmap)
    #     #
    #     # # self.pixmap = QPixmap(self.filePathForDraw)
    #
    #     # self.pixmap = pixmap
    #     # self.pixmap = QPixmap()
    #     # print(QPixmapCache.cacheLimit())
    #     # self.pixmap = QPixmapCache.find(self.filePathForDraw, self.pixmap)
    #     self.pixmap = QPixmapCache.find(self.filePathForDraw)
    #     if not self.pixmap:
    #         # print("asdasd")
    #         # viewRectSize = self.scene().views()[0].get_visible_rect().size().toSize()
    #         # self.pixMap = QPixmap(self.filePathForDraw).scaled(viewRectSize / 1.5, Qt.KeepAspectRatio)
    #         if self.tip == shared.VIDEO_ITEM_TYPE or self.tip == shared.DOSYA_ITEM_TYPE:
    #             iconProvider = QFileIconProvider()
    #             self.ikon = iconProvider.icon(QFileInfo(dosya_adresi))
    #             # self.pixmap = self.ikon.pixmap(self._rect.toRect().size())
    #             self.pixmap = self.ikon.pixmap(QSize(45, 45))
    #         else:
    #             self.pixmap = QPixmap(self.filePathForDraw).scaledToWidth(45, Qt.TransformationMode.FastTransformation)
    #         QPixmapCache.insert(self.filePathForDraw, self.pixmap)
    #     else:
    #         self.pixmap = self.pixmap.scaledToWidth(45, Qt.TransformationMode.FastTransformation)

    # ---------------------------------------------------------------------
    def _onizleme_pixmap_olustur(self):
        # viewRectSize = self.scene().views()[0].get_visible_rect().size().toSize()
        # self.pixMap = QPixmap(self.filePathForDraw).scaled(viewRectSize / 1.5, Qt.KeepAspectRatio)
        self.onizlemePixmap = QPixmap(self.filePathForDraw).scaledToWidth(300, Qt.TransformationMode.FastTransformation)

        self.onizlemePixmapItem = QGraphicsPixmapItem(self.onizlemePixmap, self)

    # # ---------------------------------------------------------------------
    # def _onizleme_pixmap_olustur_eski(self):
    #     self.onizlemePixmap = QPixmapCache.find(self.dosya_adresi)
    #     if not self.onizlemePixmap:
    #         # print("asdasd")
    #         # viewRectSize = self.scene().views()[0].get_visible_rect().size().toSize()
    #         # self.pixMap = QPixmap(self.filePathForDraw).scaled(viewRectSize / 1.5, Qt.KeepAspectRatio)
    #         self.onizlemePixmap = QPixmap(self.filePathForDraw).scaledToWidth(300, Qt.TransformationMode.FastTransformation)
    #         QPixmapCache.insert(self.dosya_adresi, self.onizlemePixmap)
    #     else:
    #         self.onizlemePixmap = self.onizlemePixmap.scaledToWidth(300, Qt.TransformationMode.FastTransformation)
    #
    #     self.onizlemePixmapItem = QGraphicsPixmapItem(self.onizlemePixmap, self)

    # ---------------------------------------------------------------------
    def sceneCenter(self):
        return self.mapToScene(self._rect.center())

    # ---------------------------------------------------------------------
    def sceneWidth(self):
        return self.sceneRight() - self.sceneLeft()

    # ---------------------------------------------------------------------
    def sceneHeight(self):
        return self.sceneBottom() - self.sceneTop()

    # ---------------------------------------------------------------------
    def sceneRight(self):
        return max(self.mapToScene(self._rect.topLeft()).x(),
                   self.mapToScene(self._rect.topRight()).x(),
                   self.mapToScene(self._rect.bottomRight()).x(),
                   self.mapToScene(self._rect.bottomLeft()).x())

    # ---------------------------------------------------------------------
    def sceneLeft(self):
        return min(self.mapToScene(self._rect.topLeft()).x(),
                   self.mapToScene(self._rect.topRight()).x(),
                   self.mapToScene(self._rect.bottomRight()).x(),
                   self.mapToScene(self._rect.bottomLeft()).x())

    # ---------------------------------------------------------------------
    def sceneTop(self):
        return min(self.mapToScene(self._rect.topLeft()).y(),
                   self.mapToScene(self._rect.topRight()).y(),
                   self.mapToScene(self._rect.bottomRight()).y(),
                   self.mapToScene(self._rect.bottomLeft()).y())

    # ---------------------------------------------------------------------
    def sceneBottom(self):
        return max(self.mapToScene(self._rect.topLeft()).y(),
                   self.mapToScene(self._rect.topRight()).y(),
                   self.mapToScene(self._rect.bottomRight()).y(),
                   self.mapToScene(self._rect.bottomLeft()).y())

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
    def boundingRect(self):
        # TODO: kare gruplandiginda bu padding belli oluyor.
        # cunku self.rect ile paint ediyoruz. ellipsete yok bu problem.
        # pad = self.pen().widthF() / 2 + self.handleSize
        pad = self.pen().widthF() / 2
        self._boundingRect = QRectF(self._rect)
        return self._boundingRect.adjusted(-pad, -pad, pad, pad)

        # path = QPainterPath()
        # path.addRect(self._rect)
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

    # # ---------------------------------------------------------------------
    # def setText(self, text):
    #     self._text = text
    #     self.update()
    #
    # # ---------------------------------------------------------------------
    # def text(self):
    #     return self._text

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
        # self.scene().parent().on_item_context_menu_about_to_show(self)
        # self.scene().parent().itemContextMenu.popup(event.screenPos())
        self.scene().parent().kutuphaneNesneSagMenu.popup(event.screenPos())
        event.accept()

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        """sahneden nesneleri secebilir"""

        super(KutuphaneNesnesi, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def setCizgiRengi(self, col):

        # _selectionLineBgColor = QColor.fromHsv(col.hue(),
        #                                        0,
        #                                        20 if col.value() > 127 else 250)

        _activeItemLineColor = QColor(self.activeItemLineColor)
        if col.hue() > 300 or col.hue() < 30:
            _activeItemLineColor.setHsv((col.hue() + 150) % 360,
                                        self.activeItemLineColor.saturation(),
                                        self.activeItemLineColor.value())

        self._pen.setColor(col)
        self.cizgiRengi = col

        # self.selectionPenBottom = QPen(_selectionLineBgColor,
        #                                self._pen.width(),
        #                                Qt.DashLine,
        #                                Qt.FlatCap, Qt.RoundJoin)

        self.selectionPenBottom = QPen(_activeItemLineColor,
                                       self._pen.width(),
                                       Qt.PenStyle.DashLine,
                                       Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.RoundJoin)

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
    def setArkaPlanRengi(self, col):
        self.arkaPlanRengi = col
        self.setBrush(QBrush(col))

    # ---------------------------------------------------------------------
    def hoverMoveEvent(self, event):
        # event propagationdan dolayi bos da olsa burda implement etmek lazim
        # mousePress,release,move,doubleclick de bu mantıkta...
        # baska yerden baslayip mousepress ile , mousemove baska, mouseReleas baska widgetta gibi
        # icinden cikilmaz durumlara sebep olabiliyor.
        # ayrica override edince accept() de edilmis oluyor mouseeventler
        super(KutuphaneNesnesi, self).hoverMoveEvent(event)

    # ---------------------------------------------------------------------
    def hoverEnterEvent(self, QGraphicsSceneHoverEvent):
        # TODO: bu daha optimize edilebilir hatta iimage ve bunun normal pixmapleri de
        # scale kısmı verimli degil gibi
        # scale edilmişi de mi cache atıyoruz.
        # else kısmında ve de.

        if QGraphicsSceneHoverEvent.modifiers() == Qt.KeyboardModifier.AltModifier:

            # self.pixmap = QPixmap()
            # print(QPixmapCache.cacheLimit())
            # self.pixmap = QPixmapCache.find(self.filePathForDraw, self.pixmap)
            if not self.onizlemePixmapItem:
                self._onizleme_pixmap_olustur()
            else:
                self.onizlemePixmapItem.setVisible(True)

            self.scene().zDeger_arttir(self)
        super(KutuphaneNesnesi, self).hoverEnterEvent(QGraphicsSceneHoverEvent)

    # ---------------------------------------------------------------------
    def hoverLeaveEvent(self, QGraphicsSceneHoverEvent):
        if self.onizlemePixmapItem:
            self.onizlemePixmapItem.setVisible(False)
        super(KutuphaneNesnesi, self).hoverLeaveEvent(QGraphicsSceneHoverEvent)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, e):
        # if e.buttons() != Qt.RightButton:
        #     return

        # write the relative cursor position to mime data
        mimeData = QMimeData()
        # simple string with 'x,y'
        # mimeData.setText('%d,%d' % (e.x(), e.y()))
        mimeData.setUrls((QUrl.fromLocalFile(self.dosya_adresi),))

        # # below makes the pixmap half transparent
        # painter = QPainter(pixmap)
        # painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        # painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
        # painter.end()

        # make a QDrag
        drag = QDrag(e.widget())
        # put our MimeData
        drag.setMimeData(mimeData)
        # set its Pixmap
        drag.setPixmap(self.pixmap)
        # shift the Pixmap so that it coincides with the cursor position
        drag.setHotSpot(e.pos().toPoint())

        # start the drag operation
        # exec_ will return the accepted action from dropEvent
        if drag.exec_(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction) == Qt.DropAction.MoveAction:
            print('moved')
            self.sahnede_kullaniliyor_mu = True
            self.belgede_kullaniliyor_mu = True
            self.update()
        else:
            print('copied')

        self.setCursor(Qt.CursorShape.OpenHandCursor)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        # QGraphicsItem.mousePressEvent(self, e)
        # if e.button() == Qt.LeftButton:
        #     print('press')

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):

        painter.setClipRect(option.exposedRect)

        painter.setFont(self._font)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # rect = self.boundingRect().toRect()
        rect = self._rect.toRect()
        painter.drawPixmap(rect, self.pixmap)

        # # painter.setWorldMatrixEnabled(False)
        # painter.save()
        # metrics = painter.fontMetrics()
        # # --- basla -- elided text icin-------------------------------------------------------------
        # # txt = metrics.elidedText(self._text, Qt.ElideRight, self._rect.width() / scale)
        # # r = QRectF(metrics.boundingRect(txt))
        # # --- bitir -- elided text icin-------------------------------------------------------------
        #
        # r = QRectF(metrics.boundingRect(self._rect.toRect(), Qt.TextWrapAnywhere, self._text))
        # r.moveCenter(self._rect.center())
        # # draw text background rect
        # painter.setPen(Qt.NoPen)
        # painter.setBrush(self.arkaPlanRengi)
        #
        # painter.drawRect(r.intersected(self._rect))
        # # draw text
        # # painter.setPen(self._pen)
        # painter.setPen(self.yaziRengi)
        # # painter.drawText(self._rect, Qt.AlignCenter, txt)
        # painter.drawText(self._rect, self._text, self.painterTextOption)
        # # painter.drawText(self.painterTextRect, self._text, self.painterTextOption)
        #
        # painter.restore()
        # # painter.setWorldMatrixEnabled(True)

        if option.state & QStyle.StateFlag.State_Selected:
            selectionPenBottom = self.selectionPenBottom

            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.setPen(selectionPenBottom)
            painter.drawRect(self._rect)

            # painter.setPen(self.selectionPenTop)
            # painter.drawRect(self._rect)

        if self.isHtmlImage:
            painter.setBrush(Qt.GlobalColor.cyan)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawEllipse(QRectF(0, 0, 16, 15))
            painter.drawText(QRectF(3, 0, 16, 15), "w")
            return

        if not self.isEmbeded:
            painter.setBrush(Qt.GlobalColor.yellow)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawEllipse(QRectF(0, 0, 15, 15))
            painter.drawText(QRectF(3, 0, 15, 15), "~")
            return

        if not self.belgede_kullaniliyor_mu:
            painter.setBrush(Qt.GlobalColor.red)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawEllipse(QRectF(0, 0, 15, 15))
            painter.drawText(QRectF(3, 0, 15, 15), "X")
            # painter.drawEllipse(QRectF(0,0,10,10))
            return

        if not self.sahnede_kullaniliyor_mu:
            painter.setBrush(Qt.GlobalColor.darkYellow)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawEllipse(QRectF(0, 0, 15, 15))
            painter.drawText(QRectF(3, 0, 15, 15), "X")
            # painter.drawEllipse(QRectF(0,0,10,10))
            return
