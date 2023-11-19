# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '25/Oct/2018'
__author__ = 'Erdinç Yılmaz'
__license__ = 'GPLv3'

import os
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsView, QApplication
from PySide6.QtCore import Qt, QRectF, Slot


########################################################################
class EkranKutuphane(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(EkranKutuphane, self).__init__(scene, parent)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        # self.setRenderHint(QPainter.Antialiasing)
        # self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        # self.setDragMode(QGraphicsView.RubberBandDrag)  # secmek icin meseala box selection
        # self.setRubberBandSelectionMode(Qt.ItemSelectionModelaraBak)

        # TODO !!
        # self.setViewportUpdateMode(self.SmartViewportUpdate)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate)  # default
        # https: // doc.qt.io / qt - 5 / qgraphicsview.html  # ViewportUpdateMode-enum
        # self.setViewportUpdateMode(self.BoundingRectViewportUpdate)
        # self.setViewportUpdateMode(self.FullViewportUpdate)

        # self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.panStartPos = None

        # self.background = QPixmap('/pictures/rig.jpg')
        # self.backgroundImage = None

        self.setBackgroundBrush(Qt.GlobalColor.lightGray)
        self.backgroundImagePixmap = None
        self.backgroundImagePath = None
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # gercek sahnede "if event.source().objectName() == "kev": " ile
        # kutuphanede drag drop edildi ise nesneyi embeded isaretleyebilmek icin.
        self.viewport().setObjectName("kev")

    # def scrollContentsBy(self, p_int, p_int_1):
    #     pass

    # # ---------------------------------------------------------------------
    # def resizeEvent(self, QResizeEvent):
    #
    #     # self.scene().setSceneRect(self.get_visible_rect())
    #     # self.scene().setSceneRect(self.get_visible_rect())
    #     vrect = self.viewport().rect()
    #     self.scene().setSceneRect(QRectF(0, 0, vrect.width(), vrect.height()))
    #
    #     super(EkranKutuphane, self).resizeEvent(QResizeEvent)

    # ---------------------------------------------------------------------
    def contextMenuEvent(self, event):
        QGraphicsView.contextMenuEvent(self, event)

        # if some item was under the mouse and showed its context menu, the event will
        # have been accepted
        if not event.isAccepted():
            self.scene().parent().ekran_kutuphane_sag_menu_goster(event.globalPos())
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

        # # ---  pos debug start   ---
        # painter.drawRect(self.sceneRect())
        # painter.drawRect(self.kopyaRekt)
        # painter.drawRect(QRectF(0,0,20,20))
        # painter.drawRect(rectf.center().x(),rectf.center().y(),10,10)
        # painter.setPen(QPen(Qt.blue))
        # painter.drawRect(self.get_visible_rect())
        # painter.setPen(QPen(Qt.red))
        # painter.drawRect(self.scene().sceneRect())
        # # ---  pos debug end   ---

        if self.backgroundImagePixmap:
            # painter.drawPixmap(rectf.toRect(), self.backgroundImagePixmap)
            painter.drawPixmap(0, 0, self.backgroundImagePixmap)

        # painter.drawRect(QRectF(self.sceneRect().x(), self.sceneRect().y(), 10, 10))

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
            self.scene().setSceneRect(QRectF(self.backgroundImagePixmap.rect()))
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.backgroundImagePath = imagePath
        self.resetCachedContent()

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):
        # self.scene().keyPressEvent(event)  # viewi bypass edip sahneye gonderiyoruz, ok tuslarini yiyor view
        if event.key() == Qt.Key.Key_Space:
            if not event.isAutoRepeat():
                if self.horizontalScrollBar().isVisible() or self.verticalScrollBar().isVisible():
                    self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                    # bu interactive olmazsa mouse altında nesne olunca event nesneye geciyor.
                    self.setInteractive(False)
                    # self.bosluk_tusu_basildi_mi = True
                    # self.setCursor(Qt.ClosedHandCursor)
                    event.accept()
        super(EkranKutuphane, self).keyPressEvent(event)

    # ---------------------------------------------------------------------
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            if not event.isAutoRepeat():
                if self.horizontalScrollBar():
                    self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                    # bu interactive olmazsa mouse altında nesne olunca event nesneye geciyor.
                    self.setInteractive(True)
                    # self.bosluk_tusu_basildi_mi = False
                    # self.setCursor(Qt.ArrowCursor)
                    event.accept()
        super(EkranKutuphane, self).keyPressEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.MiddleButton:
            # if not self.scene().selectedItems():
            # if not self.itemAt(event.pos()):
            self.panStartPos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super(EkranKutuphane, self).mousePressEvent(event)
        # return QGraphicsView.mousePressEvent(self, event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.panStartPos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setSceneRect(self.sceneRect().united(self.scene().itemsBoundingRect()))
            event.accept()

        super(EkranKutuphane, self).mouseReleaseEvent(event)

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

        super(EkranKutuphane, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):
        # factor = 1.41 ** (event.delta() / 240.0)
        # self.scale(factor, factor)

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # alt 2 satir olmazsa ctrl+shift nesnelere gecmiyor.
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                return QGraphicsView.wheelEvent(self, event)

            if event.angleDelta().y() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
        else:
            super(EkranKutuphane, self).wheelEvent(event)
        # superi cagirmayalim cunku scrool bar move ediyor normalde wheel

    # ---------------------------------------------------------------------
    def setDragModeRubberBandDrag(self):
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    # ---------------------------------------------------------------------
    def setDragModeNoDrag(self):
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

    # ---------------------------------------------------------------------
    @Slot()
    def zoomIn(self):
        if self.scene().parent().zoomSBox.value() < 10000:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.scale(1.15, 1.15)
            # ir = self.scene().itemsBoundingRect()
            # vr = self.get_visible_rect()
            # if vr.width() * vr.height() > ir.width() * ir.height():
            #     self.scene().setSceneRect(self.get_visible_rect())
            # else:
            #     self.scene().setSceneRect(ir)
            # if self.scene().selectedItems():
            #     self.scene().activeItem.update_resize_handles(force=True)

            # self.scene().parent().zoomSBox.setValue(self.transform().m11() * 100)

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
                self.scene().setSceneRect(self.get_visible_rect())

            # if self.scene().selectedItems():
            #     self.scene().activeItem.update_resize_handles(force=True)

            # self.scene().parent().zoomSBox.setValue(self.transform().m11() * 100)
            QApplication.restoreOverrideCursor()

    # ---------------------------------------------------------------------
    @Slot()
    def zoomToFit(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        # make sure the sceneRect is only as large as it needs to be, since
        # it does not automatically shrink
        if self.scene().items():
            self.scene().setSceneRect(self.scene().itemsBoundingRect())
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            # self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self.scene().setSceneRect(self.get_visible_rect())

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
            self.scene().setSceneRect(self.get_visible_rect())
        else:
            self.scene().setSceneRect(ir)

        # self.scene().parent().zoomSBox.setValue(self.transform().m11() * 100)
        QApplication.restoreOverrideCursor()
