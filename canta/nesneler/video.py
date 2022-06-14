# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '04/Sep/2016'

import os

from PySide6.QtCore import Qt, QUrl, QSizeF, QRectF, QPointF, QPoint, QLine
from PySide6.QtGui import QPen, QPixmap, QPixmapCache, QPainterPath, QBrush, QColor
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
            self.yariIkonBoyutu = self.ikonBoyutu / 2
            self.boundingRectTasmaDegeri = max(self.handleSize, self._pen.widthF() / 2, self.yariIkonBoyutu)
            # print(self.playControlsY)

            self.sliderLine = QLine(self.videoItem.pos().x() + 0,
                                    self.playControlsY,
                                    self.videoItem.size().width(),
                                    self.playControlsY)

            self.player.positionChanged.connect(self.act_player_position_changed)

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
    def html_dive_cevir(self, html_klasor_kayit_adres, video_kopyalaniyor_mu):
        video_adi = os.path.basename(self.filePathForSave)
        video_adres = self.filePathForSave
        if not html_klasor_kayit_adres:  # def dosyasi icine kaydet
            if self.isEmbeded:
                video_adres = os.path.join("videos", video_adi)
        else:  # dosya html olarak baska bir yere kaydediliyor
            # kopyalanmazsa da, zaten embed olmayan video normal hddeki adresten yuklenecektir.
            if video_kopyalaniyor_mu:
                if not self.isEmbeded:  # embed ise zaten tmp klasorden hedef klasore baska metodta kopylanıyor hepsi.
                    video_adres = os.path.join(html_klasor_kayit_adres, "videos", video_adi)

        # video_str = f'<video src="{self.filePathForSave}" width:{self.videoItem.size().width()}; height{self.videoItem.size().height()}"></video>'
        video_str = f'<video style="width:100%; height:100%;" controls> <source src="{video_adres}"></video>'

        rect = self.sceneBoundingRect()
        xr = rect.left()
        yr = rect.top()
        xs = self.scene().sceneRect().x()
        ys = self.scene().sceneRect().y()
        x = xr - xs
        y = yr - ys

        bicimSozluk = self.ver_karakter_bicimi()
        bold = "font-weight:bold;" if bicimSozluk["b"] else ""
        italic = "font-style:bold;" if bicimSozluk["i"] else ""
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
        if hiza == Qt.AlignCenter or hiza == Qt.AlignCenter | Qt.AlignVCenter:
            yazi_hiza = "center"
        elif hiza == Qt.AlignRight or hiza == Qt.AlignRight | Qt.AlignVCenter:
            yazi_hiza = "right"
        elif hiza == Qt.AlignJustify or hiza == Qt.AlignJustify | Qt.AlignVCenter:
            yazi_hiza = "justify"
        else:
            yazi_hiza = "left"

        div_str = f"""
                    <div style="
                     background:rgba{renk_arkaPlan};
                     color:rgba{renk_yazi};
                     font-size:{self.fontPointSize()}pt; 
                     font-family:{self.font().family()};
                     text-align: {yazi_hiza};
                     {bicimler1}
                     {bicimler2}
                     position:absolute;
                     z-index:{int(self.zValue() * 10) if self.zValue() else 0};
                     width:{self._rect.width() * self.scale()}px;
                     height:{self._rect.height() * self.scale()}px;
                     top:{y}px;
                     left:{x}px;
                     transform-box: fill-box;
                     transform-origin: center;
                     transform: rotate({self.rotation()}deg);" id="{self._kim}">{video_str}{self.text()}</div>\n"""

        # /*background-image:url('{resim_adres}');*/
        return div_str

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
                      "command": self._command,
                      }
        return properties

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return VideoItem.Type

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
                QPointF(self.videoItem.pos().x() + (self.videoItem.size().width() * pos / self.player.duration()),
                        self.playControlsY))
            # print(self.playControlsY)

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

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(VideoItem, self).mouseReleaseEvent(event)
        # self.videoItem.setPos(0, 0)
        self.videoItem.setPos(self._rect.topLeft())
        # if self.videoSliderEllipseRect.contains(event.pos()):
        if self.videoSliderEllipseStartDrag:
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
            # self.scaleItem(event.angleDelta().y())

        # elif event.modifiers() & Qt.ShiftModifier:
        elif toplam == shift:
            self.rotateItem(event.delta())

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
        super(VideoItem, self).paint(painter, option, widget)

        # painter.drawRect(self.sliderRect)
        # painter.drawEllipse(self.sliderEllipse)

        # painter.drawEllipse(self.videoSliderEllipseRect)
        # painter.drawRect(self.boundingRect())

        if option.state & QStyle.State_MouseOver:
            painter.setOpacity(0.7)
            painter.setPen(QPen(Qt.red))
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
            painter.drawText(self._rect, Qt.AlignLeft, "{}/{}".format(self.player.position(), self.player.duration()))
            painter.setPen(QPen(Qt.blue))
            painter.setOpacity(0.7)
            if self.isAudioSliderHovered:
                painter.setOpacity(1)
            painter.drawEllipse(self.audioSliderEllipseRect)
