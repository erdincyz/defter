# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '06/03/24'
__author__ = 'E. Y.'

import os
import time
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (QHBoxLayout, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QFileDialog, QAbstractItemView, QComboBox,
                               QCheckBox)

from .. import shared
from ...canta.pushButton import PushButton
from ...canta.lineEdit import AraLineEdit
from ..yw.yuzenWidget import YuzenWidget


#######################################################################
class AltyaziYW(YuzenWidget):
    log = Signal(str)
    sonKlasorVideolarGuncelle = Signal()
    sahneAktifNesneBilgisiGuncelle = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(AltyaziYW, self).__init__(kapatilabilir_mi=False, parent=parent)

        temelW = QWidget(self)
        temelW.setContentsMargins(0, 0, 0, 0)
        anaLay = QVBoxLayout(temelW)
        anaLay.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)
        # anaLay.setContentsMargins(3, 5, 3, 3)
        # anaLay.setContentsMargins(1, 3, 1, 1)
        anaLay.setContentsMargins(1, 3, 1, 3)
        anaLay.setSpacing(3)

        btnRenk = QColor(200, 200, 200)

        self.otoGuncelleCBox = QCheckBox(self)
        self.otoGuncelleCBox.setMaximumWidth(15)
        self.otoGuncelleCBox.setToolTip(self.tr("Auto refresh subtitles when a video item is selected"))
        self.otoGuncelleCBox.setStatusTip(self.tr("Auto refresh subtitles when a video item is selected"))
        self.otoGuncelleCBox.setChecked(True)

        self.yukleBtn = PushButton(self.tr('Load'), yukseklik=16, renkArkaplan=btnRenk, parent=temelW)
        self.yukleBtn.setFixedWidth(35)
        self.yukleBtn.setToolTip(self.tr("Load Subtitle"))
        self.yukleBtn.clicked.connect(self.altyazi_yukle)
        # self.yukleBtn.setDisabled(True)

        self.araLineEdit = AraLineEdit(self)
        # self.araLineEdit.setMinimumWidth(250)
        self.araLineEdit.setPlaceholderText(self.tr("Search..."))
        self.araLineEdit.returnVeyaEnterBasildi.connect(self.act_ara)
        # self.araLineEdit.shiftEnterVeyaReturnBasildi.connect(self.act_ara)

        self.araLineEdit.temizleBtnClicked.connect(self.act_aramayi_temizle)
        self.araLineEdit.aramaMetniDegisti.connect(lambda: self.act_aramayi_temizle(yeniden_ara=True))

        self.zamanAcKapaBtn = PushButton(self.tr('0:0'), yukseklik=16, renkArkaplan=btnRenk, parent=temelW)
        self.zamanAcKapaBtn.setFixedWidth(35)
        self.zamanAcKapaBtn.setToolTip(self.tr("Timecode On / Off"))
        self.zamanAcKapaBtn.clicked.connect(self.zaman_ac_kapa)
        # self.zamanAcKapaBtn.setDisabled(True)

        self.oncekiAltyaziBtn = PushButton(self.tr('<'), yukseklik=16, renkArkaplan=btnRenk, parent=temelW)
        self.oncekiAltyaziBtn.setFixedWidth(35)
        self.oncekiAltyaziBtn.setToolTip(self.tr("Previous Subtitle"))
        self.oncekiAltyaziBtn.clicked.connect(self.onceki_altyaziya_git)
        # self.oncekiAltyaziBtn.setDisabled(True)

        self.sonrakiAltyaziBtn = PushButton(self.tr('>'), yukseklik=16, renkArkaplan=btnRenk, parent=temelW)
        self.sonrakiAltyaziBtn.setFixedWidth(35)
        self.sonrakiAltyaziBtn.setToolTip(self.tr("Next subtitle"))
        self.sonrakiAltyaziBtn.clicked.connect(self.sonraki_altyaziya_git)
        # self.sonrakiAltyaziBtn.setDisabled(True)

        self.oynatDurdurBtn = PushButton(self.tr('//>'), yukseklik=16, renkArkaplan=btnRenk, parent=temelW)
        self.oynatDurdurBtn.setFixedWidth(35)
        self.oynatDurdurBtn.setToolTip(self.tr("Play / Pause"))
        self.oynatDurdurBtn.clicked.connect(self.oynat_durdur)
        # self.oynatDurdurBtn.setDisabled(True)

        self.dongudeOynatBtn = PushButton(self.tr('[o-o]'), yukseklik=16, renkArkaplan=btnRenk, parent=temelW)
        self.dongudeOynatBtn.setFixedWidth(35)
        self.dongudeOynatBtn.setToolTip(self.tr("Play selected subtitles in loop"))
        self.dongudeOynatBtn.clicked.connect(self.oynat_dongude)
        self.dongudeOynatBtn.setCheckable(True)
        # self.dongudeOynatBtn.setDisabled(True)

        self.altyaziCBox = QComboBox(temelW)
        self.altyaziCBox.setEditable(False)
        # self.altyaziCBox.currentIndexChanged.connect(self.altyazi_degistir_cbox)
        self.altyaziCBox.activated.connect(self.altyazi_degistir_cbox)

        layYukle = QHBoxLayout()
        # layYukle.addWidget(lblOtoGuncelle)
        layYukle.addWidget(self.otoGuncelleCBox)
        layYukle.addWidget(self.yukleBtn)
        # layYukle.addStretch()
        layYukle.addWidget(self.altyaziCBox)
        layOynatmaKontrol = QHBoxLayout()
        layOynatmaKontrol.addWidget(self.zamanAcKapaBtn)
        layOynatmaKontrol.addWidget(self.oncekiAltyaziBtn)
        layOynatmaKontrol.addWidget(self.sonrakiAltyaziBtn)
        layOynatmaKontrol.addWidget(self.oynatDurdurBtn)
        layOynatmaKontrol.addWidget(self.dongudeOynatBtn)
        layOynatmaKontrol.addStretch()
        layOynatmaKontrol.addSpacing(10)

        self.dongude = False

        self.altyaziTW = QTableWidget(temelW)
        self.altyaziTW.setObjectName("aTW")
        self.altyaziTW.setDragEnabled(True)
        self.altyaziTW.setColumnCount(2)
        self.altyaziTW.horizontalHeader().hide()
        self.altyaziTW.verticalHeader().hide()
        self.altyaziTW.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.altyaziTW.setWordWrap(True)
        self.altyaziTW.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # self.altyaziTW.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.altyaziTW.itemDoubleClicked.connect(self.tiklanan_altyazi_zamanina_git)
        # self.altyaziTW.currentItemChanged.connect(self.loop)
        self.altyaziTW.itemSelectionChanged.connect(self.loop)
        # self.altyaziTW.itemSelectionChanged.connect(self.act_stylePresetsListWidget_secim_degisti)
        # self.altyaziTW.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self.altyaziTW.customContextMenuRequested.connect(self.act_stiller_sag_menu_goster)

        self.dongudekiSatirBrush = QBrush(QColor(220, 225, 235))
        self.orjinalBrush = QTableWidgetItem().background()
        self.donguSecilenSatirIndexleri = []

        qss_stil = """
                    QTableViewt{outline: none;}
                    QTableWidget::item{padding: 3px 0;}
                    QTableWidget::item:selected {color: #ffffff; background: #81aac5; border:none;}
                    """

        self.altyaziTW.setStyleSheet(qss_stil)
        # self.altyaziTW.setAttribute(Qt.WA_MacShowFocusRect, 0)

        anaLay.addLayout(layYukle)
        anaLay.addWidget(self.araLineEdit)
        anaLay.addWidget(self.altyaziTW)
        anaLay.addLayout(layOynatmaKontrol)
        # anaLay.addStretch()

        self.ekleWidget(temelW)

        self.setMinimumWidth(250)
        self.setMinimumHeight(170)

        self.sonKlasorVideolar = ""
        self.sahneAktifNesne = None

    # ---------------------------------------------------------------------
    def sonKlasorVideolar_guncelle(self, klasor):
        self.sonKlasorVideolar = klasor

    # ---------------------------------------------------------------------
    def sahneAktifNesneBilgisi_guncelle(self, nesne):
        # self.sahneAktifNesne = weakref.ref(nesne)
        self.sahneAktifNesne = nesne

    # ---------------------------------------------------------------------
    def zaman_ac_kapa(self):
        self.altyaziTW.setColumnHidden(0, not self.altyaziTW.isColumnHidden(0))

    # ---------------------------------------------------------------------
    def act_aramayi_temizle(self, yeniden_ara=False):
        # TODO: bu undoRedoSiniflarda 6 yerde var
        # print("temizlendi")
        for satir in range(self.altyaziTW.rowCount()):
            self.altyaziTW.setRowHidden(satir, False)
            # if self.isVisible():
            if yeniden_ara:
                self.act_ara()

    # ---------------------------------------------------------------------
    def act_ara(self):
        for satir in range(self.altyaziTW.rowCount()):
            nesne = self.altyaziTW.item(satir, 1)
            if not self.araLineEdit.text() in nesne.text():
                self.altyaziTW.setRowHidden(satir, True)

    # ---------------------------------------------------------------------
    def oynat_durdur(self):
        self.dongude = False
        if self.donguSecilenSatirIndexleri:
            for satirIdx in self.donguSecilenSatirIndexleri:
                self.altyaziTW.item(satirIdx.row(), 0).setBackground(self.orjinalBrush)
                self.altyaziTW.item(satirIdx.row(), 1).setBackground(self.orjinalBrush)
            self.donguSecilenSatirIndexleri = []

        videoNesne = self.videoNesnesi()
        if videoNesne:
            if videoNesne.player.playbackState() == videoNesne.player.PlaybackState.PlayingState:
                videoNesne.player.pause()
            else:
                videoNesne.player.play()

    # ---------------------------------------------------------------------
    def sonraki_altyaziya_git(self):
        satir = self.altyaziTW.currentRow()
        if not satir == -1:
            self.altyaziTW.selectRow(satir + 1)
            self.tiklanan_altyazi_zamanina_git(self.altyaziTW.currentItem())

    # ---------------------------------------------------------------------
    def onceki_altyaziya_git(self):
        satir = self.altyaziTW.currentRow()
        if not satir == -1:
            self.altyaziTW.selectRow(satir - 1)
            self.tiklanan_altyazi_zamanina_git(self.altyaziTW.currentItem())

    # ---------------------------------------------------------------------
    def oynat_dongude(self):
        self.dongude = True
        self.donguSecilenSatirIndexleri = self.altyaziTW.selectionModel().selectedRows()
        if self.donguSecilenSatirIndexleri:

            for satirIdx in self.donguSecilenSatirIndexleri:
                self.altyaziTW.item(satirIdx.row(), 0).setBackground(self.dongudekiSatirBrush)
                self.altyaziTW.item(satirIdx.row(), 1).setBackground(self.dongudekiSatirBrush)

            self.baslaSatir = self.donguSecilenSatirIndexleri[0].row()
            self.bitirSatir = self.donguSecilenSatirIndexleri[-1].row() + 1
            self.tiklanan_altyazi_zamanina_git(self.altyaziTW.item(self.baslaSatir, 0))
            self.altyaziTW.selectRow(self.baslaSatir)

            videoNesne = self.videoNesnesi()
            if videoNesne:
                if not videoNesne.player.playbackState() == videoNesne.player.PlaybackState.PlayingState:
                    videoNesne.player.play()

    # ---------------------------------------------------------------------
    # def loop(self, item, onceki):
    def loop(self):
        if self.dongude:
            # print(self.altyaziTW.currentRow(), self.bitirSatir)
            if self.altyaziTW.currentRow() == self.bitirSatir:
                self.tiklanan_altyazi_zamanina_git(self.altyaziTW.item(self.baslaSatir, 0))
                self.altyaziTW.selectRow(self.baslaSatir)

    # ---------------------------------------------------------------------
    def videoNesnesi(self):
        self.sahneAktifNesneBilgisiGuncelle.emit()
        if self.sahneAktifNesne:
            if self.sahneAktifNesne.type() == shared.VIDEO_ITEM_TYPE:
                return self.sahneAktifNesne
        return None

    # ---------------------------------------------------------------------
    def satir_sec(self, satir):
        # TODO: aynı zamanda videoyu da sec, secili degilse
        self.altyaziTW.selectRow(satir)

    # ---------------------------------------------------------------------
    def tiklanan_altyazi_zamanina_git(self, nesne):
        # self.dongude = False
        videoNesne = self.videoNesnesi()
        if videoNesne:
            if videoNesne.altyazilarSozluk[videoNesne.simdikiAltyazi][0]:
                videoNesne.altyazi_sira_bul(videoNesne.player.position())
            # print(nesne.data(Qt.ItemDataRole.UserRole))
            # print(videoNesne.player.position())
            videoNesne.player_set_position(nesne.data(Qt.ItemDataRole.UserRole))

    # ---------------------------------------------------------------------
    def tasinanSatirlariYaziyaCevir(self):
        secilenIndexler = self.altyaziTW.selectionModel().selectedRows()
        yazi = ""
        for satirIdx in secilenIndexler:
            yazi = f"{yazi}\n{self.altyaziTW.item(satirIdx.row(), 1).text()}"
        return yazi

    # ---------------------------------------------------------------------
    def altyazi_degistir_cbox(self, idx):
        # print(self.altyaziCBox.itemText(idx))
        # print(self.altyaziCBox.itemData(idx))
        videoNesne = self.videoNesnesi()
        if not videoNesne.simdikiAltyazi == self.altyaziCBox.currentData():
            videoNesne.simdikiAltyazi = self.altyaziCBox.currentData()
            self.altyazilari_guncelle()

    # ---------------------------------------------------------------------
    def altyazi_yukle(self):
        videoNesne = self.videoNesnesi()
        if videoNesne:

            self.sonKlasorVideolarGuncelle.emit()
            filtre = self.tr("srt Files (*.srt);;All Files(*)")
            # filtre = self.tr("srt Files (*.srt);;webvtt Files (*.vtt);;All Files(*)")
            fn = QFileDialog.getOpenFileNames(self,
                                              self.tr("Open Subtitle Files..."),
                                              self.sonKlasorVideolar,
                                              filtre
                                              )
            # if fn:
            if fn[0]:
                altyaziAdresleri = fn[0]
                # altyaziAdres = altyaziAdresleri[0]
                t1 = time.time()
                videoNesne.altyazi_hesapla(altyaziAdresleri)
                self.log.emit(self.tr(f'Subtitles succesfully loaded!  -  {time.time() - t1:.2f} s'))
                self.sonKlasorVideolar = os.path.dirname(altyaziAdresleri[0])
        else:
            self.log.emit(self.tr("Please select a video item"))

    # ---------------------------------------------------------------------
    def altyazilari_guncelle(self):
        videoNesne = self.videoNesnesi()
        if videoNesne:
            self.altyaziCBox.clear()
            for altyaziAdres in videoNesne.altyazilarSozluk:
                self.altyaziCBox.addItem(os.path.basename(altyaziAdres), altyaziAdres)

            self.altyaziTW.clear()
            self.altyaziTW.setRowCount(len(videoNesne.altyazilarSozluk[videoNesne.simdikiAltyazi][0]))
            i = 0
            # altYaziBaslamaZamanlari , altYaziBitisZamanlari
            for pos_ms, altyazi in zip(videoNesne.altyazilarSozluk[videoNesne.simdikiAltyazi][0],
                                       videoNesne.altyazilarSozluk[videoNesne.simdikiAltyazi][1]):
                dk, sn = divmod((pos_ms // 1000), 60)
                saat, dk = divmod(dk, 60)
                nesne = QTableWidgetItem(f"{saat:02}:{dk:02}:{sn:02}")
                nesne.setData(Qt.ItemDataRole.UserRole, pos_ms)
                self.altyaziTW.setItem(i, 0, nesne)
                nesne = QTableWidgetItem(altyazi)
                nesne.setData(Qt.ItemDataRole.UserRole, pos_ms)
                self.altyaziTW.setItem(i, 1, nesne)
                i += 1

        self.altyaziTW.resizeColumnsToContents()
        self.altyaziTW.resizeRowsToContents()
        self.donguSecilenSatirIndexleri = []
