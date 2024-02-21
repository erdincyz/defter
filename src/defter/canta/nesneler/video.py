# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '04/Sep/2016'

import os

from PySide6.QtCore import Qt, QUrl, QSizeF, QRectF, QPointF, QPoint, QLine
from PySide6.QtGui import QPen, QPixmap, QPixmapCache, QPainterPath, QColor
from PySide6.QtWidgets import QStyle
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem

from .. import shared
from ..nesneler.base import BaseItem


########################################################################
class GraphicsVideoItem(QGraphicsVideoItem):
    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(GraphicsVideoItem, self).__init__(parent)
        self.ustGrup = None

    def text(self):
        return ""

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, video_kopyalaniyor_mu):
        return ""


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
        self.videoItem.setFlag(QGraphicsVideoItem.GraphicsItemFlag.ItemStacksBehindParent)
        rect.setSize(self.videoItem.size())

        #
        arkaPlanRengi = QColor(0, 0, 0, 0)
        super(VideoItem, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)
        # QGraphicsVideoItem.__init__(parent)
        # super(VideoItem, self).__init__(parent)
        # BaseItem.__init__(pos, rect, arkaPlanRengi, pen, font, parent)

        # self.videoItem = QGraphicsVideoItem(self)
        # self.videoItem = GraphicsVideoItem(self)
        # self.videoItem.setFlag(QGraphicsVideoItem.ItemStacksBehindParent)

        self.kenarPen = QPen(pen.color(), 3, Qt.PenStyle.SolidLine)

        self.videoItem.nativeSizeChanged.connect(self.act_native_size_changed)
        # resolution = media.canonicalResource().resolution()
        # self.videoItem.nativeSizeChanged.connect(self._rect.setSize)
        self.videoItem.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

        self.video_hazir_mi = False

        self.videoItem.setParentItem(self)
        # self.player parenti defter.py ekle_video_direkt icinde (scene.py cagiriyor) ekliyoruz,
        # yoksa tab silinince self.player kaliyor,
        # ve video oyamakta iken tab kapanirsa self.player.playbackStateChanged sinyali vermeye devam ediyor
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
            self.eskiYazi = self.text()
            self.setText("Loading...")
            url = QUrl.fromLocalFile(filePath)
            # media = QMediaContent(url)
            # print(media.canonicalResource().audioCodec())
            # print(media.canonicalResource().videoCodec())
            # print(media.canonicalResource().audioBitRate())
            # print(media.canonicalResource().videoBitRate())
            # print(media.canonicalResource().channelCount())

            # self.player.setMedia(media)
            self.video_poziyon_sure_str = self.video_toplam_sure_str = "00:00:00"
            self.player.hasVideoChanged.connect(self.act_video_changed)
            self.player.positionChanged.connect(self.act_player_position_changed)
            self.player.durationChanged.connect(self.act_player_duration_changed)
            self.player.mediaStatusChanged.connect(self.act_player_media_status_changed)
            self.player.errorOccurred.connect(self.act_player_error_occured)
            self.player.errorChanged.connect(self.act_player_error_changed)
            self.player.seekableChanged.connect(self.act_seekable_changed)
            self.player.setSource(url)

            self.playControlsY = self._rect.bottom() - 50
            # self.playControlsY = self.videoItem.size().height() / 2
            self.ikonBoyutu = 20
            self.yariIkonBoyutu = self.ikonBoyutu / 2
            self.boundingRectTasmaDegeri = max(self.handleSize, self._pen.widthF() / 2, self.yariIkonBoyutu)
            # print(self.playControlsY)

            self.sliderLine = QLine(self.videoItem.pos().x() + 0,
                                    self.playControlsY,
                                    self.videoItem.size().width(),
                                    self.playControlsY)

            self.videoSliderEllipseRect = QRectF(0, self.playControlsY,
                                                 self.ikonBoyutu,
                                                 self.ikonBoyutu)
            self.videoIkonMerkezNoktasi = QPointF(0, self.playControlsY)

            self.daire_ici_ikonlari_olustur()

            self.videoSliderEllipseFirstClickPos = QPointF()
            self.videoSliderEllipseStartDrag = False
            self.audioSliderEllipseRect = QRectF(self._rect.center().x(),
                                                 # (100 / self._rect.height() / self.audioOutput.volume()),
                                                 self._rect.height() - self._rect.height() * self.audioOutput.volume(),
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
    def kareAl(self):

        # self.player.setPosition()
        image = self.player.videoSink().videoFrame().toImage()
        return image

    # ---------------------------------------------------------------------
    def setRect(self, rect):
        if self._rect == rect:
            return
        self.prepareGeometryChange()
        self._rect = rect
        self._boundingRect = QRectF()
        self.update()
        # self.videoItem.setSize(rect.size())

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Right:
            self.player.setPosition(self.player.position() + 10000)
        elif event.key() == Qt.Key.Key_Left:
            self.player.setPosition(self.player.position() - 10000)
        elif event.key() == Qt.Key.Key_Space:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState \
                    or self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
                self.player.play()
            else:
                # self.player.stop()
                self.player.pause()

        event.accept()

    # super(VideoItem, self).keyPressEvent(event)

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
        self.scene().parent().on_video_sag_menu_about_to_show(self)
        self.scene().parent().videoSagMenu.popup(event.screenPos())

        event.accept()

    # ---------------------------------------------------------------------
    def act_player_media_status_changed(self, status):
        # print(status)
        pass

    # ---------------------------------------------------------------------
    def act_player_error_occured(self, error, errorString):
        # print(error)
        # print(errorString)
        pass

    # ---------------------------------------------------------------------
    def act_player_error_changed(self):
        # print("degisti error")
        pass

    # ---------------------------------------------------------------------
    def act_seekable_changed(self, seekable):
        # print(seekable, "seekable")
        pass

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return VideoItem.Type

    # ---------------------------------------------------------------------
    def get_properties_for_save_binary(self):
        properties = {"type": self.type(),
                      "kim": self._kim,
                      "isEmbeded": self.isEmbeded,
                      "filePath": self.filePathForSave,
                      "originalSourceFilePath": self.originalSourceFilePath,
                      "rect": self._rect,
                      "pos": self.pos(),
                      "rotation": self.rotation(),
                      "zValue": self.zValue(),
                      "yaziRengi": self.yaziRengi,
                      "arkaPlanRengi": self.arkaPlanRengi,
                      "pen": self._pen,
                      "font": self._font,
                      # "imageOpacity": self.imageOpacity,
                      "yaziHiza": int(self.painterTextOption.alignment()),
                      "text": self.text(),
                      "isPinned": self.isPinned,
                      "command": self._command,
                      }
        return properties

    # ---------------------------------------------------------------------
    def varsaEnUsttekiGrubuGetir(self):
        parentItem = self.parentItem()
        while parentItem:
            if parentItem.type() == shared.GROUP_ITEM_TYPE:
                return parentItem
            parentItem = parentItem.parentItem()
        return None

    # ---------------------------------------------------------------------
    def nesne_sahneden_silinmek_uzere(self):
        # playerPositionChanged sinyali gitmeye devam ediyor ve nesne "already deleted" hatası.
        self.player.stop()

    # ---------------------------------------------------------------------
    def boundingRect(self):
        # if self._boundingRect.isNull():
        self._boundingRect = QRectF(self.rect())
        return self._boundingRect.adjusted(-self.boundingRectTasmaDegeri, -self.boundingRectTasmaDegeri,
                                           self.boundingRectTasmaDegeri, self.boundingRectTasmaDegeri)

    # ---------------------------------------------------------------------
    def setCizgiKalinligi(self, width):
        self._pen.setWidthF(width)
        self.textPen.setWidthF(width)
        self.boundingRectTasmaDegeri = max(self.handleSize, self._pen.widthF() / 2, self.yariIkonBoyutu)
        self.update()

    # ---------------------------------------------------------------------
    def daire_ici_ikonlari_olustur(self):

        olcekli_mesafe = self.ikonBoyutu / 4

        self.videoPlayIkonu = QPainterPath()
        self.videoPlayIkonu.moveTo(olcekli_mesafe, olcekli_mesafe)
        self.videoPlayIkonu.lineTo(olcekli_mesafe, self.ikonBoyutu - olcekli_mesafe)
        self.videoPlayIkonu.lineTo(self.ikonBoyutu - olcekli_mesafe, self.ikonBoyutu / 2)
        self.videoPlayIkonu.lineTo(olcekli_mesafe, olcekli_mesafe)

        self.videoPauseIkonu = QPainterPath()
        self.videoPauseIkonu.moveTo(olcekli_mesafe, olcekli_mesafe)
        self.videoPauseIkonu.lineTo(olcekli_mesafe, self.ikonBoyutu - olcekli_mesafe)
        self.videoPauseIkonu.moveTo(3 * olcekli_mesafe, olcekli_mesafe)
        self.videoPauseIkonu.lineTo(3 * olcekli_mesafe, self.ikonBoyutu - olcekli_mesafe)

        self.videoStopIkonu = QPainterPath()
        self.videoStopIkonu.addRect(olcekli_mesafe,
                                    olcekli_mesafe,
                                    self.ikonBoyutu - 2 * olcekli_mesafe,
                                    self.ikonBoyutu - 2 * olcekli_mesafe)

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
        self.setText(self.eskiYazi)
        self.video_hazir_mi = video_hazir_mi
        # self.player.play()

    # ---------------------------------------------------------------------
    def act_native_size_changed(self, nativeSize):
        if not nativeSize.isEmpty():  # videoItem silinice bos QSizeF() gonderiyor.
            self._rect.setSize(nativeSize.scaled(self.videoItem.size(), Qt.AspectRatioMode.KeepAspectRatio))
            self.update_elements_after_resize()

    # ---------------------------------------------------------------------
    def update_elements_after_resize(self):
        self.update_resize_handles()
        self.scene().parent().change_transform_box_values(self)
        # self.setPos(x, y)
        # return QGraphicsItem.mouseMoveEvent(self, event)

        self.update_painter_text_rect()

        self.playControlsY = self.videoItem.size().height() / 2

        self.videoItem.setPos(self._rect.topLeft())
        self.videoItem.setSize(self._rect.size())
        # self.sliderLine.setLength()
        # self.playControlsY = self._rect.bottom() - 50
        # self.playControlsY = self.videoItem.boundingRect().center().y()
        # self.playControlsY = 100
        self.sliderLine.setPoints(QPoint(self.videoItem.pos().x(), self.playControlsY),
                                  QPoint(self._rect.right() + self.videoItem.pos().x(), self.playControlsY))

        # TODO: hmm kirmiz da asagilara falan da tasinabilsin ,,
        #  ama tabi x ekseni gecerli olsun mavi de oyle ters eksende.
        # self.videoSliderEllipseRect.moveCenter(QPointF(event.pos().x(), self.playControlsY))
        # TODO: aynı zamanda y oranını tekrar hesaplamak lazım.
        self.audioSliderEllipseRect.moveCenter(QPointF(self._rect.center().x(),
                                                       self._rect.height() - self._rect.height() * self.audioOutput.volume()))

        if self.player.duration():  # olasi bir sifira bolmek durumu olmasin diye
            self.videoSliderEllipseRect.moveCenter(
                QPointF(self.videoItem.pos().x() + (
                        self.videoItem.size().width() * self.player.position() / self.player.duration()),
                        self.playControlsY))

    # ---------------------------------------------------------------------
    def itemChange(self, change, value):
        if change == BaseItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.scene().parent().item_selected(self)
            else:
                self.scene().parent().item_deselected(self)
        elif change == BaseItem.GraphicsItemChange.ItemSceneChange:
            # The value argument is the new scene or a null pointer if the item is removed from a scene.
            # When item removed from the scene, we stop the player, to prevent stream errors.
            if not value:
                self.player.stop()
        return value
        # super(Rect, self).itemChange(change, value)

    # ---------------------------------------------------------------------
    # @Slot(int)  # qint64 # hata oluyor su an, bug varmis.
    def act_player_position_changed(self, pos_ms):
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
                QPointF(self.videoItem.pos().x() + (self.videoItem.size().width() * pos_ms / self.player.duration()),
                        self.playControlsY))
            # print(self.playControlsY)

        dk, sn = divmod((pos_ms // 1000), 60)
        saat, dk = divmod(dk, 60)
        self.video_poziyon_sure_str = f"{saat:02}:{dk:02}:{sn:02}"

    # ---------------------------------------------------------------------
    def act_player_duration_changed(self, toplam_sure_ms):
        dk, sn = divmod((toplam_sure_ms // 1000), 60)
        saat, dk = divmod(dk, 60)
        self.video_toplam_sure_str = f"{saat:02}:{dk:02}:{sn:02}"

    # ---------------------------------------------------------------------
    def childItems(self):
        liste = super(VideoItem, self).childItems()
        liste.remove(self.videoItem)
        return liste

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        super(VideoItem, self).mousePressEvent(event)

        if self.videoSliderEllipseRect.contains(event.pos()):
            # print(self.player.playbackState(), 1)
            if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState \
                    or self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
                self.player.play()
                # print(self.player.playbackState(), 2)
            else:
                # self.player.stop()
                self.player.pause()
            self.videoSliderEllipseStartDrag = True
            self.yeniPlayerPosition = None
            self.videoSliderEllipseFirstClickPos = event.pos()

        if self.audioSliderEllipseRect.contains(event.pos()):
            self.audioSliderEllipseStartDrag = True

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        if self.videoSliderEllipseStartDrag:
            if abs(self.videoSliderEllipseFirstClickPos.manhattanLength() - event.pos().manhattanLength()) > 0:
                self.player.pause()
                x = min(max(event.pos().x(), 0), self.videoItem.size().width())
                self.videoSliderEllipseRect.moveCenter(QPointF(x, self.playControlsY))
                # ~ self.videoSliderEllipseRect.moveCenter(event.pos())
                # yuzde = pos / self.player.duration() * 100
                # self.sliderEllipseCenterX = self.videoItem.size().width() / 100 * yuzde

                oran = x / self.videoItem.size().width()
                self.yeniPlayerPosition = int(oran * self.player.duration())
                # print(duration, "/", self.player.duration())

                # self.player.setPosition(int(self.yeniPlayerPosition))
                # self.player.play()

                # print(self.player.position(), self.yeniPlayerPosition)
                dk, sn = divmod((self.yeniPlayerPosition // 1000), 60)
                saat, dk = divmod(dk, 60)
                self.video_poziyon_sure_str = f"{saat:02}:{dk:02}:{sn:02}"
                self.update()

                # self.playControlsY = event.pos().y()

                # self.player.setPosition(event.pos().x()/self.videoItem.size().width() * 100 * self.player.duration())
            return

        if self.audioSliderEllipseStartDrag:
            yuzde = event.pos().y() / self._rect.height()
            self.audioOutput.setVolume(1 - yuzde)
            # if self.yariIkonBoyutu < event.pos().y() < self._rect.size().height() - self.yariIkonBoyutu:
            if 0 < event.pos().y() < self._rect.size().height():
                self.audioSliderEllipseRect.moveCenter(QPointF(self._rect.center().x(), event.pos().y()))

            return

        # burda super(VideoItem, self).mouseMoveEvent(event) cagirmiyoruz
        # shift + resize durumu videoda yok mesela o yuzden.
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

            c = self._rect.center()

            # Alt Key - to resize around center.
            if event.modifiers() == Qt.KeyboardModifier.AltModifier:
                rect.moveCenter(c)

            # ---------------------------------------------------------------------
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

            self.setRect(rect)  # mouse release eventten gonderiyoruz undoya

            self.update_elements_after_resize()

        # event.accept()
        else:
            super(BaseItem, self).mouseMoveEvent(event)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(VideoItem, self).mouseReleaseEvent(event)
        # self.videoItem.setPos(0, 0)
        self.videoItem.setPos(self._rect.topLeft())
        # if self.videoSliderEllipseRect.contains(event.pos()):
        if self.videoSliderEllipseStartDrag:
            if self.yeniPlayerPosition:
                self.player.blockSignals(True)
                self.player.setPosition(int(self.yeniPlayerPosition))
                self.player.blockSignals(False)
                self.update()
                self.player.play()
            self.videoSliderEllipseStartDrag = False

        # if self.audioSliderEllipseRect.contains(event.pos()):
        if self.audioSliderEllipseStartDrag:
            self.audioSliderEllipseStartDrag = False

    # ---------------------------------------------------------------------
    def hoverEnterEvent(self, event):
        # event propagationdan dolayi bos da olsa burda implement etmek lazim
        # mousePress,release,move,doubleclick de bu mantıkta...
        # baska yerden baslayip mousepress ile , mousemove baska, mouseReleas baska widgetta gibi
        # icinden cikilmaz durumlara sebep olabiliyor.
        # ayrica override edince accept() de edilmis oluyor mouseeventler
        super(VideoItem, self).hoverEnterEvent(event)

    # ---------------------------------------------------------------------
    def hoverMoveEvent(self, event):
        # self.sagUstKare.hide()

        # cursor = self.scene().parent().cursor()

        if self.isSelected():
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
    def hoverLeaveEvent(self, event):
        # event propagationdan dolayi bos da olsa burda implement etmek lazim
        # mousePress,release,move,doubleclick de bu mantıkta...
        # baska yerden baslayip mousepress ile , mousemove baska, mouseReleas baska widgetta gibi
        # icinden cikilmaz durumlara sebep olabiliyor.
        # ayrica override edince accept() de edilmis oluyor mouseeventler
        super(VideoItem, self).hoverLeaveEvent(event)

    # ---------------------------------------------------------------------
    def ses_ayarla(self, delta):

        if delta > 0:
            self.audioOutput.setVolume(self.audioOutput.volume() + 0.025)

        else:
            self.audioOutput.setVolume(self.audioOutput.volume() - 0.025)

        self.audioSliderEllipseRect.moveCenter(QPointF(self._rect.center().x(),
                                                       self._rect.size().height() - self._rect.size().height() * self.audioOutput.volume()))

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):
        # factor = 1.41 ** (event.delta() / 240.0)

        if self.ustGrup:
            return BaseItem.wheelEvent(self, event)

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
            self.scaleItemByResizing(event.delta())

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
        #
        elif toplam == altShift:
            # self.changeImageItemTextBackgroundColorAlpha(event.delta())
            self.changeLineColorAlpha(event.delta())

        # elif toplam == ctrlAltShift:
        #     self.scaleItemByResizing(event.delta())

        else:
            self.ses_ayarla(event.delta())
            # super(VideoItem, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def paint_warning_image(self, painter, option, widget=None):
        painter.setClipRect(option.exposedRect)
        painter.drawPixmap(self._rect.toRect(), self.pixmap)

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget=None):
        # super(VideoItem, self).paint(painter, option, widget)

        if not self._pen.width():
            painter.setPen(Qt.PenStyle.NoPen)
        else:
            painter.setPen(self._pen)
        painter.setBrush(self._brush)

        painter.setPen(self.kenarPen)
        painter.drawRect(self._rect)

        if self._text:
            # painter.setWorldMatrixEnabled(False)
            painter.save()
            painter.setFont(self._font)
            # we recreate textPen from same exact color. otherwise, color's alpha not working.
            painter.setPen(self.textPen)
            painter.translate(self._rect.center())
            painter.rotate(-self.rotation())

            painter.translate(-self._rect.center())

            painter.drawText(self.painterTextRect, self._text, self.painterTextOption)

            # painter.drawText(10,10, txt)
            painter.restore()
            # painter.setWorldMatrixEnabled(True)

        # if option.state & QStyle.State_MouseOver:
        if option.state & QStyle.StateFlag.State_Selected or self.cosmeticSelect:
            # painter.setPen(QPen(option.palette.windowText(), 0, Qt.DashLine))
            # painter.setPen(QPen(option.palette.highlight(), 0, Qt.DashLine))

            if self.isActiveItem:
                selectionPenBottom = self.selectionPenBottomIfAlsoActiveItem
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(self.handleBrush)
                painter.drawRect(self.topLeftHandle)
                painter.drawRect(self.topRightHandle)
                painter.drawRect(self.bottomRightHandle)
                painter.drawRect(self.bottomLeftHandle)
            else:
                selectionPenBottom = self.selectionPenBottom

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(selectionPenBottom)
            painter.drawRect(self.rect())

        if option.state & QStyle.StateFlag.State_MouseOver:
            painter.setOpacity(0.7)
            painter.setPen(QPen(Qt.GlobalColor.red))
            # if self.isSelected():
            # if option.state & QStyle.State_Selected:
            #     painter.setBrush(QBrush(QColor(255, 50, 50)))
            painter.drawLine(self.sliderLine)
            if self.isVideoSliderHovered:
                painter.setOpacity(1)
            painter.drawEllipse(self.videoSliderEllipseRect)
            painter.save()
            painter.translate(self.videoSliderEllipseRect.topLeft())
            painter.drawPath(self.videoIkonu)
            painter.restore()
            painter.drawText(self._rect, Qt.AlignmentFlag.AlignLeft, f"{self.video_poziyon_sure_str} - {self.video_toplam_sure_str}")
            painter.setPen(QPen(Qt.GlobalColor.blue))
            painter.setOpacity(0.7)
            if self.isAudioSliderHovered:
                painter.setOpacity(1)
            painter.drawEllipse(self.audioSliderEllipseRect)

        # # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self._rect, "{0:.2f},  {1:.2f} pos \n{2:.2f},  {3:.2f} spos".format(p.x(), p.y(), s.x(), s.y()))
        # # # t = self.transformOriginPoint()
        # # # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self._rect.topLeft())
        # painter.drawText(self._rect.x(), self._rect.y(), "{0:.2f}  {1:.2f} map".format(mapped.x(), mapped.y()))
        # painter.drawEllipse(self.scenePos(), 10, 10)
        # painter.setPen(Qt.blue)
        # painter.drawEllipse(self.mapFromScene(self.pos()), 10, 10)
        # r = self.textItem.boundingRect()
        # r = self.mapRectFromItem(self.textItem, r)
        # painter.drawRect(r)
        # painter.drawText(self._rect.center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # painter.setPen(QPen(Qt.red,17))
        # painter.drawPoint(self._rect.center())
        # painter.setPen(QPen(Qt.green,12))
        # painter.drawPoint(self.mapFromScene(self.sceneBoundingRect().center()))
        # painter.setPen(QPen(Qt.blue,8))
        # painter.drawPoint(self.sceneBoundingRect().center())
        # painter.drawRect(self.sceneBoundingRect())
        # # # # # # debug end - pos() # # # # #

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, video_kopyalaniyor_mu):
        video_adi = os.path.basename(self.filePathForSave)
        video_adres = self.filePathForSave
        if not html_klasor_kayit_adres:  # def dosyasi icine kaydet
            if self.isEmbeded:
                video_adres = os.path.join("videos", video_adi)
        else:  # dosya html olarak baska bir yere kaydediliyor
            # kopyalanmazsa da, zaten embed olmayan video normal hddeki adresten yuklenecektir.
            if video_kopyalaniyor_mu:
                # iptal: if not self.isEmbeded:  # embed ise zaten tmp klasorden hedef klasore baska metodta kopylanıyor hepsi.
                # embed veya degil, yukarda bahsettigi gibi video kopyalansa da adresi de guncellemek lazim.
                video_adres = os.path.join(html_klasor_kayit_adres, "videos", video_adi)

        # video_str = f'<video src="{self.filePathForSave}" width:{self.videoItem.size().width()};' \
        #             f' height{self.videoItem.size().height()}"></video>'
        video_str = f'<video style="width:100%; height:100%;" controls> <source src="{video_adres}"></video>'

        # rect = self.sceneBoundingRect()
        # xr = rect.left()
        # yr = rect.top()
        # xs = self.scene().sceneRect().x()
        # ys = self.scene().sceneRect().y()
        # x = xr - xs
        # y = yr - ys

        w = self._rect.width()
        h = self._rect.height()
        c = self.sceneBoundingRect().center()
        xr = c.x() - w / 2
        yr = c.y() - h / 2
        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = xr - xs
        y = yr - ys

        bicimSozluk = self.ver_karakter_bicimi()
        bold = "font-weight:bold;" if bicimSozluk["b"] else ""
        italic = "font-style:italic;" if bicimSozluk["i"] else ""
        underline = "underline" if bicimSozluk["u"] else ""
        strikeOut = "line-through" if bicimSozluk["s"] else ""
        overline = "overline" if bicimSozluk["o"] else ""
        bicimler1 = bold + italic
        if any((underline, strikeOut, overline)):
            bicimler2 = f"text-decoration: {underline} {strikeOut} {overline};"
        else:
            bicimler2 = ""

        renk_arkaPlan = f"({self.arkaPlanRengi.red()},{self.arkaPlanRengi.green()},{self.arkaPlanRengi.blue()},{self.arkaPlanRengi.alpha() / 255})"
        renk_yazi = f"({self.yaziRengi.red()},{self.yaziRengi.green()},{self.yaziRengi.blue()},{self.yaziRengi.alpha() / 255})"

        hiza = self.ver_yazi_hizasi()
        # if hiza == Qt.AlignLeft or hiza == Qt.AlignLeft | Qt.AlignVCenter:
        #     yazi_hiza = "left"
        if hiza == Qt.AlignmentFlag.AlignCenter or hiza == Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter:
            yazi_hiza = "center"
        elif hiza == Qt.AlignmentFlag.AlignRight or hiza == Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter:
            yazi_hiza = "right"
        elif hiza == Qt.AlignmentFlag.AlignJustify or hiza == Qt.AlignmentFlag.AlignJustify | Qt.AlignmentFlag.AlignVCenter:
            yazi_hiza = "justify"
        else:
            yazi_hiza = "left"

        div_str = f"""
                    <div style="
                     background:rgba{renk_arkaPlan};
                     color:rgba{renk_yazi};
                     font-size:{self.fontPointSizeF()}pt; 
                     font-family:{self.font().family()};
                     text-align: {yazi_hiza};
                     {bicimler1}
                     {bicimler2}
                     position:absolute;
                     z-index:{int(self.zValue() * 10) if self.zValue() else 0};
                     width:{self._rect.width()}px;
                     height:{self._rect.height()}px;
                     top:{y}px;
                     left:{x}px;
                     transform-box: fill-box;
                     transform-origin: center;
                     transform: rotate({self.rotation()}deg);" id="{self._kim}">{video_str}{self.text()}</div>\n"""

        # /*background-image:url('{resim_adres}');*/
        return div_str
