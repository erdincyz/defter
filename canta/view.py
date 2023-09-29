# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/27/16'

import os
from PySide6.QtGui import QPainter, QPixmap, QPen
from PySide6.QtWidgets import QGraphicsView, QApplication
from PySide6.QtCore import Qt, QRectF, Slot


########################################################################
class View(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(View, self).__init__(scene, parent)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        # self.setRenderHint(QPainter.Antialiasing)
        # self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        # self.setDragMode(QGraphicsView.RubberBandDrag)  # secmek icin meseala box selection
        # self.setRubberBandSelectionMode(Qt.ItemSelectionModelaraBak)

        # TODO !!
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        # self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        # self.setViewportUpdateMode(self.MinimalViewportUpdate)  # default
        # self.setViewportUpdateMode(self.BoundingRectViewportUpdate)
        # self.setViewportUpdateMode(self.FullViewportUpdate)

        # self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.panStartPos = None

        # self.background = QPixmap('/pictures/rig.jpg')
        # self.backgroundImage = None

        self.setBackgroundBrush(Qt.GlobalColor.lightGray)
        self.backgroundImagePixmap = None
        self.backgroundImagePath = None
        self.backgroundImagePathIsEmbeded = False
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.baski_cerceve_kalemi = QPen(Qt.GlobalColor.black)
        self.baskiRectler = []

        # self.debug_rect=QRectF()

    # def scrollContentsBy(self, p_int, p_int_1):
    #     pass

    # def resizeEvent(self, QResizeEvent):
    #
    #     self.setSceneRect(self.get_visible_rect())
    #
    #     super(View, self).resizeEvent(QResizeEvent)

    # ---------------------------------------------------------------------
    def baski_cerceve_rengi_kur(self, renk):
        self.baski_cerceve_kalemi = QPen(renk,
                                         0,
                                         Qt.PenStyle.DashLine,
                                         Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

    # ---------------------------------------------------------------------
    def setDragModeRubberBandDrag(self):
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    # ---------------------------------------------------------------------
    def setDragModeNoDrag(self):
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

    # ---------------------------------------------------------------------
    def contextMenuEvent(self, event):

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.scene().parent().nesne_ozellikleriYW_goster_gizle()
            return

        if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            self.scene().parent().stil_uygulaYW_goster_gizle()
            return

        QGraphicsView.contextMenuEvent(self, event)
        # mouse altinda bir nesne varsa ve sag click menusunu gosterdiyse event.accepted() doner.
        if not event.isAccepted():
            self.scene().parent().view_sag_menu_goster(event.globalPos())
            # TODO: gerek var mi?
            # event.accept()

    # ---------------------------------------------------------------------
    def get_visible_rect(self):
        """used for mirror line pos"""
        r = self.mapToScene(self.viewport().rect()).boundingRect()
        # r = self.mapToScene(self.rect()).boundingRect()
        r.adjust(1, 1, -1, -1)
        return r
        # return

    # # ---------------------------------------------------------------------
    # def get_scroll_bar_positions(self):
    #     return self.horizontalScrollBar().value(),self.verticalScrollBar().value()
    #
    # # ---------------------------------------------------------------------
    # def set_scroll_bar_positions(self, horizontal, vertical):
    #     self.horizontalScrollBar().setValue(horizontal)
    #     self.verticalScrollBar().setValue(vertical)

    # ---------------------------------------------------------------------
    def drawBackground(self, painter, rectf):
        painter.setBrushOrigin(0, 0)
        painter.fillRect(rectf, self.backgroundBrush())

        # ---  pos debug start   ---
        # painter.drawRect(self.sceneRect())
        # painter.drawRect(self.kopyaRekt)
        #
        # painter.drawEllipse(rectf.center().x(),rectf.center().y(),10,10)
        # #painter.setPen(QPen(Qt.blue))
        # #painter.drawRect(self.get_visible_rect())
        # painter.setPen(QPen(Qt.green))
        # painter.drawRect(self.scene().itemsBoundingRect())
        # painter.setPen(QPen(Qt.red))
        # painter.drawRect(QRectF(0,0,20,20))
        # painter.drawRect(self.sceneRect())
        # painter.setPen(QPen(Qt.yellow))
        # painter.drawRect(QRectF(0, 0, 20, 20))
        # painter.drawRect(QRectF(100, 0, 20, 20))
        # painter.drawRect(QRectF(200, 0, 20, 20))
        # painter.drawRect(QRectF(300, 0, 20, 20))
        # painter.drawRect(QRectF(400, 0, 20, 20))
        # painter.drawRect(QRectF(0, 100, 20, 20))
        # painter.drawRect(QRectF(0, 200, 20, 20))
        # painter.drawRect(QRectF(0, 300, 20, 20))
        # painter.drawRect(QRectF(0, 400, 20, 20))
        # painter.drawRect(self.kagitPozisyonBoyutRect)
        # painter.drawRect(self.debug_rect)
        # ---  pos debug end   ---

        if self.backgroundImagePixmap:
            # painter.drawPixmap(rectf.toRect(), self.backgroundImagePixmap)
            painter.drawPixmap(0, 0, self.backgroundImagePixmap)

        # painter.drawRect(QRectF(self.sceneRect().x(), self.sceneRect().y(), 10, 10))

        for rect in self.baskiRectler:
            painter.setPen(self.baski_cerceve_kalemi)
            painter.drawRect(rect)

    # ---------------------------------------------------------------------
    def set_background_image(self, imagePath):

        if not imagePath:
            self.backgroundImagePixmap = None
            self.backgroundImagePath = None
        else:
            # TODO: belki: ekelenen imajin ortalama rengine cevir scene bgcolor
            if not os.path.isfile(imagePath):
                imagePath = ':/icons/warning.png'
            self.backgroundImagePixmap = QPixmap(imagePath)
            # view's setSceneRect is not scene's setSceneRect, they are different.
            # self.setSceneRect(QRectF(self.backgroundImagePixmap.rect()))
            self.setSceneRect(QRectF(self.backgroundImagePixmap.rect()))
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.backgroundImagePath = imagePath
        self.resetCachedContent()

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):
        # self.scene().keyPressEvent(event)  # viewi bypass edip sahneye gonderiyoruz, ok tuslarini yiyor view

        key = event.key()
        # print(event.key())
        # print((Qt.Key_PageUp, Qt.Key_PageDown))

        # ---------------------------------------------------------------------
        # Bunu iptal ettik space basinca sahne hareket ettirmek icindi, keyreleasede de var devamı
        # ---------------------------------------------------------------------
        # if key == Qt.Key_Space:
        #     devam = False
        #     if self.scene().activeItem:
        #         if self.scene().activeItem.type() == shared.TEXT_ITEM_TYPE:
        #             if not self.scene().activeItem.hasFocus():
        #                 devam = True
        #         elif self.scene().activeItem.type() == shared.GROUP_ITEM_TYPE:
        #             # devam = False
        #             pass
        #         else:
        #             if not self.scene().activeItem.tempTextItem:
        #                 devam = True
        #     if devam:
        #         if not event.isAutoRepeat():
        #             if self.horizontalScrollBar().isVisible() or self.verticalScrollBar().isVisible():
        #                 self.setDragMode(QGraphicsView.ScrollHandDrag)
        #                 # bu interactive olmazsa mouse altında nesne olunca event nesneye geciyor.
        #                 self.setInteractive(False)
        #                 # self.bosluk_tusu_basildi_mi = True
        #                 # self.setCursor(Qt.ClosedHandCursor)
        #                 event.accept()
        # ---------------------------------------------------------------------

        # sahneye gitmeden once view' in abstractScrollAreasindaki
        # scrollbarlarin sliderSingleStepAdd aksiyonuna gidiyor. bu da nesne secili iken,
        #  ekranın scroll etmesine sebep oluyor
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Right, Qt.Key.Key_Left):
            if self.scene().activeItem:
                self.horizontalScrollBar().setSingleStep(0)
                self.verticalScrollBar().setSingleStep(0)
                # if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                #     self.horizontalScrollBar().setPageStep(0)
                #     self.verticalScrollBar().setPageStep(0)
                # else:
                #     self.horizontalScrollBar().setSingleStep(0)
                #     self.verticalScrollBar().setSingleStep(0)

        # print(self.viewportEvent())/

        if key == Qt.Key.Key_Home:
            self.verticalScrollBar().setValue(self.verticalScrollBar().minimum())

        if key == Qt.Key.Key_End:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

        if key == Qt.Key.Key_PageUp:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - self.viewport().rect().height() + 10)

        if key == Qt.Key.Key_PageDown:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + self.viewport().rect().height() - 10)

        super(View, self).keyPressEvent(event)

    # ---------------------------------------------------------------------
    def keyReleaseEvent(self, event):
        key = event.key()
        # ---------------------------------------------------------------------
        # Bunu iptal ettik space basinca sahne hareket ettirmek icindi, keypressde de var oncesi
        # ---------------------------------------------------------------------
        # if key == Qt.Key.Key_Space:
        #     if self.dragMode() == QGraphicsView.ScrollHandDrag:
        #         if not event.isAutoRepeat():
        #             self.setDragMode(QGraphicsView.RubberBandDrag)
        #             # bu interactive olmazsa mouse altında nesne olunca event nesneye geciyor.
        #             self.setInteractive(True)
        #             # self.bosluk_tusu_basildi_mi = False
        #             # self.setCursor(Qt.ArrowCursor)
        #             event.accept()
        # ---------------------------------------------------------------------

        super(View, self).keyPressEvent(event)

        # bunların superden sonra gelmesi lazim.
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Right, Qt.Key.Key_Left):
            # bir tusu birakmadan diger tusa basinca ve digerini birtakinca kaymalar oluyor o yuzden
            # secili nesne kontrolu
            if not self.scene().activeItem:
                self.horizontalScrollBar().setSingleStep(self.viewport().size().width() / 20)  # orjinal 1
                self.verticalScrollBar().setSingleStep(self.viewport().size().height() / 20)  # orjinal 1

            # self.horizontalScrollBar().setPageStep(self.viewport().size().width())
            # self.verticalScrollBar().setPageStep(self.viewport().size().height())

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.MiddleButton:
            # if not self.scene().selectedItems():
            # if not self.itemAt(event.pos()):
            self.panStartPos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            # nesne uzerine orta tıklayıp sahne hareket ettirisek,
            # orta tusu birakinca ic nesneleri seciyor ve secili birakiyor, o yuzden burda return kullandik
            # mouseReleaseEvent te de kullanabilirdik.
            return

        super(View, self).mousePressEvent(event)
        # return QGraphicsView.mousePressEvent(self, event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.panStartPos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setSceneRect(self.sceneRect().united(self.scene().itemsBoundingRect()))

            event.accept()
            # ! bunu mousePressEvent e tasidik.
            # nesne uzerine orta tıklayıp sahne hareket ettirisek,
            # orta tusu birakinca ic nesneleri seciyor ve secili birakiyor, o yuzden return
            # return

        super(View, self).mouseReleaseEvent(event)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        if self.panStartPos:
            # normal gezinme , sahne boyutlarini degistirmez. scroll bar sonlari sinirdir.
            # alt kisim eklenince, islevi biraz degisti, bu olmazsa sadece alt kisim varsa ve sahnede scrollbar varsa
            # sahnede gezinirken scrollbarlar bitene kadar sahne sabit kaliyor sonra gezinme basliyor.
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - (event.x() - self.panStartPos.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self.panStartPos.y()))

            # bu sonradan eklendi ve de bununla beraber,
            # mouse release eklendi- > self.setSceneRect(self.sceneRect().united(self.scene().itemsBoundingRect()))
            transform = self.transform()
            deltaX = (self.panStartPos.x() - event.x()) / transform.m11()
            deltaY = (self.panStartPos.y() - event.y()) / transform.m22()
            self.setSceneRect(self.sceneRect().translated(deltaX, deltaY))

            self.panStartPos = event.pos()

            event.accept()

        super(View, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):
        # factor = 1.41 ** (event.delta() / 240.0)
        # self.scale(factor, factor)

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # alt 2 satir olmazsa ctrl+shift nesnelere gecmiyor.
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                return QGraphicsView.wheelEvent(self, event)

            # alt 2 satir olmazsa ctrl+alt nesnelere gecmiyor.
            if event.modifiers() == Qt.KeyboardModifier.AltModifier:
                return QGraphicsView.wheelEvent(self, event)

            if event.angleDelta().y() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
            # return ediyoruz ki normal view ctrl hizli scroll iptal olsun
            return
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            #     # self.scene().tekerlek_ile_firca_boyu_degistir(event.angleDelta().y())
            #     # print(event.isAccepted())
            #     # if (event.isAccepted()):
            #     #     return
            #     # alt satir olmazsa shift nesnelere gecmiyor.

            # if not self.scene().activeItem:
            if self.itemAt(event.position().toPoint()):
                return QGraphicsView.wheelEvent(self, event)
        else:
            super(View, self).wheelEvent(event)
        # superi cagirmayalim cunku scrool bar move ediyor normalde wheel

    # # ---------------------------------------------------------------------
    # def wheelEvent_nesne_varsa_nesne_scale_eden(self, event):
    #     # factor = 1.41 ** (event.delta() / 240.0)
    #     # self.scale(factor, factor)
    #
    #     if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
    #         # alt satir olmazsa ctrl basili iken event nesnelere gecmiyor.
    #         if self.items(event.pos()):
    #             # for item in self.items(event.pos()):
    #             #     if item.isSelected
    #             # alt satir olmazsa ctrl basili iken event nesnelere gecmiyor.
    #             return QGraphicsView.wheelEvent(self, event)
    #         else:
    #
    #             # if event.delta() > 0:
    #             if event.angleDelta().y() > 0:
    #                 self.zoomIn()
    #             else:
    #                 self.zoomOut()
    #     else:
    #         super(View, self).wheelEvent(event)
    #     # superi cagirmayalim cunku scrool bar move ediyor normalde wheel

    # ---------------------------------------------------------------------
    @Slot(int)
    def set_scale(self, scale):
        """
            we set this from status bar spinbox
        """
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        scale = scale / 100 * (1 / self.transform().m11())
        # self.scene().parent().zoomSBox.setValue(scale*100)
        self.scale(scale, scale)
        if self.scene().selectedItems():
            self.scene().activeItem.update_resize_handles()

        QApplication.restoreOverrideCursor()

    # ---------------------------------------------------------------------
    @Slot()
    def zoomIn(self):
        if self.scene().parent().zoomSBox.value() < 10000:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.scale(1.15, 1.15)
            # ir = self.scene().itemsBoundingRect()
            # vr = self.get_visible_rect()
            # if vr.width() * vr.height() > ir.width() * ir.height():
            #     self.setSceneRect(self.get_visible_rect())
            # else:
            #     self.setSceneRect(ir)
            if self.scene().selectedItems():
                self.scene().activeItem.update_resize_handles()

            self.scene().parent().zoomSBox.setValue(self.transform().m11() * 100)

            QApplication.restoreOverrideCursor()

    # ---------------------------------------------------------------------
    @Slot()
    def zoomOut(self):
        if self.scene().parent().zoomSBox.value() > 1:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.scale(1 / 1.15, 1 / 1.15)
            sr = self.scene().sceneRect()
            vr = self.get_visible_rect()
            if vr.width() * vr.height() > sr.width() * sr.height():
                self.setSceneRect(self.get_visible_rect())

            if self.scene().selectedItems():
                self.scene().activeItem.update_resize_handles()

            self.scene().parent().zoomSBox.setValue(self.transform().m11() * 100)
            QApplication.restoreOverrideCursor()

    # ---------------------------------------------------------------------
    @Slot()
    def zoomToFit(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        # make sure the sceneRect is only as large as it needs to be, since
        # it does not automatically shrink
        if self.scene().items():
            self.setSceneRect(self.scene().itemsBoundingRect())
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            # self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        # self.setSceneRect(self.get_visible_rect())

        if self.scene().selectedItems():
            self.scene().activeItem.update_resize_handles()

        self.scene().parent().zoomSBox.setValue(self.transform().m11() * 100)
        QApplication.restoreOverrideCursor()

    # ---------------------------------------------------------------------
    @Slot()
    def zoomToSelection(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        if self.scene().selectionQueue:
            yeniRect = QRectF()
            for item in self.scene().selectionQueue:
                # if item.isVisible():
                if not item.parentItem():
                    yeniRect = yeniRect.united(item.boundingRect().translated(item.pos()))
                else:
                    # parent edilmis nesnelerin pos degerleri parenta gore
                    # bunlari sahneye goreye cevirmek lazim
                    itemPosMappedFromParent = item.mapFromParent(item.pos())
                    itemScenePos = item.mapToScene(itemPosMappedFromParent)
                    yeniRect = yeniRect.united(item.boundingRect().translated(itemScenePos))

            self.setSceneRect(yeniRect)
            self.debug_rect = yeniRect
            # self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
            self.fitInView(yeniRect, Qt.AspectRatioMode.KeepAspectRatio)
            # self.setSceneRect(self.get_visible_rect())
            # self.centerOn(0, 0)

            # if self.scene().selectedItems():
            self.scene().activeItem.update_resize_handles()

            self.scene().parent().zoomSBox.setValue(self.transform().m11() * 100)
        QApplication.restoreOverrideCursor()

    # ---------------------------------------------------------------------
    @Slot()
    def zoomInitial(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.resetTransform()
        # sr = self.scene().sceneRect()
        ir = self.scene().itemsBoundingRect()
        vr = self.get_visible_rect()
        if vr.width() * vr.height() > ir.width() * ir.height():
            self.setSceneRect(self.get_visible_rect())
        else:
            self.setSceneRect(ir)

        if self.scene().selectedItems():
            self.scene().activeItem.update_resize_handles()

        self.scene().parent().zoomSBox.setValue(self.transform().m11() * 100)
        QApplication.restoreOverrideCursor()
