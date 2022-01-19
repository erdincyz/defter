# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '04/Sep/2016'

import os

from PySide6.QtCore import Qt, QUrl, QSizeF, QRectF, QPointF, QPoint, QLine
from PySide6.QtGui import QPen, QPixmap, QPixmapCache, QPainterPath
from PySide6.QtWidgets import QStyle
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem

from canta import shared
from canta.nesneler.base import BaseItem


########################################################################
class GraphicsVideoItem(QGraphicsVideoItem):
    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(GraphicsVideoItem, self).__init__(parent)


########################################################################
class VideoItem(BaseItem):
    # @Slot() kullanmiyouz cunku qobjectten inherit etmiyor.
    # !! videoItem qgraphicsobjecten ediyor, yalniz bu baseItem ikisinden de etmiyor...

    Type = shared.VIDEO_ITEM_TYPE

    # ---------------------------------------------------------------------
    def __init__(self, filePath, pos, rect, yaziRengi, arkaPlanRengi, pen, font, isEmbeded=False, parent=None):
        # if rect.size() == QSizeF(1, 1):
        #     rect
        self.videoItem = GraphicsVideoItem()
        self.videoItem.setFlag(QGraphicsVideoItem.ItemStacksBehindParent)
        rect.setSize(self.videoItem.size())
        super(VideoItem, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)
        # QGraphicsVideoItem.__init__(parent)
        # super(VideoItem, self).__init__(parent)
        # BaseItem.__init__(pos, rect, arkaPlanRengi, pen, font, parent)

        # self.videoItem = QGraphicsVideoItem(self)
        # self.videoItem = GraphicsVideoItem(self)
        # self.videoItem.setFlag(QGraphicsVideoItem.ItemStacksBehindParent)

        self.video_hazir_mi = False

        self.videoItem.setParentItem(self)
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.videoItem)

        self.audioOutput = QAudioOutput()
        self.player.setAudioOutput(self.audioOutput)
        self.player.playbackStateChanged.connect(self.act_playback_state_changed)

        self.isEmbeded = isEmbeded
        self.filePathForSave = filePath
        if not isEmbeded:
            self.originalSourceFilePath = filePath

        # url = QUrl("http://")
        if os.path.exists(filePath):
            self.setText("Loading...")
            url = QUrl.fromLocalFile(filePath)
            # media = QMediaContent(url)
            # print(media.canonicalResource().audioCodec())
            # print(media.canonicalResource().videoCodec())
            # print(media.canonicalResource().audioBitRate())
            # print(media.canonicalResource().videoBitRate())
            # print(media.canonicalResource().channelCount())

            # self.player.setMedia(media)
            self.player.hasVideoChanged.connect(self.act_video_changed)
            self.player.setSource(url)
            # resolution = media.canonicalResource().resolution()

            self.videoItem.nativeSizeChanged.connect(self.act_native_size_changed)
            # self.videoItem.nativeSizeChanged.connect(self._rect.setSize)

            self.videoItem.setAspectRatioMode(Qt.KeepAspectRatio)

            # self.playControlsY = self._rect.bottom() - 50
            self.playControlsY = self.videoItem.size().height() / 2
            self.ikonBoyutu = 20
            # print(self.playControlsY)

            self.sliderLine = QLine(0,
                                    self.playControlsY,
                                    self.videoItem.size().width(),
                                    self.playControlsY)

            self.videoDuration = self.player.duration()
            self.player.positionChanged.connect(self.act_player_position_changed)

            self.videoSliderEllipseRect = QRectF(0, self.playControlsY,
                                                 self.ikonBoyutu,
                                                 self.ikonBoyutu)
            self.videoIkonMerkezNoktasi = QPointF(0, self.playControlsY)

            self.daire_ici_ikonlari_olustur()

            self.videoSliderEllipseFirstClickPos = QPointF()
            self.videoSliderEllipseStartDrag = False

            self.audioSliderEllipseRect = QRectF(self._rect.center().x(),
                                                 self.playControlsY,
                                                 self.ikonBoyutu,
                                                 self.ikonBoyutu)
            self.audioSliderEllipseStartDrag = False

            self.isVideoSliderHovered = False
            self.isAudioSliderHovered = False

        else:
            self.filePathForDraw = ':icons/warning.png'
            self.pixmap = QPixmap()
            # print(QPixmapCache.cacheLimit())
            # self.pixmap = QPixmapCache.find(self.filePathForDraw, self.pixmap)
            self.pixmap = QPixmapCache.find(self.filePathForDraw)
            if not self.pixmap:
                self.pixmap = QPixmap(self.filePathForDraw)
                QPixmapCache.insert(self.filePathForDraw, self.pixmap)

            # !!!! paint method override
            self.paint = self.paint_warning_image
            self.mousePressEvent = super(VideoItem, self).mousePressEvent
            self.mouseMoveEvent = super(VideoItem, self).mouseMoveEvent
            self.mouseReleaseEvent = super(VideoItem, self).mouseReleaseEvent
            self.hoverMoveEvent = super(VideoItem, self).hoverMoveEvent

    # ---------------------------------------------------------------------
    def daire_ici_ikonlari_olustur(self):

        olcekli_mesafe = self.ikonBoyutu / 4

        self.videoPlayIkonu = QPainterPath()
        self.videoPlayIkonu.moveTo(olcekli_mesafe, olcekli_mesafe)
        self.videoPlayIkonu.lineTo(olcekli_mesafe, self.ikonBoyutu - olcekli_mesafe)
        self.videoPlayIkonu.lineTo(self.ikonBoyutu - olcekli_mesafe, self.ikonBoyutu/2)
        self.videoPlayIkonu.lineTo(olcekli_mesafe, olcekli_mesafe)

        self.videoPauseIkonu = QPainterPath()
        self.videoPauseIkonu.moveTo(olcekli_mesafe, olcekli_mesafe)
        self.videoPauseIkonu.lineTo(olcekli_mesafe, self.ikonBoyutu - olcekli_mesafe)
        self.videoPauseIkonu.moveTo(3*olcekli_mesafe, olcekli_mesafe)
        self.videoPauseIkonu.lineTo(3*olcekli_mesafe, self.ikonBoyutu - olcekli_mesafe)

        self.videoStopIkonu = QPainterPath()
        self.videoStopIkonu.addRect(olcekli_mesafe,
                                    olcekli_mesafe,
                                    self.ikonBoyutu-2*olcekli_mesafe,
                                    self.ikonBoyutu-2*olcekli_mesafe)

        # self.videoBosDaireIkonu = QPainterPath()
        # self.videoBosDaireIkonu.addEllipse(self.videoSliderEllipseRect)

        self.videoIkonu = self.videoStopIkonu

    # ---------------------------------------------------------------------
    def act_playback_state_changed(self, pbstate):

        if pbstate == QMediaPlayer.PlaybackState.StoppedState:
            self.videoIkonu = self.videoStopIkonu
        elif pbstate == QMediaPlayer.PlaybackState.PlayingState:
            self.videoIkonu = self.videoPlayIkonu
        elif pbstate == QMediaPlayer.PlaybackState.PausedState:
            self.videoIkonu = self.videoPauseIkonu
        # else:
        #     # buraya gelmesi beklenmemekte, ilerki qt surumlerinde ek durumlar gelirse..
        #     self.videoIkonu = self.videoBosDaireIkonu

    # ---------------------------------------------------------------------
    def act_video_changed(self, video_hazir_mi):
        self.setText("")
        self.video_hazir_mi = video_hazir_mi
        # self.player.play()

    # ---------------------------------------------------------------------
    def act_native_size_changed(self, nativeSize):
        if not nativeSize.isEmpty():  # videoItem silinice bos QSizeF() gonderiyor.
            self._rect.setSize(nativeSize.scaled(self.videoItem.size(), Qt.KeepAspectRatio))
            self.update_elements_after_resize()

    # ---------------------------------------------------------------------
    def update_elements_after_resize(self):
        self.update_resize_handles()
        self.scene().parent().change_transform_box_values(self)
        # self.setPos(x, y)
        # return QGraphicsItem.mouseMoveEvent(self, event)

        self.update_painter_text_rect()

        self.videoItem.setPos(self._rect.topLeft())
        self.videoItem.setSize(self._rect.size())
        # self.sliderLine.setLength()
        # self.playControlsY = self._rect.bottom() - 50
        # self.playControlsY = self.videoItem.boundingRect().center().y()
        # self.playControlsY = 100
        self.sliderLine.setPoints(QPoint(0, self.playControlsY), QPoint(self._rect.right(), self.playControlsY))

        # TODO: hmm kirmiz da asagilara falan da tasinabilsin ,,
        #  ama tabi x ekseni gecerli olsun mavi de oyle ters eksende.
        # self.videoSliderEllipseRect.moveCenter(QPointF(event.pos().x(), self.playControlsY))
        # TODO: aynı zamanda y oranını tekrar hesaplamak lazım.
        self.audioSliderEllipseRect.moveCenter(
            QPointF(self.videoItem.boundingRect().center().x(), self.audioSliderEllipseRect.center().y()))

        self.audioSliderEllipseRect.moveCenter(QPointF(self.audioSliderEllipseRect.x() / self.videoItem.size().width() * 100,
                                                   self.audioSliderEllipseRect.center().y()))

        # self.videoSliderEllipseRect.moveCenter(
        #     QPointF(self.videoSliderEllipseRect.x(), self.playControlsY))

        if self.player.duration():  # olasi bir sifira bolmek durumu olmasin diye
            self.videoSliderEllipseRect.moveCenter(
                QPointF(self.videoItem.size().width() * self.player.position() / self.player.duration(),
                        self.playControlsY))

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):
        if change == self.ItemSelectedChange:
            if value:
                self.scene().parent().item_selected(self)
            else:
                self.scene().parent().item_deselected(self)
        elif change == self.ItemSceneChange:
            # The value argument is the new scene or a null pointer if the item is removed from a scene.
            # When item removed from the scene, we stop the player, to prevent stream errors.
            if not value:
                self.player.stop()
        return value
        # super(Rect, self).itemChange(change, value)

    # ---------------------------------------------------------------------
    # @Slot(int)  # qint64 # hata oluyor su an, bug varmis.
    def act_player_position_changed(self, pos):
        # yuzde = pos / self.player.duration() * 100
        # self.sliderEllipseCenterX = self.videoItem.size().width() / 100 * yuzde
        # self.sliderEllipseCenter = QPointF(self.videoItem.size().width() * pos / self.player.duration(), 100)

        # TODO:
        """
        self.videoSliderEllipseRect.moveCenter(QPointF(self.videoItem.size().width() * pos / self.player.duration(),
         self.playControlsY))
        ZeroDivisionError: float division by zero
        """
        # print(pos)
        # return
        if self.player.duration():
            self.videoSliderEllipseRect.moveCenter(
                QPointF(self.videoItem.size().width() * pos / self.player.duration(), self.playControlsY))
            # print(self.playControlsY)

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      "kim": self._kim,
                      "isEmbeded": self.isEmbeded,
                      "filePath": self.filePathForSave,
                      "originalSourceFilePath": self.originalSourceFilePath,
                      "rect": self.rect(),
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "scale": self.scale(),
                      "zValue": self.zValue(),
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "pen": self._pen,
                      "font": self._font,
                      # "imageOpacity": self.imageOpacity,
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "isFrozen": self.isFrozen,
                      # "isMirrorX": self.isMirrorX,
                      # "isMirrorY": self.isMirrorY,
                      "command": self._command,
                      }
        return properties

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return VideoItem.Type

    # ---------------------------------------------------------------------
    def childItems(self):
        liste = super(VideoItem, self).childItems()
        liste.remove(self.videoItem)
        return liste

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        super(VideoItem, self).mousePressEvent(event)

        if self.videoSliderEllipseRect.contains(event.pos()):
            if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState \
                    or self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
                self.player.play()
            else:
                # self.player.stop()
                self.player.pause()
            self.videoSliderEllipseStartDrag = True
            self.videoSliderEllipseFirstClickPos = event.pos()

        if self.audioSliderEllipseRect.contains(event.pos()):
            self.audioSliderEllipseStartDrag = True

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        if self.videoSliderEllipseStartDrag:
            if abs(self.videoSliderEllipseFirstClickPos.manhattanLength() - event.pos().manhattanLength()) > 0:
                # self.videoSliderEllipseRect.moveCenter(QPointF(event.pos().x(), self.playControlsY))
                self.videoSliderEllipseRect.moveCenter(event.pos())
                # yuzde = pos / self.player.duration() * 100
                # self.sliderEllipseCenterX = self.videoItem.size().width() / 100 * yuzde

                yuzde = event.pos().x() / self.videoItem.size().width() * 100
                yeniPlayerPosition = yuzde * self.player.duration() / 100
                # print(duration, "/", self.player.duration())
                self.player.setPosition(int(yeniPlayerPosition))
                self.player.play()
                self.update()
                # self.playControlsY = event.pos().y()

                # self.player.setPosition(event.pos().x()/self.videoItem.size().width() * 100 * self.player.duration())
            return

        if self.audioSliderEllipseStartDrag:
            yuzde = event.pos().y() / self.videoItem.size().height() * 100
            self.audioOutput.setVolume(100 - yuzde)
            # print(self.player.volume())
            # self.audioSliderEllipseRect.moveCenter(QPointF(self._rect.center().x(), event.pos().y()))
            self.audioSliderEllipseRect.moveCenter(event.pos())
            # self.playControlsY = event.pos().y()

            return

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

            self.setRect(rect)  # mouse release eventten gonderiyoruz undoya

            self.update_elements_after_resize()

        # event.accept()
        else:
            super(BaseItem, self).mouseMoveEvent(event)

            # super(BaseItem, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(VideoItem, self).mouseReleaseEvent(event)
        self.videoItem.setPos(0, 0)
        # if self.videoSliderEllipseRect.contains(event.pos()):
        if self.videoSliderEllipseStartDrag:
            self.videoSliderEllipseStartDrag = False

        # if self.audioSliderEllipseRect.contains(event.pos()):
        if self.audioSliderEllipseStartDrag:
            self.audioSliderEllipseStartDrag = False

    # ---------------------------------------------------------------------
    def hoverMoveEvent(self, event):
        # self.sagUstKare.hide()

        # cursor = self.scene().parent().cursor()

        if self.isSelected() and not self.isFrozen:
            if self.videoSliderEllipseRect.contains(event.pos()):
                self.isVideoSliderHovered = True
            else:
                self.isVideoSliderHovered = False

            if self.audioSliderEllipseRect.contains(event.pos()):
                self.isAudioSliderHovered = True
            else:
                self.isAudioSliderHovered = False

        super(VideoItem, self).hoverMoveEvent(event)

    # ---------------------------------------------------------------------
    def paint_warning_image(self, painter, option, widget=None):
        painter.setClipRect(option.exposedRect)
        painter.drawPixmap(self._rect.toRect(), self.pixmap)

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):
        super(VideoItem, self).paint(painter, option, widget)

        # painter.drawRect(self.sliderRect)
        # painter.drawEllipse(self.sliderEllipse)

        # painter.drawEllipse(self.videoSliderEllipseRect)

        if option.state & QStyle.State_MouseOver:
            painter.setOpacity(0.7)
            painter.setPen(QPen(Qt.red))
            # if self.isSelected():
            # if option.state & QStyle.State_Selected:
            #     painter.setBrush(QBrush(QColor(255, 50, 50)))
            # painter.drawLine(self.sliderLine)
            if self.isVideoSliderHovered:
                painter.setOpacity(1)
            painter.drawEllipse(self.videoSliderEllipseRect)
            painter.save()
            painter.translate(self.videoSliderEllipseRect.topLeft())
            painter.drawPath(self.videoIkonu)
            painter.restore()
            painter.drawText(self._rect, Qt.AlignLeft, "{}/{}".format(self.player.position(), self.player.duration()))
            painter.setPen(QPen(Qt.blue))
            painter.setOpacity(0.7)
            if self.isAudioSliderHovered:
                painter.setOpacity(1)
            painter.drawEllipse(self.audioSliderEllipseRect)
