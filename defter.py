# -*- coding: utf-8 -*-
# .

# الحمد لله

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '25/03/16'
__license__ = 'GPLv3'

import sys
import os
import subprocess
import locale
import operator
import time
import filecmp
import zipfile
# import time
import shutil
import tempfile
import platform
from collections import deque

# from PySide6.QtOpenGL import QGLWidget

from PySide6.QtGui import (QCursor, QKeySequence, QIcon, QPixmap, QColor, QPen, QFont, QPainter, QPainterPath,
                           QImageReader, QImage, QPixmapCache, QTextCharFormat, QTextCursor, QPalette, QTextListFormat,
                           QTextBlockFormat, QPageSize, QPageLayout, QAction, QActionGroup, QUndoGroup, QUndoStack,
                           QShortcut)
from PySide6.QtWebEngineCore import QWebEngineSettings  # , QWebEngineProfile, QWebEnginePage

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication,
                               QFileDialog, QToolBar, QMenuBar, QMenu, QColorDialog, QMessageBox,
                               QStatusBar, QSizePolicy, QLabel, QPushButton, QScrollArea,
                               QDialog, QTextEdit, QInputDialog, QListWidget, QListWidgetItem,
                               QLineEdit, QToolButton, QComboBox, QButtonGroup, QGroupBox, QRadioButton, QProgressBar,
                               QCheckBox)

from PySide6.QtCore import (Qt, QRectF, QCoreApplication, QSettings, QPoint, Slot, QSizeF, QSize, QFile, QSaveFile,
                            QIODevice, QDataStream, QMimeData, QByteArray, QPointF, qCompress, qUncompress, QLocale,
                            QThread, QUrl, QLineF, QObject, QRect, QTimer, QDir)

from PySide6.QtWebEngineWidgets import QWebEngineView

from PySide6.QtPrintSupport import QPrinter, QPrinterInfo
from canta import shared
from canta.dockWidget import DockWidget
from canta.nesneOzellikleriYuzenWidget import NesneOzellikleriYuzenWidget
from canta.printPreviewDialog import PrintPreviewDialog
from canta.renkSecici import RenkSeciciWidget
from canta.scene import Scene
from canta.view import View
from canta.ekranKutuphane import EkranKutuphane
from canta.sahneKutuphane import SahneKutuphane
from canta.tabWidget import TabWidget
from canta.tabBar import TabBar
from canta.spinBoxlar import SpinBox, SpinBoxForRotation
from canta.sliderDoubleWithDoubleSpinBox import SliderDoubleWithDoubleSpinBox
from canta.komutPenceresi import CommandDialog
from canta.nesneler.base import BaseItem
from canta.nesneler.ellipse import Ellipse
from canta.nesneler.image import Image
from canta.nesneler.path import PathItem
from canta.nesneler.line import LineItem
from canta.nesneler.rect import Rect
from canta.nesneler.text import Text
from canta.nesneler.video import VideoItem
from canta.nesneler.group import Group
from canta.nesneler.dosya import DosyaNesnesi
from canta.comboBox import ComboBox
from canta.fontComboBox import FontComboBox
# from canta.ozelliklerAcilirMenu import OzelliklerAcilirMenu
from canta.nesneler.web import Web
# from canta.syntaxHighlighter import HtmlHighlighter
from canta.listWidgetItem import ListWidgetItem, ListWidgetItemDelegate
from canta.threadWorkers import DownloadWorker
from canta.htmlParsers import ImgSrcParser
from canta.treeView import TreeView
from canta.treeSayfa import Sayfa
from canta.pushButton import PushButton, PushButtonRenk
from canta.yuzenWidget import YuzenWidget
from canta.with_signals_updates_blocked import signals_blocked_and_updates_disabled as signals_updates_blocked, \
    signals_blocked
import canta.icons_rc

from canta import undoRedoFonksiyolar as undoRedo

from canta.ekranGoruntusu.secilen_bolge_comp_manager_on import TamEkranWidget_CM_On
from canta.ekranGoruntusu.secilen_bolge_comp_manager_off import TamEkranWidget_CM_Off

# DEFTER_SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

VERSION = "(v0.9)"
DEF_MAGIC_NUMBER = 25032016
DEF_FILE_VERSION = 1
DEFSTYLES_MAGIC_NUMBER = 13132017
DEFSTYLES_FILE_VERSION = 1


# def get_cursor_pos(item):
#     # Get mouse position relative to this item
#     cursor_pos = item.scene().parent().mapFromGlobal(QCursor.pos())
#     cursor_pos = item.scene().views()[0].mapToScene(cursor_pos)
#     cursor_pos = item.mapFromScene(cursor_pos)
#     return cursor_pos


########################################################################
class DefterAnaPencere(QMainWindow):

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(DefterAnaPencere, self).__init__(parent)

        self.setWindowTitle("Defter")
        # self.ekran_cozunurluk = QApplication.primaryScreen().availableGeometry()
        # self.resize(self.ekran_cozunurluk.size().width(), self.ekran_cozunurluk.size().height()-50)
        self.resize(1024, 740)

        self.dpi = QApplication.primaryScreen().physicalDotsPerInch()

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_data_changed)

        self.supportedImageFormatList = []
        for formatAsQByte in QImageReader.supportedImageFormats():
            self.supportedImageFormatList.append(str(formatAsQByte, 'ascii'))

        # TODO: options=QFileDialog.DontUseNativeDialog
        # TODO: su anda JPEG, PNG gibi buyuk harfli dosyalari bir gtk bugindan dolayi gormuyor,
        # TODO: ya native dialog kullanmayacagiz, ya bunlari ekleyecegiz listeye, ya da AllFiles ekleyecegiz..
        # TODO: ya da gtk theme kullaniliyorsa nativedegil veya hangi cozum kullanildi ise yoksa native ac gibi..
        # TODO: şimdilik All Files ekliyoruz.
        self.supportedImageFormats = self.tr("Image Files ")
        for imgFormat in self.supportedImageFormatList:
            self.supportedImageFormats = "{}{}".format(self.supportedImageFormats, "*.{} ".format(imgFormat))
        self.supportedImageFormats = self.supportedImageFormats.rstrip()
        _ = self.tr(";;All files(*)")
        self.supportedImageFormats = "{}{}".format(self.supportedImageFormats, _)

        self.recentFilesQueue = deque(maxlen=15)

        self.theme = None

        # oku_kullanici_ayarlari icinde tekrar atamalar yapiliyor
        self.baskiCerceveRengi = QColor(0, 0, 0)

        self.karakter_bicimi_sozluk = {"b": False,
                                       "i": False,
                                       "u": False,
                                       "s": False,
                                       "o": False,
                                       }

        self.itemSize = QSizeF(25, 25)

        # TODO: self.textSize iptal edilebilir . font uzerinden devam edilebilir.
        self.textSize = 10

        self.yazi_hizasi = Qt.AlignLeft

        self.printer = None
        self._get_printer()

        self.undoGroup = QUndoGroup(self)

        # clean_mode icin
        self.state_before_clean_mode = None

        self.imlec_arac = None

        self.olustur_ayarlar()
        self.oku_kullanici_ayarlari()
        self.olustur_sayfalarDW()
        self.olustur_tab_widget()
        self.olustur_kutuphaneDW()

        self.olustur_tools_toolbar()
        self.olustur_properties_toolbar()
        self.olustur_cizgi_ozellikleri_toolbar()
        self.olustur_font_toolbar()
        self.olustur_renk_toolbar()
        self.olustur_align_toolbar()
        self.olustur_menu_bar()
        self.olustur_utilities_toolbar()
        self.olustur_status_bar()
        self.olustur_item_context_menus_and_actions()
        self.olustur_dummy_widget_for_actions()

        self.ekle_hotkeys()

        self.olustur_nesne_ozellikleriDW()
        self.olustur_nesne_ozellikleriYW()
        self.olustur_stillerDW()
        self.olustur_stillerYW()
        self.olustur_sahneye_baski_siniri_cizim_ayarlari()
        self.arsivleme_programi_adres_belirle()

        self.act_switch_to_selection_tool()

        self.oku_arayuz_ayarlari()
        # self.actionAlwaysOnTopToggle u , read_gui_settingste sinyalleri block ederek set ediyoruz.
        # etmezsek ustuste iki tane show oluyor, ilk acılıs harici, daha settings olusmadigindan ilk acilista da
        # eger burdaki self.show() u kaldirisak ilk acilista acilmiyor, dolayisi ile boyle bir workaround
        # aslında ust uste iki tane show olsa da ne olacak bi sorun yok da,
        if self.actionAlwaysOnTopToggle.isChecked():
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        self.cScene.setSceneRect(self.cView.get_visible_rect())

        # self.pixmapCache = QPixmapCache()

        # QPixmapCache.setCacheLimit(1024000)  # 1 GB
        QPixmapCache.setCacheLimit(524288)  # 512 MB

        # this is for text item's "Localize HTML" action
        self.is_fetching = False

        # self.logViewerDialog = None
        # self.logCounter = 0
        self.olustur_log_viewer_dialog()

        # import os
        # import psutil
        # process = psutil.Process(os.getpid())
        # print(process.memory_info().rss)

    #     self.print_shortcuts()
    #
    # # ---------------------------------------------------------------------
    # def print_shortcuts(self):
    #     for item in self.findChildren(QAction):
    #         # print(item.parent().text())
    #         print(item.text()," --> ",item.shortcut().toString())

    # ---------------------------------------------------------------------
    def setCursor(self, cursor, gecici_mi=False):
        if not gecici_mi:
            self.imlec_arac = cursor
        super(DefterAnaPencere, self).setCursor(cursor)

    # ---------------------------------------------------------------------
    def olustur_nesne_ozellikleriDW(self):

        self.nesneOzellikleriDW = DockWidget(self.tr("Item & Tool Properties"), self)
        self.nesneOzellikleriDW.setObjectName("nesneOzellikleriDW")
        # self.nesneOzellikleriDW.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.nesneOzellikleriDW)

        # -- her ada nın cevresine bir onu kaplayici ve margini ayarlanabilir bir cember veya kutu

        self.nesneOzellikleriDWScroll = QScrollArea()
        # self.nesneOzellikleriDWScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.nesneOzellikleriDWScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nesneOzellikleriDWScroll.setWidgetResizable(True)
        # self.nesneOzellikleriDWScroll.setBackgroundRole(QPalette.Dark)
        self.nesneOzellikleriDW.setWidget(self.nesneOzellikleriDWScroll)
        # scrollLayout = QVBoxLayout(self.nesneOzellikleriDWScroll)

        self.nesneOzellikleriDWBaseWidget = QWidget(self.nesneOzellikleriDWScroll)
        # self.nesneOzellikleriDW.setWidget(self.nesneOzellikleriDWBaseWidget)
        anaLay = QVBoxLayout(self.nesneOzellikleriDWBaseWidget)
        # anaLay.setSizeConstraint(QVBoxLayout.SetFixedSize)
        # anaLay.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        anaLay.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        # anaLay.setSizeConstraint(QVBoxLayout.SetMaximumSize)
        # anaLay.setContentsMargins(0,0,0,0)
        # self.nesneOzellikleriDW.setContentsMargins(0, 0, 0, 0)
        # self.nesneOzellikleriDWBaseWidget.setContentsMargins(0,0,0,0)
        # scrollLayout.addWidget(self.nesneOzellikleriDWBaseWidget)
        self.nesneOzellikleriDWScroll.setWidget(self.nesneOzellikleriDWBaseWidget)
        # self.nesneOzellikleriDWScroll.setLayout(layout)

        self.nesneGrupW = QWidget(self.nesneOzellikleriDWBaseWidget)
        nesneLay = QVBoxLayout(self.nesneGrupW)
        nesneLay.setContentsMargins(0, 0, 0, 0)
        self.yaziGrupW = QWidget(self.nesneOzellikleriDWBaseWidget)
        yaziLay = QVBoxLayout(self.yaziGrupW)
        yaziLay.setContentsMargins(0, 0, 0, 0)
        self.cizgiGrupW = QWidget(self.nesneOzellikleriDWBaseWidget)
        cizgiLay = QVBoxLayout(self.cizgiGrupW)
        cizgiLay.setContentsMargins(0, 0, 0, 0)

        #######################################################################
        #######################################################################
        self.itemWidthSBox_nesnedw = SpinBox(self.nesneGrupW)
        self.itemWidthSBox_nesnedw.setSuffix(" w")
        self.itemWidthSBox_nesnedw.setMinimum(1)
        self.itemWidthSBox_nesnedw.setMaximum(99999)
        self.itemWidthSBox_nesnedw.setSingleStep(1)
        self.itemWidthSBox_nesnedw.setValue(int(self.itemSize.width()))
        self.itemWidthSBox_nesnedw.setToolTip(self.tr("Width"))
        self.itemWidthSBox_nesnedw.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_item_width)
        self.itemWidthSBox_nesnedw.valueChanged.connect(self.itemWidthSBox_tbar.setValue)
        # ilk acilista burasi daha sonra cagriliyor o yuzden burda itemRotationSBox_tbar baglantilarini yapiyoruz
        self.itemWidthSBox_tbar.valueChanged.connect(self.itemWidthSBox_nesnedw.setValue)

        self.itemHeightSBox_nesnedw = SpinBox(self.nesneGrupW)
        self.itemHeightSBox_nesnedw.setSuffix(" h")
        self.itemHeightSBox_nesnedw.setMinimum(1)
        self.itemHeightSBox_nesnedw.setMaximum(99999)
        self.itemHeightSBox_nesnedw.setSingleStep(1)
        self.itemHeightSBox_nesnedw.setValue(int(self.itemSize.height()))
        self.itemHeightSBox_nesnedw.setToolTip(self.tr("Height"))
        self.itemHeightSBox_nesnedw.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_item_height)
        self.itemHeightSBox_nesnedw.valueChanged.connect(self.itemHeightSBox_tbar.setValue)
        # ilk acilista burasi daha sonra cagriliyor o yuzden burda itemHeightSBox_tbar baglantilarini yapiyoruz
        self.itemHeightSBox_tbar.valueChanged.connect(self.itemHeightSBox_nesnedw.setValue)

        self.itemRotationSBox_nesnedw = SpinBoxForRotation(self.nesneGrupW)
        self.itemRotationSBox_nesnedw.setSuffix(u"\u00b0")
        self.itemRotationSBox_nesnedw.setValue(0)
        self.itemRotationSBox_nesnedw.setMinimum(-1)
        self.itemRotationSBox_nesnedw.setMaximum(360)
        self.itemRotationSBox_nesnedw.setSingleStep(1)
        self.itemRotationSBox_nesnedw.setToolTip(self.tr("Rotation"))
        self.itemRotationSBox_nesnedw.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_item_rotation)
        self.itemRotationSBox_nesnedw.valueChanged.connect(self.itemRotationSBox_tbar.setValue)
        # ilk acilista burasi daha sonra cagriliyor o yuzden burda itemRotationSBox_tbar baglantilarini yapiyoruz
        self.itemRotationSBox_tbar.valueChanged.connect(self.itemRotationSBox_nesnedw.setValue)

        boyutLay = QHBoxLayout()

        boyutLay.addWidget(self.itemWidthSBox_nesnedw)
        boyutLay.addWidget(self.itemHeightSBox_nesnedw)
        boyutLay.addWidget(self.itemRotationSBox_nesnedw)
        # ---------------------------------------------------------------------

        self.nesneArkaplanRengiBtn = PushButtonRenk("", 36, 36, self.cScene.aktifArac.arkaPlanRengi, self.nesneGrupW)
        self.nesneArkaplanRengiBtn.clicked.connect(self.act_set_item_background_color)

        renklerDisLay = QHBoxLayout()
        renklerSatirlarLay = QVBoxLayout()
        renklerSatir1Lay = QHBoxLayout()
        renklerSatir2Lay = QHBoxLayout()

        self.nesne_arkaplan_rengi_btn_liste = []

        for i in range(8):
            btn = self.ver_renk_palet_buton(tip="a", gen=15, yuk=15,
                                            renk=self.nesne_arkaplan_rengi_btn_liste_acilis_renkleri[i],
                                            parent=self.nesneGrupW)
            renklerSatir1Lay.addWidget(btn)

            self.nesne_arkaplan_rengi_btn_liste.append(btn)

        for i in range(8, 16):
            btn = self.ver_renk_palet_buton(tip="a", gen=15, yuk=15,
                                            renk=self.nesne_arkaplan_rengi_btn_liste_acilis_renkleri[i],
                                            parent=self.nesneGrupW)
            renklerSatir2Lay.addWidget(btn)

            self.nesne_arkaplan_rengi_btn_liste.append(btn)

        renklerSatirlarLay.addLayout(renklerSatir1Lay)
        renklerSatirlarLay.addLayout(renklerSatir2Lay)
        renklerDisLay.addWidget(self.nesneArkaplanRengiBtn)
        renklerDisLay.addLayout(renklerSatirlarLay)
        renklerDisLay.addStretch()

        nesneLay.addLayout(renklerDisLay)
        nesneLay.addSpacing(5)
        nesneLay.addLayout(boyutLay)
        nesneLay.addStretch()
        #######################################################################
        #######################################################################
        # ---------------------------------------------------------------------
        self.fontCBox_yazidw = FontComboBox(self.yaziGrupW)
        # self.fontCBox_yazidw.activated[str].connect(self.act_set_current_font)
        # self.fontCBox_yazidw.currentFontChanged.connect(self.set_text_family)
        # self.fontCBox_yazidw.currentIndexChanged.connect(self.act_change_font)
        self.fontCBox_yazidw.setMaximumWidth(203)
        self.fontCBox_yazidw.setCurrentFont(self.currentFont)
        self.fontCBox_yazidw.valueChangedFromFontComboBoxGuiNotByCode.connect(self.act_set_current_font)
        self.fontCBox_yazidw.currentFontChanged.connect(self.fontCBox_tbar.setCurrentFont)
        # bu metod daha sonra cagrildigi ve fontCBox_yazidw daha sonra olusturuldugu icin
        # fontCBox_tbar atamasini burda yapiyoruz.
        self.fontCBox_tbar.currentFontChanged.connect(self.fontCBox_yazidw.setCurrentFont)

        self.textSizeSBox_yazidw = SpinBox(self.yaziGrupW)
        self.textSizeSBox_yazidw.setSuffix(" pt")
        self.textSizeSBox_yazidw.setValue(self.textSize)
        self.textSizeSBox_yazidw.setMaximumWidth(85)
        self.textSizeSBox_yazidw.setMinimum(5)
        self.textSizeSBox_yazidw.setMaximum(999)
        self.textSizeSBox_yazidw.setSingleStep(1)
        # self.textSizeSBox_yazidw.valueChanged[int].connect(self.act_change_item_size)
        self.textSizeSBox_yazidw.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_text_size)
        self.textSizeSBox_yazidw.valueChanged.connect(self.textSizeSBox_tbar.setValue)
        # bu metod daha sonra cagrildigi ve textSizeSBox_yazidw daha sonra olusturuldugu icin
        # textSizeSBox_tbar atamasini burda yapiyoruz.
        self.textSizeSBox_tbar.valueChanged.connect(self.textSizeSBox_yazidw.setValue)
        self.textSizeSBox_yazidw.setToolTip(self.tr("Text Size"))

        self.yaziListeBicimiCBox = QComboBox(self.yaziGrupW)
        self.yaziListeBicimiCBox.setMaximumWidth(135)
        self.yaziListeBicimiCBox.addItem(self.tr("Standard"))
        self.yaziListeBicimiCBox.addItem(self.tr("Bullet List (Disc)"))
        self.yaziListeBicimiCBox.addItem(self.tr("Bullet List (Circle)"))
        self.yaziListeBicimiCBox.addItem(self.tr("Bullet List (Square)"))
        self.yaziListeBicimiCBox.addItem(self.tr("Ordered List (Decimal)"))
        self.yaziListeBicimiCBox.addItem(self.tr("Ordered List (Alpha lower)"))
        self.yaziListeBicimiCBox.addItem(self.tr("Ordered List (Alpha upper)"))
        self.yaziListeBicimiCBox.addItem(self.tr("Ordered List (Roman lower)"))
        self.yaziListeBicimiCBox.addItem(self.tr("Ordered List (Roman upper)"))
        self.yaziListeBicimiCBox.activated.connect(self.act_set_text_style)

        # self.yaziListeBicmiAction = self.fontToolBar.addWidget(self.yaziListeBicimiCBox)

        # ---------------------------------------------------------------------
        self.yaziRengiBtn = PushButtonRenk("", 36, 36, self.cScene.aktifArac.yaziRengi, self.yaziGrupW)
        self.yaziRengiBtn.clicked.connect(self.act_set_item_text_color)

        renklerDisLay = QHBoxLayout()
        renklerSatirlarLay = QVBoxLayout()
        renklerSatir1Lay = QHBoxLayout()
        renklerSatir2Lay = QHBoxLayout()

        self.yazi_rengi_btn_liste = []

        for i in range(8):
            btn = self.ver_renk_palet_buton(tip="y", gen=15, yuk=15, renk=self.yazi_rengi_btn_liste_acilis_renkleri[i],
                                            parent=self.yaziGrupW)
            renklerSatir1Lay.addWidget(btn)

            self.yazi_rengi_btn_liste.append(btn)

        for i in range(8, 16):
            btn = self.ver_renk_palet_buton(tip="y", gen=15, yuk=15, renk=self.yazi_rengi_btn_liste_acilis_renkleri[i],
                                            parent=self.yaziGrupW)
            renklerSatir2Lay.addWidget(btn)

            self.yazi_rengi_btn_liste.append(btn)

        renklerSatirlarLay.addLayout(renklerSatir1Lay)
        renklerSatirlarLay.addLayout(renklerSatir2Lay)
        renklerDisLay.addWidget(self.yaziRengiBtn)
        renklerDisLay.addLayout(renklerSatirlarLay)
        renklerDisLay.addStretch()

        self.btnBold = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnBold.setIcon(QIcon(':icons/bold.png'))
        self.btnBold.setFlat(True)
        self.btnBold.setCheckable(True)
        self.btnBold.clicked.connect(lambda: self.act_bold(from_button=True))

        self.btnItalic = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnItalic.setIcon(QIcon(':icons/italic.png'))
        self.btnItalic.setFlat(True)
        self.btnItalic.setCheckable(True)
        self.btnItalic.clicked.connect(lambda: self.act_italic(from_button=True))

        self.btnUnderline = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnUnderline.setIcon(QIcon(':icons/underline.png'))
        self.btnUnderline.setFlat(True)
        self.btnUnderline.setCheckable(True)
        self.btnUnderline.clicked.connect(lambda: self.act_underline(from_button=True))

        self.btnStrikeOut = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnStrikeOut.setIcon(QIcon(':icons/strikeout.png'))
        self.btnStrikeOut.setFlat(True)
        self.btnStrikeOut.setCheckable(True)
        self.btnStrikeOut.clicked.connect(lambda: self.act_strikeout(from_button=True))

        self.btnOverline = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnOverline.setIcon(QIcon(':icons/overline.png'))
        self.btnOverline.setFlat(True)
        self.btnOverline.setCheckable(True)
        self.btnOverline.clicked.connect(lambda: self.act_overline(from_button=True))

        btnKaratkerBicimleriLay = QHBoxLayout()
        btnKaratkerBicimleriLay.addWidget(self.btnBold)
        btnKaratkerBicimleriLay.addWidget(self.btnItalic)
        btnKaratkerBicimleriLay.addWidget(self.btnUnderline)
        btnKaratkerBicimleriLay.addWidget(self.btnStrikeOut)
        btnKaratkerBicimleriLay.addWidget(self.btnOverline)
        btnKaratkerBicimleriLay.addStretch()

        grp = QButtonGroup(self.yaziGrupW)
        grp.buttonClicked.connect(self.act_yazi_hizala_btn)

        self.btnYaziHizalaSola = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnYaziHizalaSola.setIcon(
            QIcon.fromTheme('format-justify-left', QIcon(':icons/icons/format-justify-left.png')))
        self.btnYaziHizalaSola.setFlat(True)
        self.btnYaziHizalaSola.setCheckable(True)

        self.btnYaziHizalaOrtala = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnYaziHizalaOrtala.setIcon(
            QIcon.fromTheme('format-justify-center', QIcon(':icons/icons/format-justify-center.png')))
        self.btnYaziHizalaOrtala.setFlat(True)
        self.btnYaziHizalaOrtala.setCheckable(True)

        self.btnYaziHizalaSaga = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnYaziHizalaSaga.setIcon(
            QIcon.fromTheme('format-justify-right', QIcon(':icons/icons/format-justify-right.png')))
        self.btnYaziHizalaSaga.setFlat(True)
        self.btnYaziHizalaSaga.setCheckable(True)

        self.btnYaziHizalaSigdir = PushButton("", 16, 16, parent=self.yaziGrupW)
        self.btnYaziHizalaSigdir.setIcon(
            QIcon.fromTheme('format-justify-fill', QIcon(':icons/icons/format-justify-fill.png')))
        self.btnYaziHizalaSigdir.setFlat(True)
        self.btnYaziHizalaSigdir.setCheckable(True)

        grp.addButton(self.btnYaziHizalaSola)
        grp.addButton(self.btnYaziHizalaOrtala)
        grp.addButton(self.btnYaziHizalaSaga)
        grp.addButton(self.btnYaziHizalaSigdir)

        btnHizalaLay = QHBoxLayout()
        btnHizalaLay.addWidget(self.btnYaziHizalaSola)
        btnHizalaLay.addWidget(self.btnYaziHizalaOrtala)
        btnHizalaLay.addWidget(self.btnYaziHizalaSaga)
        btnHizalaLay.addWidget(self.btnYaziHizalaSigdir)
        btnHizalaLay.addStretch()

        btnBicimlerLay = QHBoxLayout()
        btnBicimlerLay.addLayout(btnKaratkerBicimleriLay)
        btnBicimlerLay.addSpacing(10)
        btnBicimlerLay.addLayout(btnHizalaLay)
        btnBicimlerLay.addStretch(1)

        lay = QHBoxLayout()
        lay.addWidget(self.textSizeSBox_yazidw)
        lay.addWidget(self.yaziListeBicimiCBox)
        lay.addStretch()

        yaziLay.addLayout(renklerDisLay)
        yaziLay.addSpacing(5)
        yaziLay.addLayout(btnBicimlerLay)
        yaziLay.addSpacing(5)
        yaziLay.addWidget(self.fontCBox_yazidw)
        yaziLay.addSpacing(5)
        yaziLay.addLayout(lay)
        yaziLay.addStretch()
        #######################################################################
        #######################################################################

        # ---------------------------------------------------------------------
        # def olustur_cizgi_ozellikleriDW(self):
        # ---------------------------------------------------------------------
        # ---- cizgi tipi -----------------------------------------------------------------
        cizgiTipiLabel = QLabel(self.tr("Line Type"), self.cizgiGrupW)
        cizgiTipiLabel.setFixedWidth(67)
        self.cizgiTipiCBox = ComboBox(self.cizgiGrupW)
        self.cizgiTipiCBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cizgiTipiCBox.setIconSize(QSize(100, 15))
        self.cizgiTipiCBox.addItem(self.tr("      No Line"), userData=Qt.NoPen)
        self.cizgiTipiCBox.addItem(QIcon(':icons/line_solid.png'), "", userData=Qt.SolidLine)
        self.cizgiTipiCBox.addItem(QIcon(':icons/line_dotted.png'), "", userData=Qt.DotLine)
        self.cizgiTipiCBox.addItem(QIcon(':icons/line_dashed.png'), "", userData=Qt.DashLine)
        self.cizgiTipiCBox.addItem(QIcon(':icons/line_dash_dot.png'), "", userData=Qt.DashDotLine)
        self.cizgiTipiCBox.addItem(QIcon(':icons/line_dash_dot_dot.png'), "", userData=Qt.DashDotDotLine)
        self.cizgiTipiCBox.setCurrentIndex(1)
        # self.cizgiTipiCBox.activated.connect(self.act_cizgi_tipi_degistir)
        self.cizgiTipiCBox.currentIndexChangedFromComboBoxGuiNotBySetCurrentIndex[int].connect(
            lambda x: self.act_cizgi_tipi_degistir(self.cizgiTipiCBox.itemData(x, Qt.UserRole)))

        cizgiTipiLayout = QHBoxLayout()
        cizgiTipiLayout.addWidget(cizgiTipiLabel)
        cizgiTipiLayout.addWidget(self.cizgiTipiCBox)

        # ---- cizgi birlesim tipi -----------------------------------------------------------------
        cizgiBirlesimTipiLabel = QLabel(self.tr("Join Style"), self.cizgiGrupW)
        cizgiBirlesimTipiLabel.setFixedWidth(67)
        self.cizgiBirlesimTipiCBox = ComboBox(self.cizgiGrupW)
        self.cizgiBirlesimTipiCBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cizgiBirlesimTipiCBox.addItem(QIcon(':icons/line_solid.png'), self.tr("Round"),
                                           userData=Qt.RoundJoin)  # Yuvarlak
        self.cizgiBirlesimTipiCBox.addItem(QIcon(':icons/line_solid.png'), self.tr("Miter"),
                                           userData=Qt.MiterJoin)  # Sivri
        self.cizgiBirlesimTipiCBox.addItem(QIcon(':icons/line_solid.png'), self.tr("Bevel"),
                                           userData=Qt.BevelJoin)  # Kırpık
        self.cizgiBirlesimTipiCBox.currentIndexChangedFromComboBoxGuiNotBySetCurrentIndex[int].connect(
            lambda x: self.act_cizgi_birlesim_tipi_degistir(self.cizgiBirlesimTipiCBox.itemData(x, Qt.UserRole)))

        cizgiBirlesimTipiLayout = QHBoxLayout()
        cizgiBirlesimTipiLayout.addWidget(cizgiBirlesimTipiLabel)
        cizgiBirlesimTipiLayout.addWidget(self.cizgiBirlesimTipiCBox)

        # ---- cizgi ucu tipi -----------------------------------------------------------------
        cizgiUcuTipiLabel = QLabel(self.tr("Cap Style"), self.cizgiGrupW)
        cizgiUcuTipiLabel.setFixedWidth(67)
        self.cizgiUcuTipiCBox = ComboBox(self.cizgiGrupW)
        self.cizgiUcuTipiCBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cizgiUcuTipiCBox.addItem(QIcon(':icons/line_solid.png'), self.tr("Flat"), userData=Qt.FlatCap)
        self.cizgiUcuTipiCBox.addItem(QIcon(':icons/line_solid.png'), self.tr("Square"), userData=Qt.SquareCap)
        self.cizgiUcuTipiCBox.addItem(QIcon(':icons/line_solid.png'), self.tr("Round"), userData=Qt.RoundCap)
        self.cizgiUcuTipiCBox.currentIndexChangedFromComboBoxGuiNotBySetCurrentIndex[int].connect(
            lambda x: self.act_cizgi_ucu_tipi_degistir(self.cizgiUcuTipiCBox.itemData(x, Qt.UserRole)))

        cizgiUcuTipiLayout = QHBoxLayout()
        cizgiUcuTipiLayout.addWidget(cizgiUcuTipiLabel)
        cizgiUcuTipiLayout.addWidget(self.cizgiUcuTipiCBox)

        # ---- cizgi kalinligi -----------------------------------------------------------------
        self.cizgiKalinligiDSliderWithDSBox = SliderDoubleWithDoubleSpinBox(yerlesim=Qt.Horizontal,
                                                                            parent=self.cizgiGrupW)
        # self.cizgiKalinligiSBox.setSuffix(" h")
        self.cizgiKalinligiDSliderWithDSBox.setMinimum(0)
        self.cizgiKalinligiDSliderWithDSBox.setMaximum(100)
        self.cizgiKalinligiDSliderWithDSBox.setSingleStep(0.1)
        self.cizgiKalinligiDSliderWithDSBox.setValue(self.cScene.aktifArac.cizgiKalinligi * 10)
        # self.cizgiKalinligiSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_item_height)
        self.cizgiKalinligiDSliderWithDSBox.setToolTip(self.tr("Line Width"))

        self.cizgiKalinligiDSliderWithDSBox.degerDegisti.connect(self.act_cizgi_kalinligi_degistir)

        self.cizgiKalinligiDSliderWithDSBox.degerDegisti.connect(
            lambda x: self.cizgiKalinligiDSliderWithDSBox_tbar.setValue(x * 10))
        self.cizgiKalinligiDSliderWithDSBox_tbar.degerDegisti.connect(
            lambda x: self.cizgiKalinligiDSliderWithDSBox.setValue(x * 10))

        cizgiOzellikleriniSifirlaBtn = QPushButton(self.tr("Reset"), self.cizgiGrupW)
        cizgiOzellikleriniSifirlaBtn.clicked.connect(self.act_cizgi_ozelliklerini_sifirla)

        self.cizgiRengiBtn = PushButtonRenk("", 36, 36, self.cScene.aktifArac.cizgiRengi, self.cizgiGrupW)
        self.cizgiRengiBtn.clicked.connect(self.act_set_item_line_color)

        renklerDisLay = QHBoxLayout()
        renklerSatirlarLay = QVBoxLayout()
        renklerSatir1Lay = QHBoxLayout()
        renklerSatir2Lay = QHBoxLayout()

        self.cizgi_rengi_btn_liste = []

        for i in range(8):
            btn = self.ver_renk_palet_buton(tip="c", gen=15, yuk=15, renk=self.cizgi_rengi_btn_liste_acilis_renkleri[i],
                                            parent=self.cizgiGrupW)
            renklerSatir1Lay.addWidget(btn)

            self.cizgi_rengi_btn_liste.append(btn)

        for i in range(8, 16):
            btn = self.ver_renk_palet_buton(tip="c", gen=15, yuk=15, renk=self.cizgi_rengi_btn_liste_acilis_renkleri[i],
                                            parent=self.cizgiGrupW)

            renklerSatir2Lay.addWidget(btn)

            self.cizgi_rengi_btn_liste.append(btn)

        cizgiLay.addLayout(renklerDisLay)
        cizgiLay.addSpacing(5)
        cizgiLay.addWidget(self.cizgiKalinligiDSliderWithDSBox)
        cizgiLay.addLayout(cizgiTipiLayout)
        cizgiLay.addLayout(cizgiBirlesimTipiLayout)
        cizgiLay.addLayout(cizgiUcuTipiLayout)
        cizgiLay.addWidget(cizgiOzellikleriniSifirlaBtn)
        cizgiLay.addStretch()
        # anaLay.addStretch()

        renklerSatirlarLay.addLayout(renklerSatir1Lay)
        renklerSatirlarLay.addLayout(renklerSatir2Lay)
        renklerDisLay.addWidget(self.cizgiRengiBtn)
        renklerDisLay.addLayout(renklerSatirlarLay)
        renklerDisLay.addStretch()

        # Renk Secici
        # ---------------------------------------------------------------------
        self.radioBtnGroup = QButtonGroup(self)
        self.radioArkaplan = QRadioButton(self.tr("Background"), self)
        self.radioYazi = QRadioButton(self.tr("Text"), self)
        self.radioCizgi = QRadioButton(self.tr("Line && Pen"), self)
        self.radioBtnGroup.addButton(self.radioArkaplan)
        self.radioBtnGroup.addButton(self.radioYazi)
        self.radioBtnGroup.addButton(self.radioCizgi)
        self.radioArkaplan.setChecked(True)
        self.renk_tipi = "a"
        self.nesneGrupW.show()
        self.yaziGrupW.hide()
        self.cizgiGrupW.hide()
        radioLay = QHBoxLayout()
        radioLay.addWidget(self.radioArkaplan)
        radioLay.addWidget(self.radioYazi)
        radioLay.addWidget(self.radioCizgi)

        self.radioBtnGroup.buttonClicked.connect(self.act_radio_secim_degisti)

        self.renkSecici = RenkSeciciWidget(self.cScene.aktifArac.arkaPlanRengi, boyut=64, parent=self.nesneOzellikleriDWBaseWidget)
        self.renkSecici.renkDegisti.connect(self.renk_secicide_renk_degisti)
        self.renkSecici.anaLay.setContentsMargins(0, 0, 0, 0)
        shared.kutulu_arkaplan_olustur(self.nesneArkaplanRengiBtn, 5)
        shared.kutulu_arkaplan_olustur(self.yaziRengiBtn, 5)
        shared.kutulu_arkaplan_olustur(self.cizgiRengiBtn, 5)

        anaLay.addLayout(radioLay)
        anaLay.addWidget(self.renkSecici)
        anaLay.addWidget(self.nesneGrupW)
        anaLay.addWidget(self.yaziGrupW)
        anaLay.addWidget(self.cizgiGrupW)

    # ---------------------------------------------------------------------
    def act_radio_secim_degisti(self, btn):
        if btn == self.radioArkaplan:
            if self.cScene.activeItem:
                renk = self.cScene.activeItem.arkaPlanRengi
            else:
                renk = self.cScene.aktifArac.arkaPlanRengi
            self.renk_tipi = "a"

            self.nesneGrupW.show()
            self.yaziGrupW.hide()
            self.cizgiGrupW.hide()

        elif btn == self.radioYazi:
            if self.cScene.activeItem:
                renk = self.cScene.activeItem.yaziRengi
            else:
                renk = self.cScene.aktifArac.yaziRengi
            self.renk_tipi = "y"

            self.nesneGrupW.hide()
            self.yaziGrupW.show()
            self.cizgiGrupW.hide()

        elif btn == self.radioCizgi:
            if self.cScene.activeItem:
                renk = self.cScene.activeItem.cizgiRengi
            else:
                renk = self.cScene.aktifArac.cizgiRengi
            self.renk_tipi = "c"

            self.nesneGrupW.hide()
            self.yaziGrupW.hide()
            self.cizgiGrupW.show()

        self.renkSecici.disardan_renk_gir(renk)

    # ---------------------------------------------------------------------
    def renk_secicide_renk_degisti(self, renk):
        if self.renk_tipi == "a":
            self.cScene.aktifArac.arkaPlanRengi = renk
            self.act_set_item_background_color(renk, renkSecicidenMi=True)
        elif self.renk_tipi == "y":
            self.cScene.aktifArac.yaziRengi = renk
            self.act_set_item_text_color(renk, renkSecicidenMi=True)
        elif self.renk_tipi == "c":
            self.cScene.aktifArac.cizgiRengi = renk
            self.act_set_item_line_color(renk, renkSecicidenMi=True)

    # ---------------------------------------------------------------------
    def olustur_stillerYW(self):

        self.stillerYuzenWidget = YuzenWidget(self)
        self.stillerYuzenWidget.hide()

        self.yuzenStylePresetsListWidget = QListWidget(self.stillerYuzenWidget)
        self.yuzenStylePresetsListWidget.setMinimumWidth(100)
        self.yuzenStylePresetsListWidget.setMinimumHeight(100)
        # self.yuzenStylePresetsListWidget.setMaximumHeight(500)
        # self.yuzenStylePresetsListWidget.resize(250, 100)
        self.yuzenStylePresetsListWidget.setSpacing(3)
        self.yuzenStylePresetsListWidget.itemDoubleClicked.connect(self.act_apply_selected_style)

        delegate = ListWidgetItemDelegate(self.yuzenStylePresetsListWidget)
        self.yuzenStylePresetsListWidget.setItemDelegate(delegate)

        self.stillerYuzenWidget.ekleWidget(self.yuzenStylePresetsListWidget)

    # ---------------------------------------------------------------------
    def olustur_stillerDW(self):
        self.stillerDW = DockWidget(self.tr("Style Presets"), self)
        self.stillerDW.setObjectName("stillerDockWidget")
        # self.stillerDW.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.stillerDW)

        # -- her ada nın cevresine bir onu kaplayici ve margini ayarlanabilir bir cember veya kutu

        scroll = QScrollArea()
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        # scroll.setBackgroundRole(QPalette.Dark)
        self.stillerDW.setWidget(scroll)
        # scrollLayout = QVBoxLayout(scroll)

        self.stillerDWBaseWidget = QWidget(scroll)
        # self.stillerDW.setWidget(self.stillerDWBaseWidget)
        anaLay = QVBoxLayout(self.stillerDWBaseWidget)
        # anaLay.setSizeConstraint(QVBoxLayout.SetFixedSize)
        # anaLay.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        anaLay.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        # anaLay.setSizeConstraint(QVBoxLayout.SetMaximumSize)
        # anaLay.setContentsMargins(0,0,0,0)
        # self.stillerDW.setContentsMargins(0, 0, 0, 0)
        # self.stillerDWBaseWidget.setContentsMargins(0,0,0,0)
        # scrollLayout.addWidget(self.stillerDWBaseWidget)
        scroll.setWidget(self.stillerDWBaseWidget)
        # scroll.setLayout(layout)

        self.stylePresetsListWidget = QListWidget(self.stillerDWBaseWidget)

        delegate = ListWidgetItemDelegate(self.stylePresetsListWidget)
        self.stylePresetsListWidget.setItemDelegate(delegate)
        # self.stylePresetsListWidget.setItemDelegateForRow()
        # self.stylePresetsListWidget.setLineWidth(100)
        # self.stylePresetsListWidget.setViewMode(self.stylePresetsListWidget.IconMode)
        # self.stylePresetsListWidget.setMovement(self.stylePresetsListWidget.Free)
        self.stylePresetsListWidget.setSpacing(3)
        # self.stylePresetsListWidget.setSelectionMode(self.stylePresetsListWidget.ExtendedSelection)
        self.stylePresetsListWidget.itemDoubleClicked.connect(self.act_apply_selected_style)
        self.stylePresetsListWidget.itemSelectionChanged.connect(self.act_stylePresetsListWidget_secim_degisti)
        # self.stylePresetsListWidget.addItem(ListWidgetItem("asd"))

        anaLay.addWidget(self.stylePresetsListWidget)

        btnLayout = QHBoxLayout()

        addStylePresetBtn = QPushButton(self.tr("Add"), self.stillerDWBaseWidget)
        # addStylePresetBtn.setFixedWidth(50)
        addStylePresetBtn.clicked.connect(self.act_add_style_preset)
        self.removeStylePresetBtn = QPushButton(self.tr("Remove"), self.stillerDWBaseWidget)
        # self.removeStylePresetBtn.setFixedWidth(50)
        self.removeStylePresetBtn.clicked.connect(self.act_remove_style_preset)
        self.removeStylePresetBtn.setDisabled(True)
        stylePrestesMenuBtn = QPushButton("☰", self.stillerDWBaseWidget)
        stylePrestesMenuBtn.setFixedWidth(30)

        stylePresetsMenu = QMenu(self.tr("Presets"), stylePrestesMenuBtn)
        stylePresetsMenu.aboutToShow.connect(self.on_style_presets_menu_about_to_show)

        actionLoadAndReplaceStylePrests = QAction(QIcon(':icons/folder-base.png'), self.tr("Load and replace"),
                                                  stylePresetsMenu)
        actionLoadAndReplaceStylePrests.triggered.connect(self.act_load_and_replace_style_presets)

        actionLoadAndAppendStylePrests = QAction(QIcon(':icons/folder-base.png'), self.tr("Load and append"),
                                                 stylePresetsMenu)
        actionLoadAndAppendStylePrests.triggered.connect(self.act_load_and_append_style_presets)

        self.actionSaveStylePrests = QAction(QIcon(':icons/folder-base.png'), self.tr("Save presets"),
                                             stylePresetsMenu)
        self.actionSaveStylePrests.triggered.connect(self.act_save_style_presets_to_file)

        self.clearStylePresetsMenu = QMenu("Remove All", stylePresetsMenu)
        actionClearStylePresets = QAction(QIcon(':icons/folder-base.png'), self.tr("Yes"), stylePresetsMenu)
        actionClearStylePresets.setToolTip(self.tr("Can not undo!"))
        actionClearStylePresets.triggered.connect(self.act_clear_style_presets)
        self.clearStylePresetsMenu.addAction(actionClearStylePresets)

        stylePresetsMenu.addActions((
            stylePresetsMenu.addSection(self.tr("Load")),
            actionLoadAndReplaceStylePrests,
            actionLoadAndAppendStylePrests,
            # stylePresetsMenu.addSeparator(),
            stylePresetsMenu.addSection(self.tr("Save")),
            self.actionSaveStylePrests,
            # stylePresetsMenu.addSeparator(),
            stylePresetsMenu.addSection(self.tr("Remove")),
            stylePresetsMenu.addMenu(self.clearStylePresetsMenu)
        ))

        stylePrestesMenuBtn.setMenu(stylePresetsMenu)

        btnLayout.addWidget(addStylePresetBtn)
        btnLayout.addWidget(self.removeStylePresetBtn)
        btnLayout.addWidget(stylePrestesMenuBtn)
        anaLay.addLayout(btnLayout)

    # ---------------------------------------------------------------------
    def olustur_sahneye_baski_siniri_cizim_ayarlari(self):
        self.baskiSiniriCizimAyarlariDW = DockWidget(self.tr("Draw Print Borders"), self)
        self.baskiSiniriCizimAyarlariDW.setObjectName("baskiSiniriCizimAyarlariDockWidget")
        self.baskiSiniriCizimAyarlariDW.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.baskiSiniriCizimAyarlariDW.setVisible(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.baskiSiniriCizimAyarlariDW)

        # -- her ada nın cevresine bir onu kaplayici ve margini ayarlanabilir bir cember veya kutu

        scroll = QScrollArea()
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        # scroll.setBackgroundRole(QPalette.Dark)
        self.baskiSiniriCizimAyarlariDW.setWidget(scroll)
        # scrollLayout = QVBoxLayout(scroll)

        self.baskiSiniriCizimAyarlariDWBW = QWidget(scroll)
        # self.baskiSiniriCizimAyarlariDW.setWidget(self.baskiSiniriCizimAyarlariDWBW)
        anaLay = QVBoxLayout(self.baskiSiniriCizimAyarlariDWBW)
        # anaLay.setSizeConstraint(QVBoxLayout.SetFixedSize)
        # anaLay.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        anaLay.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        # anaLay.setSizeConstraint(QVBoxLayout.SetMaximumSize)
        # anaLay.setContentsMargins(10,15,0,0)
        # self.baskiSiniriCizimAyarlariDW.setContentsMargins(0, 0, 0, 0)
        # self.baskiSiniriCizimAyarlariDWBW.setContentsMargins(0,0,0,0)
        # scrollLayout.addWidget(self.baskiSiniriCizimAyarlariDWBW)
        scroll.setWidget(self.baskiSiniriCizimAyarlariDWBW)
        # scroll.setLayout(layout)

        self.baskiSinirGBox = QGroupBox(self.baskiSiniriCizimAyarlariDWBW)
        self.baskiSinirGBox.setFlat(True)
        self.baskiSinirGBox.setCheckable(True)
        self.baskiSinirGBox.setChecked(False)
        self.baskiSinirGBox.setTitle(self.tr("Draw print borders"))
        self.baskiSinirGBox.clicked.connect(self.act_yazici_sayfa_kenar_cizdir)
        self.baskiSinirGBoxLay = QVBoxLayout(self.baskiSinirGBox)

        renkLbl = QLabel(self.tr("Color"), self.baskiSiniriCizimAyarlariDWBW)
        self.baskiCerceveRengiBtn = PushButtonRenk("", 36, 16, self.baskiCerceveRengi,
                                                   self.baskiSiniriCizimAyarlariDWBW)
        self.baskiCerceveRengiBtn.clicked.connect(self.act_baski_cerceve_rengi_kur)

        renkLay = QHBoxLayout()
        renkLay.addWidget(renkLbl)
        renkLay.addWidget(self.baskiCerceveRengiBtn)
        renkLay.addStretch(1)

        self.baskiBirimCBox = QComboBox(self.baskiSiniriCizimAyarlariDWBW)

        self.baskiBirimCBox.addItem(self.tr("Millimeter"))
        self.baskiBirimCBox.addItem(self.tr("Point"))
        self.baskiBirimCBox.addItem(self.tr("Inch"))
        self.baskiBirimCBox.addItems(["Pica",
                                      "Didot",
                                      "Cicero"])

        kagitLay = QHBoxLayout()
        self.baskiKagitBoyutuCBox = QComboBox(self.baskiSiniriCizimAyarlariDWBW)
        self.baskiKagitBoyutuCBox.setMaximumWidth(135)
        printerInfo = QPrinterInfo(self.printer)
        desteklenenSayfaBoyutlari = printerInfo.supportedPageSizes()
        simdikiId = self.printer.pageLayout().pageSize().id()
        for i in range(int(QPageSize.LastPageSize)):
            psize = QPageSize((QPageSize.PageSizeId(i)))
            if psize.isValid():
                desteklenenSayfaBoyutlari.append(psize)
                self.baskiKagitBoyutuCBox.addItem(psize.name())

        widthLbl = QLabel(self.tr("Width"), self.baskiSiniriCizimAyarlariDWBW)
        heightLbl = QLabel(self.tr("Height"), self.baskiSiniriCizimAyarlariDWBW)
        self.kagitGenislikLE = QLineEdit(self.baskiSiniriCizimAyarlariDWBW)
        self.kagitGenislikLE.setMaximumWidth(75)
        self.kagitGenislikLE.setEnabled(False)
        self.kagitYukseklikLE = QLineEdit(self.baskiSiniriCizimAyarlariDWBW)
        self.kagitYukseklikLE.setMaximumWidth(75)
        self.kagitYukseklikLE.setEnabled(False)

        self.baskiBirimCBox.currentIndexChanged.connect(self.act_baski_birim_changed)
        self.baskiKagitBoyutuCBox.currentIndexChanged.connect(self.act_baski_kagit_boyutu_degisti)
        self.baskiKagitBoyutuCBox.setCurrentIndex(simdikiId)

        kagitLay.addWidget(self.baskiBirimCBox)
        kagitLay.addWidget(self.baskiKagitBoyutuCBox)
        kagitLay.addStretch(1)
        boyutLay = QHBoxLayout()
        boyutLay.addWidget(widthLbl)
        boyutLay.addWidget(self.kagitGenislikLE)
        boyutLay.addWidget(heightLbl)
        boyutLay.addWidget(self.kagitYukseklikLE)
        boyutLay.addStretch(1)

        fitRadioBtnGrp = QButtonGroup(self.baskiSinirGBox)

        self.radioSayfaSigdir = QRadioButton(self.tr("Fit page"), self.baskiSinirGBox)
        self.radioSayfaSigdir.setIcon(QIcon(":icons/sayfa-sigdir.png"))
        self.radioSayfaSigdir.setChecked(True)
        self.radioGenislikSigdir = QRadioButton(self.tr("Fit width"), self.baskiSinirGBox)
        self.radioGenislikSigdir.setIcon(QIcon(":icons/genislik-sigdir.png"))

        fitRadioBtnGrp.addButton(self.radioSayfaSigdir)
        fitRadioBtnGrp.addButton(self.radioGenislikSigdir)

        fitRadioBtnGrp.buttonClicked.connect(self.act_yazici_sayfa_kenar_cizdir)

        sigdirUstLay = QHBoxLayout()
        sigdirLay = QVBoxLayout()
        sigdirLay.addWidget(self.radioSayfaSigdir)
        sigdirLay.addWidget(self.radioGenislikSigdir)
        sigdirLay.addStretch(1)

        kagitYonLay = QVBoxLayout()

        kagitYonBtnGrp = QButtonGroup(self.baskiSiniriCizimAyarlariDWBW)

        self.radioBaskiDikey = QRadioButton(self.tr("Portrait"), self.baskiSiniriCizimAyarlariDWBW)
        self.radioBaskiDikey.setIcon(QIcon(':icons/dikey-sayfa.png'))
        self.radioBaskiDikey.setChecked(True)

        self.radioBaskiYatay = QRadioButton(self.tr("Landscape"), self.baskiSiniriCizimAyarlariDWBW)
        self.radioBaskiYatay.setIcon(QIcon(':icons/yatay-sayfa.png'))

        kagitYonBtnGrp.buttonClicked.connect(self.act_yazici_kagit_yonu_degisti)

        kagitYonBtnGrp.addButton(self.radioBaskiDikey)
        kagitYonBtnGrp.addButton(self.radioBaskiYatay)

        kagitYonLay.addWidget(self.radioBaskiDikey)
        kagitYonLay.addWidget(self.radioBaskiYatay)
        kagitYonLay.addStretch(1)

        sigdirUstLay.addLayout(kagitYonLay)
        sigdirUstLay.addLayout(sigdirLay)

        self.baskiSinirGBoxLay.addLayout(renkLay)
        self.baskiSinirGBoxLay.addLayout(kagitLay)
        self.baskiSinirGBoxLay.addLayout(boyutLay)
        self.baskiSinirGBoxLay.addLayout(sigdirUstLay)

        anaLay.addWidget(self.baskiSinirGBox)

    # ---------------------------------------------------------------------
    def act_baski_cerceve_rengi_kur(self):

        col = self.renk_sec(eskiRenk=self.baskiCerceveRengi,
                            baslik=self.tr("Print Border Color"))
        if not col.isValid():
            return

        self.baskiCerceveRengiBtn.renkGuncelle(col)
        self.baskiCerceveRengi = col

        self.cView.baski_cerceve_rengi_kur(col)

    # ---------------------------------------------------------------------
    def act_baski_birim_changed(self, idx):
        psize = QPageSize((QPageSize.PageSizeId(self.baskiKagitBoyutuCBox.currentIndex())))
        birim = psize.Unit(idx)
        birim2 = self.printer.pageLayout().Unit(idx)

        birim_yazi = ""
        # print(birim.values)
        if birim == psize.Unit.Millimeter:
            birim_yazi = "mm"
        elif birim == psize.Unit.Inch:
            birim_yazi = "in"
        elif birim == psize.Unit.Point:
            birim_yazi = "pt"
        elif birim == psize.Unit.Pica:
            birim_yazi = "P/"
        elif birim == psize.Unit.Didot:
            birim_yazi = "DD"
        elif birim == psize.Unit.Cicero:
            birim_yazi = "CC"
        self.kagitGenislikLE.setText("{}{}".format(psize.size(birim).width(), birim_yazi))
        self.kagitYukseklikLE.setText("{}{}".format(psize.size(birim).height(), birim_yazi))

        pLayout = self.printer.pageLayout()
        pLayout.setUnits(birim2)
        self.printer.setPageLayout(pLayout)

    # ---------------------------------------------------------------------
    def act_baski_kagit_boyutu_degisti(self, idx):
        psize = QPageSize((QPageSize.PageSizeId(idx)))
        # birim = self.printer.pageLayout().Unit(self.baskiBirimCBox.currentIndex())
        birim = psize.Unit(self.baskiBirimCBox.currentIndex())

        if birim == psize.Unit.Millimeter:
            birim_yazi = "mm"
        elif birim == psize.Unit.Inch:
            birim_yazi = "in"
        elif birim == psize.Unit.Point:
            birim_yazi = "pt"
        elif birim == psize.Unit.Pica:
            birim_yazi = "P/"
        elif birim == psize.Unit.Didot:
            birim_yazi = "DD"
        elif birim == psize.Unit.Cicero:
            birim_yazi = "CC"

        self.kagitGenislikLE.setText("{}{}".format(psize.size(birim).width(), birim_yazi))
        self.kagitYukseklikLE.setText("{}{}".format(psize.size(birim).height(), birim_yazi))
        # self.printer.pageLayout().setPageSize(psize)

        pLayout = self.printer.pageLayout()
        pLayout.setPageSize(psize)
        self.printer.setPageLayout(pLayout)

    # ---------------------------------------------------------------------
    def act_yazici_kagit_yonu_degisti(self, btn):
        # printer = QPrinter(QPrinter.HighResolution)
        # printer = QPrinter(QPrinter.PrinterResolution)
        # printer = QPrinter(QPrinter.ScreenResolution)
        # self.printer = QPrinter()
        # self.printer.setPageSize(QPageSize(QPageSize.A4))
        if btn == self.radioBaskiYatay:
            self.printer.setPageOrientation(QPageLayout.Landscape)
            # self.printer.pageLayout().setOrientation(QPageLayout.Landscape)
        else:
            self.printer.setPageOrientation(QPageLayout.Portrait)
            # self.printer.pageLayout().setOrientation(QPageLayout.Portrait)
        # printer.setOutputFormat(QPrinter.PdfFormat)
        # printer.setOutputFileName("deneme.pdf")
        self.act_yazici_sayfa_kenar_cizdir()

    # ---------------------------------------------------------------------
    def olustur_sayfalarDW(self):
        self.sayfalarDW = DockWidget(self.tr("Pages"), self)
        self.sayfalarDW.setObjectName("sayfalarDockWidget")
        # self.sayfalarDW.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sayfalarDW)

        # -- her ada nın cevresine bir onu kaplayici ve margini ayarlanabilir bir cember veya kutu

        base = QWidget(self.sayfalarDW)
        base.setContentsMargins(0, 0, 0, 0)
        self.sayfalarDW.setWidget(base)
        layBase = QVBoxLayout(base)
        layButonlar = QHBoxLayout()
        layBase.addLayout(layButonlar)

        # scroll = QScrollArea()
        # # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # scroll.setWidgetResizable(True)
        # # scroll.setBackgroundRole(QPalette.Dark)
        # self.sayfalarDW.setWidget(scroll)
        # # scrollLayout = QVBoxLayout(scroll)
        # sayfalarBaseWidget = QWidget(scroll)
        # layoutV = QVBoxLayout(sayfalarBaseWidget)
        #
        # layoutV.addLayout(layoutH)
        # # TODO: bu layout sistemi tam olmadı

        self.sayfalarDWTreeView = TreeView(base)
        # self.sayfalarDWTreeModel = TreeModel(self.sayfalarDWTreeView)
        # self.sayfalarDWTreeView.setModel(self.sayfalarDWTreeModel)

        # for column in range(self.sayfalarDWTreeModel.columnCount()):
        #     self.sayfalarDWTreeView.resizeColumnToContents(column)

        # self.sayfalarDWTreeView.model().dataChanged.connect(self.tw_model_data_changed)
        layBase.addWidget(self.sayfalarDWTreeView)

        # self.sayfalarDWTreeView.doubleClicked.connect(self.tw_edit_item)
        # self.sayfalarDWTreeView.itemDoubleClicked.connect(self.tw_edit_item)
        # self.sayfalarDWTreeModel.nesneDegistirilmekUzere.connect(self.tv_nesne_degistirilmek_uzere)
        # self.sayfalarDWTreeModel.nesneDegisti.connect(self.tv_nesne_degisti)
        # self.sayfalarDWTreeView.itemSelectionChanged.connect(self.tw_item_selection_changed)
        # self.sayfalarDWTreeView.itemPressed.connect(self.tw_item_clicked)
        # self.sayfalarDWTreeView.nesneAktiveEdildi.connect(self.tv_sayfa_degistir)
        self.sayfalarDWTreeView.secimDegisti.connect(self.tv_sayfa_degistir)
        # self.sayfalarDWTreeView.itemClicked.connect(self.tv_sayfa_degistir)

        self.twsayfa_ekle_btn = QPushButton(base)
        self.twsayfa_ekle_btn.setIcon(QIcon(":icons/yesil-yeni-sayfa.png"))
        self.twsayfa_ekle_btn.setToolTip(self.tr("Add new page"))
        self.twsayfa_ekle_btn.setFlat(True)
        self.twsayfa_ekle_btn.setFixedWidth(30)
        self.twsayfa_ekle_btn.setFixedHeight(20)
        # self.twsayfa_ekle_btn.setText("☪ ")  # ⊹
        self.twsayfa_ekle_btn.clicked.connect(self.tw_sayfa_ekle)
        layButonlar.addWidget(self.twsayfa_ekle_btn)

        self.tw_alt_sayfa_ekle_btn = QPushButton(base)
        self.tw_alt_sayfa_ekle_btn.setIcon(QIcon(":icons/ic-sayfa-yesil.png"))
        self.tw_alt_sayfa_ekle_btn.setToolTip(self.tr("Add new inner page"))
        self.tw_alt_sayfa_ekle_btn.setFlat(True)
        self.tw_alt_sayfa_ekle_btn.setFixedWidth(30)
        self.tw_alt_sayfa_ekle_btn.setFixedHeight(20)
        # self.tw_alt_sayfa_ekle_btn.setText("↳")  # ⥱ ⥲
        self.tw_alt_sayfa_ekle_btn.clicked.connect(self.tw_alt_sayfa_ekle)
        layButonlar.addWidget(self.tw_alt_sayfa_ekle_btn)

        self.tw_sayfa_sil_btn = QPushButton(base)
        self.tw_sayfa_sil_btn.setIcon(QIcon(":icons/sil-sayfa.png"))
        self.tw_sayfa_sil_btn.setToolTip(self.tr("Delete selected page"))
        self.tw_sayfa_sil_btn.setEnabled(False)
        self.tw_sayfa_sil_btn.setFlat(True)
        self.tw_sayfa_sil_btn.setFixedWidth(30)
        self.tw_sayfa_sil_btn.setFixedHeight(20)
        # self.tw_sayfa_sil_btn.setText("✘")  # ✗
        self.tw_sayfa_sil_btn.clicked.connect(self.tw_sayfa_sil)
        layButonlar.addWidget(self.tw_sayfa_sil_btn)

    # ---------------------------------------------------------------------
    def olustur_kutuphaneDW(self):
        self.kutuphaneDW = DockWidget(self.tr("Library"), self)
        self.kutuphaneDW.setObjectName("kutuphaneDockWidget")
        # self.kutuphaneDW.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.kutuphaneDW)

        # -- her ada nın cevresine bir onu kaplayici ve margini ayarlanabilir bir cember veya kutu

        base = QWidget(self.kutuphaneDW)
        base.setContentsMargins(0, 0, 0, 0)
        self.kutuphaneDW.setWidget(base)
        layBase = QVBoxLayout(base)
        layButonlar = QHBoxLayout()
        layBase.addLayout(layButonlar)

        #######################################################################
        #######################################################################
        # bu ikinci bir ekran icin
        #######################################################################
        #######################################################################

        # # scene = QGraphicsScene(self)  # veya self.cScene =  .. parent etmezsek selfe
        #
        # # sahne = SahneKutuphane(self, cScene)
        # # scene.setSceneRect(QRectF(0, 0, 400, 600))
        # # self.cScene.textItemSelected.connect(self.text_item_selected)
        # ekran = EkranKutuphane(self.cScene, self)
        #
        # # self.cSahneKutuphane = sahne
        # self.cEkranKutuphane = ekran
        # # view.setViewport(QGLWidget())
        # layBase.addWidget(ekran)

        #######################################################################
        #######################################################################

        # scene = QGraphicsScene(self)  # veya self.cScene =  .. parent etmezsek selfe

        # list(self.cModel.sayfalar()) cunku generator, ilk islemde tuketiyoruz, sonra problem
        sahne = SahneKutuphane(self.cScene, list(self.cModel.sayfalar()), self.cModel.tempDirPath, self)
        sahne.setSceneRect(QRectF(0, 0, 200, 500))
        # self.cScene.textItemSelected.connect(self.text_item_selected)
        ekran = EkranKutuphane(sahne, self)

        self.sahneKutuphane = sahne
        self.ekranKutuphane = ekran
        # view.setViewport(QGLWidget())
        layBase.addWidget(ekran)

    # ---------------------------------------------------------------------
    def act_kut_belgedeki_gomulu_dosyalari_goster(self):
        self.sahneKutuphane.belgedeki_gomulu_dosyalari_goster()

    # ---------------------------------------------------------------------
    def act_kut_sahnedeki_gomulu_dosyalari_goster(self):
        self.sahneKutuphane.sahnedeki_gomulu_dosyalari_goster()

    # ---------------------------------------------------------------------
    def act_kut_sahnede_kullanilmayan_gomulu_dosyalari_goster(self):
        self.sahneKutuphane.sahnede_kullanilmayan_gomulu_dosyalari_goster()

    # ---------------------------------------------------------------------
    def act_kut_belgede_kullanilmayan_gomulu_dosyalari_goster(self):
        self.sahneKutuphane.belgede_kullanilmayan_gomulu_dosyalari_goster()

    # ---------------------------------------------------------------------
    def act_kut_belgedeki_linkli_dosyalari_goster(self):
        self.sahneKutuphane.belgedeki_linkli_dosyalari_goster()

    # ---------------------------------------------------------------------
    def act_kut_sahnedeki_linkli_dosyalari_goster(self):
        self.sahneKutuphane.sahnedeki_linkli_dosyalari_goster()

    # ---------------------------------------------------------------------
    def act_kut_belgedeki_linkli_ve_gomulu_dosyalari_goster(self):
        self.sahneKutuphane.belgedeki_linkli_ve_gomulu_dosyalari_goster()

    # ---------------------------------------------------------------------
    def act_kut_belgedeki_html_imajlari_goster(self):
        self.sahneKutuphane.belgedeki_html_imajlari_goster()

    # ---------------------------------------------------------------------
    def act_kut_sahnedeki_linkli_ve_gomulu_dosyalari_goster(self):
        self.sahneKutuphane.sahnedeki_linkli_ve_gomulu_dosyalari_goster()

    # ---------------------------------------------------------------------
    def act_kut_belgede_kullanilmayan_gomulu_dosyalari_sil(self):

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(self.tr("Defter: Delete unused embeded files?"))
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(self.tr("Do you want to delete unused embeded files in the document?"))
        msgBox.setInformativeText(self.tr("This is undoable!"))

        deleteButton = msgBox.addButton(self.tr("&Delete"), QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton(self.tr("&Cancel"), QMessageBox.RejectRole)
        # msgBox.addButton(QMessageBox.Cancel)
        msgBox.setDefaultButton(deleteButton)
        msgBox.setEscapeButton(cancelButton)

        msgBox.exec()
        if msgBox.clickedButton() == deleteButton:
            self.sahneKutuphane.belgede_kullanilmayan_gomulu_dosyalari_sil()

    # ---------------------------------------------------------------------
    def act_kutuphaneden_nesne_sil(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(self.tr("Defter: Delete selected embeded files?"))
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(self.tr("Do you want to delete selected embeded files in the document?"))
        msgBox.setInformativeText(self.tr("This is undoable! Used files will not be deleted!"))

        deleteButton = msgBox.addButton(self.tr("&Delete"), QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton(self.tr("&Cancel"), QMessageBox.RejectRole)
        # msgBox.addButton(QMessageBox.Cancel)
        msgBox.setDefaultButton(deleteButton)
        msgBox.setEscapeButton(cancelButton)

        msgBox.exec()
        if msgBox.clickedButton() == deleteButton:
            self.sahneKutuphane.secilen_nesneleri_sil()

    # # ---------------------------------------------------------------------
    # @Slot(QModelIndex, QModelIndex)
    # def tw_model_data_changed(self, topLeft, bottomRight):
    #     print(topLeft.data(Qt.DisplayRole), bottomRight.data(Qt.DisplayRole))

    # ---------------------------------------------------------------------
    # @Slot('QStandardItem*')
    @Slot(Sayfa, str)
    def tv_nesne_degisti(self, sayfa, sayfa_eski_adi):
        print("nesne_degisti")
        # bu her degisiklikte cagriliyor !! , ufak resim guncellemeden dolayi..
        # resim guncellemeye -Hamd Olsun- block signals eklemek suretiyle cozuldu.
        # print(item, column)
        # if not column da olur ama burda 0 ozellikle bekledigimiz bir rakkam.
        # Yanlis anlasilma olmasin ilerde ..
        # aslında gereksiz, cunku ancak sayfayi column 1'e atarken, bi degisiklik oluyor diger columnlarda
        # yoksa hep column 0 da degisiklik var, ilk bakışta... dusunulebilir.
        # if column == 0:
        # idx = self.sayfalarDWTreeView.indexFromItem(item, column).row()
        # self.cModel.sayfalar[idx].adi = item.text(column)
        # sayfa.adi = item.text(column)
        # sayfa_adi = item.data(Qt.DisplayRole)
        # sayfa adi degistirilince kaydetme ve yildizli sayfa adi aktif olsun diye
        aciklama = self.tr("edit page name")
        undoRedo.undoableSayfaAdiDegistir(self.cScene.undoStack, aciklama, sayfa, sayfa_eski_adi)
        # self.pencere_ve_tab_yazilarini_guncelle()

        # # bu column == 0 ile test edildigi icin sadece sahne adi degistirilince cagriliyor.
        # if sayfa.scene.isModified():
        #     if not sayfa.adi[0] == "★":
        #         self.sayfalarDWTreeView.blockSignals(True)
        #         yildizli_sayfa_adi = "★ {}".format(sayfa.adi)
        #         sayfa.adi = yildizli_sayfa_adi
        #         self.sayfalarDWTreeView.blockSignals(False)
        #     # item.setForeground(0, Qt.blue)

    # # ---------------------------------------------------------------------
    # def mouseDoubleClickEvent(self, a0):
    #     super(DefterAnaPencere, self).mouseDoubleClickEvent(a0)
    #     undoStack = self.findChildren(QUndoStack, options=Qt.FindChildrenRecursively)
    #     view = self.findChildren(View, options=Qt.FindChildrenRecursively)
    #     scene = self.findChildren(Scene, options=Qt.FindChildrenRecursively)
    #     modeller = self.tabWidget.modeller
    #     cModel = self.tabWidget.cModel
    #     sayfalar = list(cModel.iterItems(cModel.kokSayfa))
    #
    #     print(undoStack)
    #     print(view)
    #     print(scene)
    #     print(modeller)
    #     print(sayfalar)

    # print([i.parent() for i in undoStack])

    # ---------------------------------------------------------------------
    def ekle_sil_butonlari_guncelle(self):

        # secilenSayfa = self.sayfalarDWTreeView.get_selected_sayfa()
        secilenSayfa = self.sayfalarDWTreeView.get_current_sayfa()
        # self.tw_sayfa_sil_btn.setEnabled(True)
        if secilenSayfa.ic_sayfa_var_mi():
            self.tw_sayfa_sil_btn.setEnabled(False)
            # return
        else:
            if secilenSayfa.parent() == self.cModel.kokSayfa:
                if self.cModel.rowCount() == 1:
                    self.tw_sayfa_sil_btn.setEnabled(False)
                else:
                    self.tw_sayfa_sil_btn.setEnabled(True)
            else:
                self.tw_sayfa_sil_btn.setEnabled(True)

    # ---------------------------------------------------------------------
    @Slot(Sayfa)
    def tv_sayfa_degistir(self, sayfa):
        # print(item)

        """
            # sayfa ekleyip cikarinca cagiriyoruz,
            # sayfalarDWTreeView.selectionChanged kullanmiyoruz cunku arada birden fazla defa emit ediliyor
            tw_sayfa_ekle()
            tw_alt_sayfa_ekle()
            tw_sayfa_sil()

            # klavye ile de sayfalarDWTreeView.itemActivated() ile cagiriyoruz..

            # selectionChanged alternatifi olarak
            sayfalarDWTreeView.mousePressEvent() cagiriyoruz.

        """

        self.cView = sayfa.view
        self.cScene = sayfa.scene
        # self.cScene = self.cView.scene()

        self.undoGroup.setActiveStack(self.cScene.undoStack)

        with signals_updates_blocked(self.tabWidget):

            idx = self.tabWidget.currentIndex()
            # print("current index:", idx)
            self.tabWidget.removeTab(idx)
            self.tabWidget.insertTab(idx, self.cView, "{} - {}".format(self.cModel.fileName, sayfa.adi))
        # TODO: ONEMLİ BUNUN DISARDA KALMASI ONEMLİ !! YİNE BİR BAKILSIN
        self.tabWidget.setCurrentIndex(idx)

        self.cScene.setFocus()

        # sayfa_idx = self.sayfalarDWTreeView.indexFromItem(item, 0).row()
        # self.cModel.enSonAktifSayfa = sayfa_idx
        self.cModel.enSonAktifSayfa = sayfa

        self.pencere_ve_tab_yazilarini_guncelle()

        # self.tabWidget.setTabToolTip(self.tabWidget.currentIndex(), self.tr("Unsaved File"))

        self.ekle_sil_butonlari_guncelle()

        try:
            self.sahneKutuphane.tempDirPath = self.cModel.tempDirPath
            self.sahneKutuphane.asil_sahne = self.cScene
            # list(self.cModel.sayfalar()) cunku generator, ilk islemde tuketiyoruz, sonra problem
            self.sahneKutuphane.sayfalar = list(self.cModel.sayfalar())
        except AttributeError:
            print("ilk açılışta problem olmasin diye.")

    # ---------------------------------------------------------------------
    @Slot()
    def tw_sayfa_ekle(self, parentItem=None):

        with signals_updates_blocked(self.sayfalarDWTreeView):
            scene, view = self.create_scene(self.cModel.tempDirPath)
            # parentItem = self.sayfalarDWTreeView.get_selected_sayfanin_parent_sayfasi()
            if not parentItem:
                parentItem = self.sayfalarDWTreeView.get_selected_sayfanin_parent_sayfasi()
                # parentItem = self.sayfalarDWTreeView.get_current_sayfa()
                # if not parentItem:
                #     self.log(self.tr("Please select a page."))
                #     return
            # satir = self.sayfalarDWTreeView.get_selected_sayfa().satir()
            satir = parentItem.satirSayisi()-1
            sayfa = self.cModel.sayfa_ekle(satir=satir,
                                           scene=scene,
                                           view=view,
                                           ustSayfa=parentItem,
                                           ikon=self.tw_get_page_as_icon()
                                           )

            # self.sayfalarDWTreeView.clearSelection()
            # root.setSelected(True)
            self.sayfalarDWTreeView.sayfayi_sec_ve_current_index_yap(sayfa)
            # self.sayfalarDWTreeView.scrollTo(self.cModel.index_sayfadan(sayfa),
            #                                  self.sayfalarDWTreeView.EnsureVisible)  # PositionAtCenter

            # self.sayfalarDWTreeView.sec()
            # item.setSelected(True)

        # tv_sayfa_degistir burda yeni dokuman yani tab ekleme ile ilgili
        # problemlere neden oluyor şimdilik iptal
        self.tv_sayfa_degistir(sayfa)

        # item.setSizeHint(0, QSize(256,256))
        # self.ekle_sil_butonlari_guncelle()

        return sayfa

    # ---------------------------------------------------------------------
    @Slot()
    def tw_alt_sayfa_ekle(self, parentItem=None):

        with signals_updates_blocked(self.sayfalarDWTreeView):
            if not parentItem:  # arayuzden altsayfa ekliyoruz, yoksa dosya yuklenirken parentItem geliyor zaten
                parentItem = self.sayfalarDWTreeView.get_current_sayfa()
                if not parentItem:
                    self.log(self.tr("Please select a page."))
                    return

            # with signals_updates_blocked(self.sayfalarDWTreeView):

            scene, view = self.create_scene(self.cModel.tempDirPath)
            # self.cScene = scene
            # self.cView = view

            # parentItem = self.sayfalarDWTreeView.get_current_sayfa()
            # parentItem = self.sayfalarDWTreeView.get_selected_sayfa()
            # satir = self.sayfalarDWTreeView.get_selected_sayfa().satir()
            sayfa = self.cModel.sayfa_ekle(scene=scene,
                                           view=view,
                                           ustSayfa=parentItem,
                                           ikon=self.tw_get_page_as_icon())

            # self.sayfalarDWTreeView.sayfayi_sec_ve_current_index_yap(sayfa.parent())
            self.sayfalarDWTreeView.sayfayi_sec_ve_current_index_yap(sayfa)

        self.sayfalarDWTreeView.sayfayi_expand_et(parentItem)
        # self.sayfalarDWTreeView.sayfayi_expand_et(sayfa.parent())
        self.tv_sayfa_degistir(sayfa)

        self.ekle_sil_butonlari_guncelle()
        # print(self.cModel.enSonAktifSayfa.adi)

        # if sayfa_dondur:
        return sayfa

    # ---------------------------------------------------------------------
    @Slot()
    def tw_sayfa_sil(self):

        sayfa = self.sayfalarDWTreeView.get_current_sayfa()

        if sayfa == self.cModel.kokSayfa:  # hep bir sayfa donuyor yoksa kokSayfa donuyor, kok sayfa da gorunmez ya
            self.log(self.tr("Please select a page."))
            return

        # klavye ile secilip aktif edilmeden silinebilir sayfa, o yuzden selectedItems[0]
        # idx = self.sayfalarDWTreeView.selectedIndexes()[0]
        # with signals_updates_blocked(self.tabWidget):
        scene = sayfa.scene
        view = sayfa.view

        self.cModel.satir_sil(sayfa)
        self.cModel.enSonAktifSayfa = None

        # self.tv_sayfa_degistir(self.sayfalarDWTreeView.currentItem())
        # self.sayfalarDWTreeView.sayfayi_sec_ve_current_index_yap(parentSayfa)
        self.tv_sayfa_degistir(self.sayfalarDWTreeView.get_current_sayfa())

        # silinen satirin(sayfanin scene ve viewi temizleniyor)
        scene.undoStack.clear()
        self.undoGroup.removeStack(scene.undoStack)
        scene.undoStack.setParent(None)
        scene.undoStack.deleteLater()
        # self.undoGroup.blockSignals(False)

        view.setParent(None)
        scene.setParent(None)
        view.deleteLater()
        scene.deleteLater()

    # ---------------------------------------------------------------------
    def tw_modeli_ve_sayfalari_sil(self, model):

        with signals_blocked(model):
            # dikkat! burda dongu yaptigimiz listeden sayfa siliyoruz, satir sil diyerek
            # o yuzden kopya uzerinde dongu yapiyoruz.
            for sayfa in model.kokSayfa.ic_sayfalar()[:]:
                sayfa.scene.undoStack.clear()
                self.undoGroup.removeStack(sayfa.scene.undoStack)
                sayfa.scene.undoStack.setParent(None)
                sayfa.scene.undoStack.deleteLater()
                # sayfa.scene.clear()
                sayfa.scene.setParent(None)
                sayfa.scene.deleteLater()
                sayfa.view.setParent(None)
                sayfa.view.deleteLater()
                if sayfa._ic_sayfalar:
                    self._tw_sayfalari_sil(sayfa, model)
                model.satir_sil(sayfa)

        # model.sifirla()
        # model.deleteLater()
        self.tabWidget.model_sil(model)
        # self.cModel = None

    #     for i in reversed(range(self.cModel.rowCount())):
    #         parentItem = self.cModel.item(i)
    #         if parentItem.ic_sayfa_var_mi():
    #             self._tw_sayfalari_sil(parentItem)
    #
    #         itemPointerList = self.cModel.takeRow(i)
    #         parentItem = itemPointerList[0]
    #         del itemPointerList
    #         sayfa = parentItem.data(Qt.UserRole)
    #         self.cModel.sayfa_sil(sayfa)
    #         del sayfa
    #         del parentItem
    #
    # ---------------------------------------------------------------------
    def _tw_sayfalari_sil(self, parentItem, model):
        # dikkat! burda dongu yaptigimiz listeden sayfa siliyoruz, satir sil diyerek
        # o yuzden kopya uzerinde dongu yapiyoruz.
        for sayfa in parentItem.ic_sayfalar()[:]:
            sayfa.scene.undoStack.clear()
            self.undoGroup.removeStack(sayfa.scene.undoStack)
            sayfa.scene.undoStack.setParent(None)
            sayfa.scene.undoStack.deleteLater()
            sayfa.scene.setParent(None)
            sayfa.scene.deleteLater()
            sayfa.view.setParent(None)
            sayfa.view.deleteLater()

            if sayfa._ic_sayfalar:
                self._tw_sayfalari_sil(sayfa, model)
            model.satir_sil(sayfa)

        # for i in reversed(range(parentItem.ic_sayfa_var_mi())):
        #     item = parentItem.child(i)  # i = row
        #     if item.ic_sayfa_var_mi():
        #         self._tw_sayfalari_sil(item)
        #
        #     itemPointerList = parentItem.takeRow(item.row())
        #     item = itemPointerList[0]
        #     del itemPointerList
        #
        #     sayfa = item.data(Qt.UserRole)
        #     self.cModel.sayfa_sil(sayfa)
        #     del sayfa
        #     del item

    # ---------------------------------------------------------------------
    @Slot()
    def tw_sayfa_guncelle(self):
        # SelectedIndexes[0] yerine curentIndex() ten item donduren metodlari kullanmak bir tik daha iyi olabilir.
        # self.sayfalarDWTreeView.get_selected_sayfa().ikon = QIcon(self.tw_get_page_as_pixmap(self.cView))
        self.sayfalarDWTreeView.get_current_sayfa().ikon = self.tw_get_page_as_icon()
        idx = self.sayfalarDWTreeView.currentIndex()
        self.sayfalarDWTreeView.dataChanged(idx, idx)
        # TODO: burda thumbnailleri preview olarak kaydetsek mi tmp klasore,
        # tab degisitrince isler karmasiklasiyor

    # ---------------------------------------------------------------------
    def tw_get_page_as_icon(self):
        """bunu ozellikle thread yapmadık, sayfalar ilk olusturulurken bu kullanılıyor"""

        # pixmap = self.cView.grab(self.cView.get_visible_rect().toRect())
        # pixmap = view.grab(view.childrenRect())
        # pixmap = view.grab(view.contentsRect())
        # pixmap = view.grab(self.tabWidget.currentWidget().contentsRect())
        # pixmap = view.grab()
        pixmap = self.cView.grab(self.cView.viewport().rect())
        # pixmap = pixmap.scaled(128,128,Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        # pixmap = pixmap.scaledToWidth(self.sayfalarDWTreeView.width(), Qt.FastTransformation)
        pixmap = pixmap.scaledToWidth(128, Qt.FastTransformation)
        return QIcon(pixmap)

    # ---------------------------------------------------------------------
    def increase_zvalue(self, item):
        self.cScene.sonZDeger += 1
        item.setZValue(self.cScene.sonZDeger)

    # ---------------------------------------------------------------------
    def get_mouse_scene_pos(self):
        """
        :return: QPoint()
        """
        # scene_pos = self.mapFromGlobal(QCursor.pos())
        scene_pos = self.cView.mapFromGlobal(QCursor.pos())
        # scene_pos = self.cScene.views()[0].mapToScene(scene_pos)
        scene_pos = self.cView.mapToScene(scene_pos)
        return scene_pos

    # ---------------------------------------------------------------------
    def move_or_append_left_in_recent_files_queue(self, filePath):
        if filePath in self.recentFilesQueue:
            self.recentFilesQueue.remove(filePath)
        self.recentFilesQueue.appendleft(filePath)
        # this line below is unnecesarry after first run (and after first file closing).
        # It is kept for User eXperince.
        self.actionReopenLastClosedTab.setEnabled(True)

    # ---------------------------------------------------------------------
    def olustur_ayarlar(self):
        QCoreApplication.setOrganizationName(shared.DEFTER_ORG_NAME)
        QCoreApplication.setOrganizationDomain(shared.DEFTER_ORG_DOMAIN)
        QCoreApplication.setApplicationName(shared.DEFTER_APP_NAME)
        self.settings = QSettings(shared.DEFTER_AYARLAR_DOSYA_ADRES, QSettings.IniFormat)
        self.settingsAraclar = QSettings(shared.DEFTER_AYARLAR_ARACLAR_DOSYA_ADRES, QSettings.IniFormat)
        # self.settings.clear()

    # ---------------------------------------------------------------------
    def oku_kullanici_ayarlari(self):
        KULLANICI_KLASORU = os.path.expanduser("~")
        self.settings.beginGroup("UserSettings")
        if self.settings.contains("sonKlasor"):
            self.sonKlasor = self.settings.value("sonKlasor", KULLANICI_KLASORU)
            self.sonKlasorResimler = self.settings.value("sonKlasorResimler", KULLANICI_KLASORU)
            self.sonKlasorVideolar = self.settings.value("sonKlasorVideolar", KULLANICI_KLASORU)
            self.sonKlasorDosyalar = self.settings.value("sonKlasorDosyalar", KULLANICI_KLASORU)
            self.sonKlasorDisaAktar = self.settings.value("sonKlasorDisaAktar", KULLANICI_KLASORU)
            self.sonKlasorHTML = self.settings.value("sonKlasorHTML", KULLANICI_KLASORU)
            self.itemSize = self.settings.value("itemSize", QSizeF(25, 25))
            self.textSize = int(self.settings.value("textSize", 10))
            self.baskiCerceveRengi = self.settings.value("baskiCerceveRengi", QColor(0, 0, 0))

            font = QFont(self.settings.value("currentFont", QApplication.font().family()))
            font.setPointSize(self.textSize)
            self.currentFont = font

            self.karakter_bicimi_sozluk = {"b": self.currentFont.bold(),
                                           "i": self.currentFont.italic(),
                                           "u": self.currentFont.underline(),
                                           "s": self.currentFont.strikeOut(),
                                           "o": self.currentFont.overline(),
                                           }

        else:
            self.sonKlasor = self.sonKlasorDisaAktar = self.sonKlasorHTML = KULLANICI_KLASORU
            self.sonKlasorResimler = self.sonKlasorVideolar = self.sonKlasorDosyalar = KULLANICI_KLASORU
            # self.sonKlasorResimler = os.path.expanduser("~")
            # self.sonKlasorDisaAktar = os.path.expanduser("~")

            font = QFont(QApplication.font().family())
            font.setPointSize(10)
            self.currentFont = font

        self.settings.endGroup()

        self.settings.beginGroup("RecentFilePaths")
        for key in self.settings.childKeys():
            self.recentFilesQueue.append(self.settings.value(key))
        self.settings.endGroup()

        self.yazi_rengi_btn_liste_acilis_renkleri = []
        self.settings.beginGroup("YaziRengiButonlari")
        for i in range(16):
            self.yazi_rengi_btn_liste_acilis_renkleri.append(self.settings.value("{}".format(i)))
        self.settings.endGroup()

        self.nesne_arkaplan_rengi_btn_liste_acilis_renkleri = []
        self.settings.beginGroup("NesneArkaplanRengiButonlari")
        for i in range(16):
            self.nesne_arkaplan_rengi_btn_liste_acilis_renkleri.append(self.settings.value("{}".format(i)))
        self.settings.endGroup()

        self.cizgi_rengi_btn_liste_acilis_renkleri = []
        self.settings.beginGroup("CizgiRengiButonlari")
        for i in range(16):
            self.cizgi_rengi_btn_liste_acilis_renkleri.append(self.settings.value("{}".format(i)))
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    def oku_arayuz_ayarlari(self):

        self.settings.beginGroup("GuiSettings")
        if self.settings.contains("winGeometry"):
            self.restoreGeometry(self.settings.value("winGeometry"))
            self.restoreState(self.settings.value("winState", 0))
            # self.actionAlwaysOnTopToggle.setChecked(bool(int(self.settings.value("alwaysOnTop", False))))
            with signals_blocked(self.actionAlwaysOnTopToggle):
                self.actionAlwaysOnTopToggle.setChecked(int(self.settings.value("alwaysOnTop", False)))
            self.ekranKutuphane.setBackgroundBrush(self.settings.value("kutuphaneArkaPlanRengi", QColor(Qt.lightGray)))
            self.cModel.treeViewIkonBoyutu = self.settings.value("treeViewIkonBoyutu", QSize(48, 48))
            self.sayfalarDWTreeView.setIconSize(self.cModel.treeViewIkonBoyutu)

        self.settings.endGroup()

        self.settings.beginGroup("StylePresets")
        for group in self.settings.childGroups():
            self.settings.beginGroup(group)

            self._add_style_preset_to_list_widget(presetName=self.settings.value("text"),
                                                  fg=self.settings.value("foreground"),
                                                  bg=self.settings.value("background"),
                                                  cizgiRengi=self.settings.value("cizgiRengi"),
                                                  pen=self.settings.value("pen"),
                                                  font=self.settings.value("font"))

            self.settings.endGroup()
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    def yaz_ayarlar(self):
        self.settings.beginGroup("GuiSettings")
        self.settings.setValue("winGeometry", self.saveGeometry())
        self.settings.setValue("winState", self.saveState(0))  # version=0
        self.settings.setValue("alwaysOnTop", shared.unicode_to_bool(self.actionAlwaysOnTopToggle.isChecked()))
        self.settings.setValue("kutuphaneArkaPlanRengi", self.ekranKutuphane.backgroundBrush().color())
        self.settings.setValue("treeViewIkonBoyutu", self.cModel.treeViewIkonBoyutu)

        self.settings.endGroup()

        self.settings.beginGroup("UserSettings")
        self.settings.setValue("sonKlasor", self.sonKlasor)
        self.settings.setValue("sonKlasorResimler", self.sonKlasorResimler)
        self.settings.setValue("sonKlasorVideolar", self.sonKlasorVideolar)
        self.settings.setValue("sonKlasorDosyalar", self.sonKlasorDosyalar)
        self.settings.setValue("sonKlasorDisaAktar", self.sonKlasorDisaAktar)
        self.settings.setValue("sonKlasorHTML", self.sonKlasorHTML)
        self.settings.setValue("itemSize", self.itemSize)
        self.settings.setValue("textSize", self.textSize)
        self.settings.setValue("baskiCerceveRengi", self.baskiCerceveRengi)
        self.settings.setValue("currentFont", self.fontCBox_tbar.currentFont())
        # self.settings.setValue("currentFont", self.fontCBox_tbar.currentText())
        # self.settings.setValue("currentFont", self.fontCBox_yazidw.currentText())
        self.settings.endGroup()

        self.settings.beginGroup("RecentFilePaths")
        for i, filePath in enumerate(self.recentFilesQueue):
            self.settings.setValue(("%s" % i), filePath)
        self.settings.endGroup()

        self.settings.beginGroup("StylePresets")
        presetList = self.get_style_presets_list_for_saving_binary()
        self.settings.remove("")
        if presetList:
            for i, preset in enumerate(presetList):
                self.settings.beginGroup(str(i))
                self.settings.setValue("text", preset[0])
                self.settings.setValue("foreground", preset[1])
                self.settings.setValue("background", preset[2])
                self.settings.setValue("pen", preset[3])
                self.settings.setValue("font", preset[4])
                self.settings.setValue("cizgiRengi", preset[5])
                self.settings.endGroup()
        self.settings.endGroup()

        self.settings.beginGroup("YaziRengiButonlari")
        for i, btn in enumerate(self.yazi_rengi_btn_liste):
            self.settings.setValue("{}".format(i), btn.renk)
        self.settings.endGroup()

        self.settings.beginGroup("NesneArkaplanRengiButonlari")
        for i, btn in enumerate(self.nesne_arkaplan_rengi_btn_liste):
            self.settings.setValue("{}".format(i), btn.renk)
        self.settings.endGroup()

        self.settings.beginGroup("CizgiRengiButonlari")
        for i, btn in enumerate(self.cizgi_rengi_btn_liste):
            self.settings.setValue("{}".format(i), btn.renk)
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    def oku_arac_ayarlari(self):
        # ilk acilista problem degil, ayar dosyasi yoksa dongude yok
        sozlukler = {}
        self.settingsAraclar.beginGroup("AracOzellikleri")
        for arac_tip in self.settingsAraclar.childGroups():
            self.settingsAraclar.beginGroup(arac_tip)
            sozlukler[arac_tip] = {
                "kalem": self.settingsAraclar.value("kalem"),
                "yaziTipi": self.settingsAraclar.value("yaziTipi"),
                "arkaPlanRengi": self.settingsAraclar.value("arkaPlanRengi"),
                "yaziRengi": self.settingsAraclar.value("yaziRengi"),
                "cizgiRengi": self.settingsAraclar.value("cizgiRengi"),
                "yaziHiza": self.settingsAraclar.value("yaziHiza"),
                "karakter_bicimi_sozluk": self.settingsAraclar.value("karakter_bicimi_sozluk")}
            self.settingsAraclar.endGroup()
        self.settingsAraclar.endGroup()
        self.cScene.arac_ozellikleri_yukle(sozlukler)

    # ---------------------------------------------------------------------
    def yaz_arac_ayarlari(self):
        self.settingsAraclar.beginGroup("AracOzellikleri")
        for arac in self.cScene.araclar:
            self.settingsAraclar.beginGroup(arac.tip)
            self.settingsAraclar.setValue("kalem", arac.kalem)
            self.settingsAraclar.setValue("yaziTipi", arac.yaziTipi)
            self.settingsAraclar.setValue("arkaPlanRengi", arac.arkaPlanRengi)
            self.settingsAraclar.setValue("yaziRengi", arac.yaziRengi)
            self.settingsAraclar.setValue("cizgiRengi", arac.cizgiRengi)
            self.settingsAraclar.setValue("yaziHiza", int(arac.yaziHiza))
            self.settingsAraclar.setValue("karakter_bicimi_sozluk", arac.karakter_bicimi_sozluk)
            self.settingsAraclar.endGroup()
        self.settingsAraclar.endGroup()

    # ---------------------------------------------------------------------
    def clean_temp_dirs(self):
        for tempDirPath in self.tabWidget.get_all_widgets_temp_dir_paths():
            # if os.path.exists(tab.scene().tempDirPath):
            try:
                shutil.rmtree(tempDirPath)
            except Exception as e:
                pass

    # ---------------------------------------------------------------------
    def closeEvent(self, event):

        # TODO: her sahne undo stack clean changed te dokuman degisikligi ref count ile tutulabilir
        # ve bir listede falan toplanabilirler eger bu ilerde yavasliga sebep olursa.

        # burda olasi butun dokumanlarin olasi butun sayfalarinin sahnelerin stackleri undoGroupta tutulduğu için
        # for dongusunde butun tablarin treeModel.degismis_sayfa_var_mi() metodunu kullanmaktan daha direkt bir yaklasim
        degisen_sahne_var_mi = False
        for stack in self.undoGroup.stacks():
            if not stack.isClean():
                degisen_sahne_var_mi = True
                break

        if degisen_sahne_var_mi:
            cvp = self.do_you_want_to_save_for_close_event()
            if cvp == "d":
                self.yaz_ayarlar()
                self.yaz_arac_ayarlari()
                self.clean_temp_dirs()
                self.clean_download_threads()
                # 1-) bu PyQt5 te yoktu. PySide6 ye gecince gerekti. Baglantiyi koparmazsak event.accept dedikten sonra
                # secim degisti metuduna gidip self.cScene bulamiyor
                # 2-)ayrica undoStack cleanChanged sinyaline bagli star_modified_tabs calisiyor ve yine problem. bunu da
                # eklemek gereketi
                # self.cScene.selectionChanged.disconnect()
                # !!- ) sayfa.scene.setParent(None) disconnectlere olan ihtiyaci ortadan kaldirdi
                for model in self.tabWidget.modeller:
                    for sayfa in model.sayfalar():
                        sayfa.scene.setParent(None)
                        # sayfa.scene.selectionChanged.disconnect()
                        # sayfa.scene.undoStack.cleanChanged.disconnect()

                # for stack in self.undoGroup.stacks():
                #     stack.cleanChanged.disconnect()

                event.accept()

            elif cvp == "c":
                event.ignore()
        else:
            self.yaz_ayarlar()
            self.yaz_arac_ayarlari()
            self.clean_temp_dirs()
            self.clean_download_threads()
            for model in self.tabWidget.modeller:
                for sayfa in model.sayfalar():
                    sayfa.scene.setParent(None)
                    # sayfa.scene.selectionChanged.disconnect()
                    # sayfa.scene.undoStack.cleanChanged.disconnect()
            event.accept()

    # ---------------------------------------------------------------------
    @Slot(int)
    def close_selected_tab(self, index):

        # scene = self.tabWidget.widget(index).scene()
        # path = scene.saveFilePath
        # blocklari koyuyoruz cunku sayfa silme esnasinda focus_current_tab_and_change_window_name e falan atliyor.

        # self.tabWidget.setUpdatesEnabled(False)
        with signals_blocked(self.tabWidget):

            # path = self.cModel.saveFilePath
            x_dugmesine_tiklanan_model = self.tabWidget.modeller[index]
            path = x_dugmesine_tiklanan_model.saveFilePath

            # undGroup kullanmiyoruz cunku baska tab aktif iken aktif olmayan tabin x butonuna tiklayinca
            # aktif tabin bilgileri islenebilir!!
            # if self.undoGroup.isClean():
            if x_dugmesine_tiklanan_model.degismis_sayfa_var_mi():

                cvp = self.do_you_want_to_save()

                if cvp == "d":
                    self.clean_download_threads()
                    self._remove_tab(index)
                    if path:
                        self.move_or_append_left_in_recent_files_queue(path)

                elif cvp == "c":
                    return

                elif cvp == "s":
                    self.clean_download_threads()
                    varsa_ayni_adresteki_dosya_silinsin_mi = False
                    if not path:
                        path, varsa_ayni_adresteki_dosya_silinsin_mi = self._get_def_file_save_path()
                    if path:
                        if self.save_file(zipDosyaTamAdres=path,
                                          cModel=x_dugmesine_tiklanan_model,
                                          varsa_ayni_adresteki_dosya_silinsin_mi=varsa_ayni_adresteki_dosya_silinsin_mi,
                                          isSaveAs=False):
                            self._remove_tab(index)
                            self.move_or_append_left_in_recent_files_queue(path)

            else:

                self.clean_download_threads()
                self._remove_tab(index)
                if path:
                    self.move_or_append_left_in_recent_files_queue(path)

        # self.tabWidget.setUpdatesEnabled(True)

        self.focus_current_tab_and_change_window_name(self.tabWidget.currentIndex())

    # ---------------------------------------------------------------------
    def _remove_tab(self, idx):

        # view = self.tabWidget.widget(index)
        # scene = view.scene()

        model = self.tabWidget.modeller[idx]
        try:
            shutil.rmtree(model.tempDirPath)
        except Exception as e:
            pass

        with signals_updates_blocked(self.tabWidget):
            self.tabWidget.removeTab(idx)  # bu ustte olmasi lazim, once remove ediyoruz,
            # yoksa asagida model_sil, view.setParent(None) yapinca, 2 tab birden gidiyor ve hala tab viewi gosteririken
            # problemler
            with signals_blocked(self.undoGroup):
                # icerde undogroup icindeki undostacklar remove ediliyor grouptan,
                # bu da setmodified ve starmoddifiedlari falan cagiriyor o yuzden blockluyoruz.
                self.tw_modeli_ve_sayfalari_sil(model)
            # :) yukarda cModel gondermemek lazim, yoksa secili olmayan tabin X ine tiklaninca
            # bi suru problem.. dikkat..

        if self.tabWidget.count() == 0:
            self.create_tab()

    # ---------------------------------------------------------------------
    def olustur_tab_widget(self):

        baseTabWidget = QWidget(self)
        self.setCentralWidget(baseTabWidget)
        layout = QVBoxLayout(baseTabWidget)
        baseTabWidget.setLayout(layout)

        self.tabWidget = TabWidget(baseTabWidget)
        # self.tabWidget = TabWidget(self)
        # self.setCentralWidget(self.tabWidget)
        self.tabWidget.setDocumentMode(True)
        layout.addWidget(self.tabWidget)

        self.tabBar = TabBar(self.tabWidget)
        # TODO:
        self.tabBar.tabMoved.connect(self.tabWidget.model_sira_degistir)
        # TODO:
        # self.tabBar.setStyleSheet("QTabBar::tab:selected{ background: %s;}" % self.colorActiveTabBg.name())
        self.tabWidget.setTabBar(self.tabBar)
        self.create_tab()
        self.setWindowTitle("%s %s  -  %s" % ("Defter", VERSION, self.tabWidget.tabText(self.tabWidget.currentIndex())))
        self.tabWidget.tabCloseRequested.connect(self.close_selected_tab)
        self.tabWidget.currentChanged.connect(self.focus_current_tab_and_change_window_name)

        self.tabBar.tabLeftMiniButtonClicked.connect(self.create_tab)
        self.tabBar.filesDroppedToTabBar.connect(self.act_open_drag_dropped_def_files)
        ########################################################################
        # self.modifedTabs = []
        self.modifedTabs = 0

    # ---------------------------------------------------------------------
    def on_clipboard_data_changed(self):
        # if self.clipboard.mimeData().hasItem:
        # print("data changed on clipboard")
        # self.actionPaste.setEnabled(True)
        mimeData = self.clipboard.mimeData()
        if any((mimeData.hasText(), mimeData.hasHtml(), mimeData.hasImage(), mimeData.data('scene/items'))):
            self.actionPaste.setEnabled(True)
        else:
            self.actionPaste.setEnabled(False)

        if mimeData.hasText() or mimeData.hasHtml():
            self.actionPasteAsPlainText.setEnabled(True)
        else:
            self.actionPasteAsPlainText.setEnabled(False)
        # if mimeData.data('scene/items') or mimeData.hasText() or mimeData.hasHtml or mimeData.hasImage():
        # program kapanip acilinca, mimeData.data('scene/items') --> b'' donduruyor. ve None olmuyor boylece,
        # dolayisiyla gerek yok, demek tutmuyor item bilgisini program kapaninca.

    # ---------------------------------------------------------------------
    def create_tab(self, tempDirPath=None):

        # dokumana tempDirPath none giderse dokuman olusturuyor yeni bi tane tempDirPath
        # o yuzden dokumanin pathi gonderiliyor
        # scene, view = self.create_scene(dokuman.tempDirPath)
        # dokuman.sayfa_ekle(scene, view, parent=None)
        self.cModel = self.tabWidget.model_ekle(tempDirPath)

        # self.sayfalarDWTreeView.setUpdatesEnabled(False)
        self.cModel.nesneDegisti.connect(self.tv_nesne_degisti)

        with signals_updates_blocked(self.sayfalarDWTreeView):
            self.sayfalarDWTreeView.setModel(self.cModel)

        #  bunu burda olusturmak lazım, sayfa = self.tw_sayfa_ekle() kullanmadan
        # sayfa eklede yaparsak tab ekleyemiyoruz, degistiri cagırıyor falan
        # o da tab remove edip yeni ekliyor ve de hep tek tab kalıyor, uzun hikaye
        scene, view = self.create_scene(self.cModel.tempDirPath)
        parentItem = self.cModel.kokSayfa
        satir = 0
        sayfa = self.cModel.sayfa_ekle(satir=satir,
                                       scene=scene,
                                       view=view,
                                       ustSayfa=parentItem,
                                       ikon=self.tw_get_page_as_icon()
                                       )

        self.tabWidget.tab_olustur(view, self.cModel.fileName, sayfa.adi)

        # bu sayfa degistiri cagircak o da ilk widgeti ekeleycek.
        with signals_blocked(self.sayfalarDWTreeView):
            self.sayfalarDWTreeView.sayfayi_sec_ve_current_index_yap(sayfa)

        # print(self.tabWidget.currentIndex(), "iindexx")
        # self.sayfalarDWTreeView.setUpdatesEnabled(True)

        # self.cModel.nesneDegisti.connect(self.tv_nesne_degisti)

        # TODO: bunu daha duzgun yapalim
        # buna gerek kalmadı, cmodel ve scene giden temDir ayni.. bi bakilabilir.. dursun simdilik.
        # sayfa.scene.tempDirPath = self.cModel.tempDirPath

    # # ---------------------------------------------------------------------
    # def yazyaz(self, bir=None, iki=None):
    #     print("sahne silindi", bir, iki)

    # ---------------------------------------------------------------------
    def create_scene(self, tempDirPath):

        # scene = QGraphicsScene(self)  # veya self.cScene =  .. parent etmezsek selfe

        scene = Scene(tempDirPath, QFont(self.currentFont), self)
        # scene.setSceneRect(QRectF(0, 0, 400, 600))
        # scene.destroyed.connect(self.yazyaz)

        # self.cScene.textItemSelected.connect(self.text_item_selected)
        view = View(scene, self)

        self.cScene = scene
        self.oku_arac_ayarlari()
        self.cView = view
        self.cView.baski_cerceve_rengi_kur(self.baskiCerceveRengi)
        # view.setViewport(QGLWidget())
        # view.show()

        # self.tabWidget.setUpdatesEnabled(False)
        # self.tabWidget.addTab(view, "untitled")
        # scene.saveFilePath = None

        # scene.modified.connect(lambda throw_away=0: self.star_modified_tabs(view))
        scene.undoStack.cleanChanged.connect(self.star_modified_scenes)
        scene.selectionChanged.connect(self.on_scene_selection_changed)

        # TODO: burayi bir debug etmeli bi kac defa alt atirlardan buraya atliyor.
        # setActiveStack i grubun en aştina mi alsak

        with signals_blocked(self.undoGroup):
            self.undoGroup.addStack(scene.undoStack)
            self.undoGroup.setActiveStack(scene.undoStack)

        # if view.isVisible():
        # normalde ilk acilista view visible olmadigindan bu asamada
        # kontrol ediyorduk, ama main window showdan sonraya taşıdık ilk
        # scene rect set etmeyi. yani ilk açılışta bu yanlış set ediyor
        # ama hemen ardından main windows showdan sonra dogru set ediliyor.
        # onun haricinde de, sifir tab kalmiskan otomatik yeni tab olusturma
        # durumunda da tab methodun bu kısmına gelene kadar olusturulmus
        # ve tabwidgetta eklenmiş ve gorolur halde oldugundan if kontrolune gerek kalmiyor.

        # TODO: bu daha sahnede aktif degil belki de ondan diktorgen oluyor ilk yuklenince
        scene.setSceneRect(self.cView.get_visible_rect())

        return scene, view

    # ---------------------------------------------------------------------
    def clean_changed(self, temiz_mi):

        idx = self.tabWidget.currentIndex()
        # if temiz_mi:
        if self.tabWidget.cModel.degismis_sayfa_var_mi():

            self.tabBar.setTabTextColor(idx, shared.renk_degismis_nesne_yazi_rengi)

            self.actionSaveFile.setEnabled(True)
            if self.cModel.saveFilePath:
                self.actionSaveAsFile.setEnabled(True)
            else:
                self.actionSaveAsFile.setEnabled(True)

        else:
            self.tabBar.setTabTextColor(idx, self.tabBar.palette().color(QPalette.Text))

            self.actionSaveFile.setEnabled(False)
            if self.cModel.saveFilePath:
                self.actionSaveAsFile.setEnabled(True)
            else:
                self.actionSaveAsFile.setEnabled(False)

    # # ---------------------------------------------------------------------
    # @Slot(int)
    # def act_files_dropped_to_tabbar(self, urls, isSourceExternal):
    #
    #     for url in urls:
    #         path = url.toLocalFile()
    #         if self.open_file_in_new_TAB(path, isExternalFile=isSourceExternal):
    #             if isSourceExternal:
    #                 if path not in self.externalFilesList:
    #                     self.externalFilesList.append(path)

    # ---------------------------------------------------------------------
    @Slot(bool)
    # TODO: bu belkide iptal edilebilir yukardaki, is gorebilir
    # yani : kaydedince_butun_yildizlari_sil, Yalnız, sahnede undo yapinca o sahne değişikliksiz
    # hale gelince durumunu unutmamak lazım
    def star_modified_scenes(self, temiz_mi):
        # self.sayfalarDWTreeView.blockSignals(True)
        sayfa = self.sayfalarDWTreeView.get_current_sayfa()
        itemText = sayfa.adi

        if temiz_mi:
            if itemText[0] == "★":
                sayfa.adi = itemText[2:]
                # sayfa.yaziRengi = QColor(0,0,0)
        else:
            if not itemText[0] == "★":
                sayfa.adi = ("★ %s" % itemText)
                # sayfa.yaziRengi = QColor(Qt.red)

        # TODO: bunu baska yere tasisak mi
        # mesela sayfa propertylerine, her degisiklik icin gerek var mi ki.
        # bir de currentindex diyoruz.. degisir mi..
        idx = self.sayfalarDWTreeView.currentIndex()
        self.sayfalarDWTreeView.dataChanged(idx, idx)

        # if self.cScene.isModified():
        #     text = ("★ %s" % item.text(0))
        #     if not itemText[0] == "★":
        #         item.setText(0, text)
        #         item.setForeground(0, Qt.blue)
        # else:
        #     if itemText[0] == "★":
        #         item.setText(0, itemText[2:])
        #         item.setForeground(0, Qt.black)

        # self.sayfalarDWTreeView.blockSignals(False)
        self.pencere_ve_tab_yazilarini_guncelle()

    # ---------------------------------------------------------------------
    def pencere_ve_tab_yazilarini_guncelle(self):
        # TODO: ilk acilista 2 defa cagriliyor ard arda.
        idx = self.tabWidget.currentIndex()
        yazi = "{} - {}".format(self.cModel.fileName, self.sayfalarDWTreeView.get_current_sayfa().adi.replace("★ ", ""))

        self.setWindowTitle("%s %s  -  %s" % ("Defter", VERSION, yazi))

        self.tabBar.setTabText(idx, yazi)  #
        # ---------------------------------------------------------------------
        if self.tabWidget.cModel.degismis_sayfa_var_mi():
            self.tabBar.setTabTextColor(idx, shared.renk_degismis_nesne_yazi_rengi)
        else:
            self.tabBar.setTabTextColor(idx, self.tabBar.palette().color(QPalette.Text))
        # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    @Slot(int)
    def focus_current_tab_and_change_window_name(self, idx):

        # print(len(self.tabWidget.modeller), "dok,",
        #       len(self.cModel.sayfalar), "sayfa,",
        #       self.cModel.no, "focusta")

        self.setWindowTitle("%s %s  -  %s" % ("Defter", VERSION, self.tabWidget.tabText(idx)))

        # if self.tabWidget.count() > 0:
        if self.tabWidget.count():
            # self.cModel = self.tabWidget.cModel = self.tabWidget.modeller[idx]
            self.cModel = self.tabWidget.modeller[idx]
            self.tabWidget.cModel = self.tabWidget.modeller[idx]
            # self.cModel = self.tabWidget.cModel

            with signals_blocked(self.sayfalarDWTreeView):
                self.sayfalarDWTreeView.setModel(self.cModel)

                self.sayfalarDWTreeView.setIconSize(self.cModel.treeViewIkonBoyutu)

                if self.cModel.enSonAktifSayfa:
                    # self.sayfalarDWTreeView.sayfayi_sec_ve_current_index_yap(self.cModel.enSonAktifSayfa)
                    self.sayfalarDWTreeView.sayfayi_current_index_yap(self.cModel.enSonAktifSayfa)
                    self.sayfalarDWTreeView.sayfayi_expand_et(self.cModel.enSonAktifSayfa.parent())

            self.cView = self.tabWidget.currentWidget()
            self.cScene = self.cView.scene()
            self.cScene.setFocus()
            self.undoGroup.setActiveStack(self.cScene.undoStack)
            # act_switch_to_selection_tool secimi sifirladigi icin bu sekilde tercih ettik
            # mesela kalem aracinda iken sayfa degisirse arac secili kaliyor ama secim araci arkaplanda
            # secilmis oldugudan tekrar kaleme tiklamak gerekiyor cizim icin
            self.cScene.secim_aracina_gec()

            try:
                self.sahneKutuphane.tempDirPath = self.cModel.tempDirPath
                self.sahneKutuphane.asil_sahne = self.cScene
                # list(self.cModel.sayfalar()) cunku generator, ilk islemde tuketiyoruz, sonra problem
                self.sahneKutuphane.sayfalar = list(self.cModel.sayfalar())
            except AttributeError:
                print("ilk açılışta problem olmasin diye.")

            # print("--",len(self.tabWidget.modeller), "dok,",
            #       len(self.cModel.sayfalar), "sayfa,",
            #       self.cModel.no, "focusta")

            # self.tw_populate_tree_root(self.cModel.sayfalar)

    # ---------------------------------------------------------------------
    def rec_modify_image_items_paths_in_dict_for_import(self, itemDictList, prefix):

        """ modifies sceneDict in act_import_def_files_into_current_def_file"""

        for itemDict in itemDictList:
            if itemDict["type"] == Image.Type and itemDict["isEmbeded"]:
                yeniBaseName = "{}_{}".format(prefix, os.path.basename(itemDict["filePath"]))
                itemDict["filePath"] = os.path.join(os.path.dirname(itemDict["filePath"]), yeniBaseName)
            elif itemDict["type"] == shared.GROUP_ITEM_TYPE:
                self.rec_modify_image_items_paths_in_dict_for_import(itemDict["group_children"], prefix)

            if "children" in itemDict:
                self.rec_modify_image_items_paths_in_dict_for_import(itemDict["children"], prefix)

    # ---------------------------------------------------------------------
    @Slot(bool)
    def act_import_def_files_into_current_def_file(self):
        fn = QFileDialog.getOpenFileNames(self,
                                          self.tr("Import Def File(s)..."),
                                          self.sonKlasor,
                                          self.tr('def Files (*.def)'))

        # if fn:
        if fn[0]:
            defPaths = fn[0]

            self.sonKlasor = os.path.dirname(defPaths[0])

        else:
            return

        self.import_def_files_into_current_def_file(defPaths)

    # ---------------------------------------------------------------------
    def import_def_files_into_current_def_file(self, filePathList):
        """bir cok def dosyasini açıp belgeye eklemek için"""
        self.lutfen_bekleyin_goster()
        self.cScene._acceptDrops = False
        self.tabBar.setAcceptDrops(False)

        # dosyalari bir for loopunda aciyoruz dolayisi ile hata olursa,
        # normalde return deyip bu methodtan çıkacağımıza, continue deyip, döngüdeki bir sonraki dosyaya geciyoruz.
        for zipFilePath in filePathList:
            tempDirPath = tempfile.mkdtemp(prefix="defter-tmp")
            try:
                shutil.unpack_archive(zipFilePath, tempDirPath, "zip")
            except Exception as e:
                hata = self.tr('Could not import file  --   "{0:s}"\n{1:s}').format(zipFilePath, str(e))
                self.log(hata, 5000, 3, dialog=True)
                continue

            # fileName = os.path.basename(zipFilePath)
            fileName = "sayfa"
            filePath = os.path.join(tempDirPath, fileName)
            _file = QFile(filePath)
            # if not _file.open(QIODevice.ReadOnly | QIODevice.Text): # QIODevice.Text - eger json load edersek diye.
            if not _file.open(QIODevice.ReadOnly):
                hata = self.tr('Could not open file  --   "{0:s}"\n{1:s}').format(filePath, _file.errorString())
                self.log(hata, 5000, 3, dialog=True)
                continue

            # read the serialized data from the file
            fromFileStream = QDataStream(_file)
            fromFileStream.setVersion(QDataStream.Qt_5_7)
            magic = fromFileStream.readInt32()
            if magic != DEF_MAGIC_NUMBER:
                # raise IOError("unrecognized file type")
                hata = self.tr('Could not open file  --   "{0:s}"\nUnrecognized file type!').format(
                    os.path.basename(filePath))
                self.log(hata, 6000, 3, dialog=True)
                # return
                continue
            version = fromFileStream.readInt16()
            if version > DEF_FILE_VERSION:
                # print("old file")
                pass
            if version > DEF_FILE_VERSION:
                # print("new file")
                pass

            # onceden readRawData kullaniyorduk, PySide6 ye gecince << kullanmak gerekti.
            # o yuzden bytearray lengthe de ihtiyac kalmadi. (Okurken problem oluyor.)
            # read byteArrayLength
            # bArrayLength = fromFileStream.readUInt64()
            # compressedBArray = fromFileStream.readRawData(bArrayLength)

            compressedBArray = QByteArray()
            fromFileStream >> compressedBArray
            unCompressedBArray = qUncompress(compressedBArray)

            tempStream = QDataStream(unCompressedBArray, QIODevice.ReadWrite)
            tempStream.setVersion(QDataStream.Qt_5_7)
            dokumanDict = tempStream.readQVariant()

            # _file.flush()
            _file.close()

            # TODO: hata mesaji guzellestir.
            if not dokumanDict:
                hata = self.tr('Could not open file  --   "{0:s}"\nFile could not be parsed!').format(
                    os.path.basename(zipFilePath))
                self.log(hata, 6000, 3, dialog=True)
                # return False
                continue

            # import edilen dosyanin temp klasorunden diger ic resource klasorlerini kopyala
            prefix = os.path.splitext(os.path.basename(zipFilePath))[0]
            for entry in os.scandir(tempDirPath):  # entry is a os.DirEntry object
                if entry.is_dir():
                    currentSceneResourceTempFolderPath = os.path.join(self.cScene.tempDirPath, entry.name)
                    if not os.path.isdir(currentSceneResourceTempFolderPath):
                        os.makedirs(currentSceneResourceTempFolderPath)
                    for innerEntry in os.scandir(entry.path):
                        yeniName = "{}_{}".format(prefix, innerEntry.name)
                        destPath = os.path.join(currentSceneResourceTempFolderPath, yeniName)
                        if not os.path.isfile(destPath):  # ust uste 2 defa embed edilirse diye
                            shutil.copy2(innerEntry.path, destPath)

            for sceneDict in dokumanDict["anaSayfalarList"]:
                self.rec_modify_image_items_paths_in_dict_for_import(sceneDict["itemList"], prefix)

                # self._dict_to_scene de, parenti false ediyoruz dongu icinde, ilk item parenta ekleniyor
                # digerleri son eklenen item secili oldugu ve de parent false oldugu icin, parent icindeki
                # item ile ayni seviyede ekleniyorlar.
                # ve tekrar buraya donuluyor burdan az once giden sayfanin ic_sayfalari bitince,
                # bunlar da anasayfalar oldugundan, en top level itemi seciyoruz ve de top levele donmus oluyoruz
                # cunku tw_sayfa_ekle secili itemin seviyesine ekliyor yeni itemlari.
                # sinyalleri simdilik blocklamaya gerek yok selectionChanged signali kullanmiyoruz cunku.
                # self.sayfalarDWTreeView.blockSignals(True)

                # self.sayfalarDWTreeView.setCurrentItem(self.sayfalarDWTreeView.topLevelItem(0))

                # self.sayfalarDWTreeView.blockSignals(False)
                self._dict_to_scene(sceneDict, parent=self.cModel.kokSayfa, altSayfaSeklindeEkle=False)
                # TODO : bu alltakine bak
                self.cScene.unite_with_scene_rect(sceneDict["sceneRect"])

            self.sayfalarDWTreeView.sayfayi_expand_et(self.cModel.enSonAktifSayfa)
            # self.sayfalarDWTreeView.sayfayi_expand_et(sayfa.parent())
            # self.tv_sayfa_degistir(sayfa)

            self.ekle_sil_butonlari_guncelle()

            # for itemDict in sceneDict["itemList"]:
            #     if itemDict["type"] == shared.GROUP_ITEM_TYPE:
            #         group = self.add_item_to_scene_from_dict(itemDict)
            #         self.dict_to_scene_recursive_group(itemDict["group_children"], group)
            #
            #         if "children" in itemDict:
            #             self.dict_to_scene_recursive_parent(itemDict["children"], group)
            #         group.updateBoundingRect()
            #         group.setScale(itemDict["scale"])
            #
            #     else:
            #         item = self.add_item_to_scene_from_dict(itemDict)
            #         if "children" in itemDict:
            #             self.dict_to_scene_recursive_parent(itemDict["children"], item)

            self.log('{0:s} succesfully loaded!'.format(self.cModel.fileName), 5000, 1)

            try:
                shutil.rmtree(tempDirPath)
            except Exception as e:
                pass

        self.lutfen_bekleyin_gizle()
        # self.log("%s succesfully loaded!" % os.path.basename(filePath), 5000, toStatusBarOnly=True)
        # self.cView.zoomToFit()
        self.cScene._acceptDrops = True
        self.tabBar.setAcceptDrops(True)

    # ---------------------------------------------------------------------
    @Slot(list)
    def act_open_drag_dropped_def_files(self, filePathList):
        for zipFilePath in filePathList:
            self.act_open_def_file(zipFilePath)

    # ---------------------------------------------------------------------
    @Slot(bool)
    def act_open_def_file(self, zipFilePath=None):
        if not zipFilePath:
            # options = QFileDialog.Options()
            # options ^= QFileDialog.DontUseNativeDialog
            filtre = self.tr('def Files (*.def);;All Files(*)')
            fn = QFileDialog.getOpenFileName(self,
                                             self.tr('Open File...'),
                                             self.sonKlasor,
                                             filtre)
            if fn[0]:
                zipFilePath = fn[0]
            else:
                return

        if not self.tabWidget.set_current_widget_with_path(zipFilePath):
            self.lutfen_bekleyin_goster()

            tempDirPath = tempfile.mkdtemp(prefix="defter-tmp")
            try:
                shutil.unpack_archive(zipFilePath, tempDirPath, "zip")
            except Exception as e:
                self.lutfen_bekleyin_gizle()
                hata = self.tr('Could not import file  --   "{0:s}"\n{1:s}').format(zipFilePath, str(e))
                self.log(hata, 5000, 3, dialog=True)
                return False

            # fileName = os.path.basename(zipFilePath)
            fileName = "sayfa"
            filePath = os.path.join(tempDirPath, fileName)
            _file = QFile(filePath)
            # if not _file.open(QIODevice.ReadOnly | QIODevice.Text): # QIODevice.Text - eger json load edersek diye.
            if not _file.open(QIODevice.ReadOnly):
                self.lutfen_bekleyin_gizle()
                hata = self.tr('Could not open file  --   "{0:s}"\n{1:s}').format(filePath, _file.errorString())
                self.log(hata, 5000, 3, dialog=True)
                return False

            # read the serialized data from the file
            fromFileStream = QDataStream(_file)
            fromFileStream.setVersion(QDataStream.Qt_5_7)
            magic = fromFileStream.readInt32()
            if magic != DEF_MAGIC_NUMBER:
                # raise IOError("unrecognized file type")
                self.log(self.tr('{0:s} : Unrecognized file type!').format(os.path.basename(filePath)), 6000, 3)
                self.lutfen_bekleyin_gizle()
                hata = self.tr('Could not open file  --   "{0:s}"'
                               '\nUnrecognized file type!').format(os.path.basename(filePath))
                self.log(hata, 6000, 3, dialog=True)
                return
            version = fromFileStream.readInt16()
            if version > DEF_FILE_VERSION:
                # print("old file")
                pass
            if version > DEF_FILE_VERSION:
                # print("new file")
                pass

            # onceden readRawData kullaniyorduk, PySide6 ye gecince << kullanmak gerekti.
            # o yuzden bytearray lengthe de ihtiyac kalmadi. (Okurken problem oluyor.)
            # read byteArrayLength
            # bArrayLength = fromFileStream.readUInt64()
            # compressedBArray = fromFileStream.readRawData(bArrayLength)

            compressedBArray = QByteArray()
            fromFileStream >> compressedBArray
            unCompressedBArray = qUncompress(compressedBArray)

            tempStream = QDataStream(unCompressedBArray, QIODevice.ReadWrite)
            tempStream.setVersion(QDataStream.Qt_5_7)
            dokumanDict = tempStream.readQVariant()

            # _file.flush()
            _file.close()

            # TODO: hata mesaji guzellestir.
            if not dokumanDict:
                self.lutfen_bekleyin_gizle()
                hata = self.tr('Could not open file  --   "{0:s}"\nFile could not be parsed!').format(
                    os.path.basename(zipFilePath))
                self.log(hata, 6000, 3, dialog=True)
                return False

            self.dokumanDict_to_dokuman(dokumanDict, tempDirPath=tempDirPath)

            for sayfa in self.cModel.sayfalar():
                sayfa._scene.undoStack.setClean()

            self.cModel.saveFilePath = zipFilePath
            self.cModel.fileName = os.path.basename(zipFilePath)

            self.move_or_append_left_in_recent_files_queue(zipFilePath)

            self.lutfen_bekleyin_gizle()
            # self._statusBar.showMessage("%s succesfully loaded!" % os.path.basename(filePath), 5000)
            self.log(self.tr('{0:s} succesfully loaded!').format(self.cModel.fileName), 5000, 1)

        # else:
        #     self._statusBar.showMessage("%s already opened" % self.cModel.fileName, 5000)

        self.sonKlasor = os.path.dirname(zipFilePath)

    # ---------------------------------------------------------------------
    def add_item_to_scene_from_dict(self, itemDict, isPaste=False):

        itemType = itemDict["type"]

        if itemType == shared.LINE_ITEM_TYPE:
            lineItem = LineItem(pos=itemDict["pos"],
                                pen=itemDict["pen"],
                                yaziRengi=itemDict.get("yaziRengi", QColor(0,0,0)),
                                arkaPlanRengi=itemDict.get("arkaPlanRengi", QColor(255,255,255)),
                                line=itemDict["line"],
                                font=itemDict.get("font", self.font()))
            # TODO: renkler bir sekilde sistem rengine donuyor.
            lineItem.setRotation(itemDict["rotation"])
            lineItem.setText(itemDict.get("text", ""))
            if itemDict.get("yaziHiza", None):
                lineItem.painterTextOption.setAlignment(Qt.Alignment(itemDict.get("yaziHiza")))
            lineItem.setScale(itemDict["scale"])
            lineItem.setZValue(itemDict["zValue"])
            lineItem.isPinned = itemDict["isPinned"]
            lineItem._command = itemDict["command"]

            if isPaste:
                lineItem._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, lineItem)
            else:
                lineItem._kim = itemDict.get("kim")
                lineItem.baglanmis_nesneler = itemDict.get("baglanmis_nesneler")
                # self.cScene.addItem(lineItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, lineItem)
                self.cScene.addItem(lineItem)
            return lineItem

        elif itemType == shared.RECT_ITEM_TYPE:
            rectItem = Rect(itemDict["pos"], itemDict["rect"], itemDict["yaziRengi"], itemDict["arkaPlanRengi"],
                            itemDict["pen"], itemDict["font"])
            # rectItem.setRect(rectItem.mapRectFromScene(item["rect"]))
            # rectItem.setPos(itemDict["pos"])
            rectItem.setRotation(itemDict["rotation"])
            rectItem.setScale(itemDict["scale"])
            rectItem.setZValue(itemDict["zValue"])
            rectItem.isPinned = itemDict["isPinned"]
            if itemDict.get("yaziHiza", None):
                rectItem.painterTextOption.setAlignment(Qt.Alignment(itemDict.get("yaziHiza")))
            rectItem._text = itemDict["text"]
            rectItem._command = itemDict["command"]

            if isPaste:
                rectItem._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, rectItem)
                # rectItem.setPos(QPointF(itemDict["pos"]))
            else:
                rectItem._kim = itemDict.get("kim")
                # self.cScene.addItem(rectItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, rectItem)
                self.cScene.addItem(rectItem)
                # rectItem.setPos(itemDict["pos"])
            return rectItem

        elif itemType == shared.ELLIPSE_ITEM_TYPE:
            ellipseItem = Ellipse(itemDict["pos"], itemDict["rect"], itemDict["yaziRengi"], itemDict["arkaPlanRengi"],
                                  itemDict["pen"], itemDict["font"])
            ellipseItem.setPos(itemDict["pos"])
            ellipseItem.setRotation(itemDict["rotation"])
            ellipseItem.setScale(itemDict["scale"])
            ellipseItem.setZValue(itemDict["zValue"])
            ellipseItem.isPinned = itemDict["isPinned"]
            if itemDict.get("yaziHiza", None):
                ellipseItem.painterTextOption.setAlignment(Qt.Alignment(itemDict.get("yaziHiza")))
            ellipseItem._text = itemDict["text"]
            ellipseItem._command = itemDict["command"]

            if isPaste:
                ellipseItem._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, ellipseItem)
            else:
                ellipseItem._kim = itemDict.get("kim")
                # self.cScene.addItem(ellipseItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, ellipseItem)
                self.cScene.addItem(ellipseItem)
            return ellipseItem

        elif itemType == shared.PATH_ITEM_TYPE:
            pathItem = PathItem(itemDict["pos"], itemDict["yaziRengi"], itemDict["arkaPlanRengi"], itemDict["pen"],
                                itemDict["font"])
            # TODO: renkler bir sekilde sistem rengine donuyor.
            pathItem.fromList(pathElementsList=itemDict["painterPathAsList"],
                              closePath=itemDict.get("isPathClosed", True))
            pathItem.setRotation(itemDict["rotation"])
            pathItem.setText(itemDict["text"])
            if itemDict.get("yaziHiza", None):
                pathItem.painterTextOption.setAlignment(Qt.Alignment(itemDict.get("yaziHiza")))
            pathItem.setScale(itemDict["scale"])
            pathItem.setZValue(itemDict["zValue"])
            pathItem.isPinned = itemDict["isPinned"]
            pathItem._command = itemDict["command"]

            if isPaste:
                pathItem._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, pathItem)
            else:
                pathItem._kim = itemDict.get("kim")
                # self.cScene.addItem(pathItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, pathItem)
                self.cScene.addItem(pathItem)

            return pathItem

        elif itemType == shared.IMAGE_ITEM_TYPE:
            # rect = item["rect"]
            # pixMap = QPixmap(item["filePath"]).scaled(rect.size().toSize(), Qt.KeepAspectRatio)
            # imageItem = Image(item["filePath"], pixMap, item["rect"], item["arkaPlanRengi"], item["pen"])

            if itemDict["isEmbeded"]:
                # .replace("\\",os.sep) windowsta kaydedilen dosya tam adresi linuxta os.path.basename ile
                # sonuc vermiyor, import ntpath yapmak lazim os path yerine, tabi biz dosya en son
                # nerde kaydedildi bunun bilgisini tutmuyoruz. Simdilik boyle bir cozum.
                filePath = os.path.join(self.cScene.tempDirPath, "images",
                                        os.path.basename(itemDict["filePath"].replace("\\", os.sep)))

                imageItem = Image(filePath, itemDict["pos"], itemDict["rect"], itemDict["yaziRengi"],
                                  itemDict["arkaPlanRengi"],
                                  itemDict["pen"], itemDict["font"], True)
                imageItem.originalSourceFilePath = itemDict["originalSourceFilePath"]
            else:
                imageItem = Image(itemDict["filePath"], itemDict["pos"], itemDict["rect"], itemDict["yaziRengi"],
                                  itemDict["arkaPlanRengi"],
                                  itemDict["pen"], itemDict["font"])

            imageItem.isEmbeded = itemDict["isEmbeded"]
            imageItem.setPos(itemDict["pos"])
            imageItem.setRotation(itemDict["rotation"])
            imageItem.setScale(itemDict["scale"])
            imageItem.setZValue(itemDict["zValue"])
            imageItem.imageOpacity = itemDict["imageOpacity"]
            imageItem.isPinned = itemDict["isPinned"]
            imageItem.isMirrorX = itemDict["isMirrorX"]
            imageItem.isMirrorY = itemDict["isMirrorY"]
            if itemDict.get("yaziHiza", None):
                imageItem.painterTextOption.setAlignment(Qt.Alignment(itemDict.get("yaziHiza")))
            imageItem._text = itemDict["text"]
            imageItem._command = itemDict["command"]
            # imageItem.reload_image_after_scale()

            if isPaste:
                imageItem._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, imageItem)
            else:
                imageItem._kim = itemDict.get("kim")
                # self.cScene.addItem(imageItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, imageItem)
                self.cScene.addItem(imageItem)
            imageItem.reload_image_after_scale()
            # pixMap = None
            return imageItem

        elif itemType == shared.TEXT_ITEM_TYPE:
            textItem = Text(itemDict["pos"], itemDict["yaziRengi"], itemDict["arkaPlanRengi"], itemDict["pen"],
                            itemDict["font"], rect=itemDict["rect"])
            textItem.set_document_url(self.cScene.tempDirPath)
            if itemDict["isPlainText"]:
                textItem.setPlainText(itemDict["text"])
            else:
                textItem.setHtml(itemDict["html"])
                textItem.isPlainText = False
            if itemDict.get("yaziHiza", None):
                option = textItem.doc.defaultTextOption()
                option.setAlignment(Qt.Alignment(itemDict.get("yaziHiza")))
                textItem.doc.setDefaultTextOption(option)
            textItem.textItemFocusedOut.connect(lambda: self.cScene.is_text_item_empty(textItem))
            textItem.setPos(itemDict["pos"])
            textItem.setRotation(itemDict["rotation"])
            textItem.setScale(itemDict["scale"])
            textItem.setZValue(itemDict["zValue"])
            textItem.isPinned = itemDict["isPinned"]
            textItem._command = itemDict["command"]

            if isPaste:
                textItem._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, textItem)
            else:
                textItem._kim = itemDict.get("kim")
                # self.cScene.addItem(textItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, textItem)
                self.cScene.addItem(textItem)
            textItem.setTextInteractionFlags(Qt.NoTextInteraction)
            cursor = textItem.textCursor()
            cursor.clearSelection()
            textItem.setTextCursor(cursor)
            return textItem
            # TODO: item edit edilebilir halde yazi secili kaliyor, ya focus ya text interactionflag

        elif itemType == shared.GROUP_ITEM_TYPE:
            groupItem = Group(itemDict["arkaPlanRengi"], itemDict.get("yaziRengi", QColor(0, 0, 0)), itemDict["pen"])
            # group = QGraphicsItemGroup(None)
            groupItem.setFlags(groupItem.ItemIsSelectable
                               | groupItem.ItemIsMovable
                               # | groupItem.ItemIsFocusable
                               )

            groupItem.setPos(itemDict["pos"])
            groupItem.setRotation(itemDict["rotation"])
            # we set scale later. after group re-populated.
            # groupItem.setScale(itemDict["scale"])
            groupItem.setZValue(itemDict["zValue"])
            groupItem.isPinned = itemDict["isPinned"]

            if isPaste:
                groupItem._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, groupItem)
            else:
                groupItem._kim = itemDict.get("kim")
                # self.cScene.addItem(groupItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, groupItem)
                self.cScene.addItem(groupItem)
            return groupItem

        elif itemType == shared.VIDEO_ITEM_TYPE:
            # rect = item["rect"]
            # pixMap = QPixmap(item["filePath"]).scaled(rect.size().toSize(), Qt.KeepAspectRatio)
            # imageItem = Image(item["filePath"], pixMap, item["rect"], item["arkaPlanRengi"], item["pen"])

            if itemDict["isEmbeded"]:
                filePath = os.path.join(self.cScene.tempDirPath, "videos",
                                        os.path.basename(itemDict["filePath"].replace("\\", os.sep)))
                videoItem = VideoItem(filePath, itemDict["pos"], itemDict["rect"], itemDict["yaziRengi"],
                                      itemDict["arkaPlanRengi"],
                                      itemDict["pen"], itemDict["font"], True)
                videoItem.originalSourceFilePath = itemDict["originalSourceFilePath"]
            else:
                videoItem = VideoItem(itemDict["filePath"], itemDict["pos"], itemDict["rect"], itemDict["yaziRengi"],
                                      itemDict["arkaPlanRengi"],
                                      itemDict["pen"], itemDict["font"])

            videoItem.isEmbeded = itemDict["isEmbeded"]
            videoItem.setPos(itemDict["pos"])
            videoItem.setRotation(itemDict["rotation"])
            videoItem.setScale(itemDict["scale"])
            videoItem.setZValue(itemDict["zValue"])
            # videoItem.imageOpacity = itemDict["imageOpacity"]
            videoItem.isPinned = itemDict["isPinned"]
            # videoItem.isMirrorX = itemDict["isMirrorX"]
            # videoItem.isMirrorY = itemDict["isMirrorY"]
            if itemDict.get("yaziHiza", None):
                videoItem.painterTextOption.setAlignment(Qt.Alignment(itemDict.get("yaziHiza")))
            # videoItem._text = itemDict["text"]
            videoItem.eskiYazi = itemDict["text"]
            videoItem._command = itemDict["command"]
            # videoItem.reload_image_after_scale()

            if isPaste:
                videoItem._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, videoItem)
            else:
                videoItem._kim = itemDict.get("kim")
                # self.cScene.addItem(videoItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, videoItem)
                self.cScene.addItem(videoItem)
            # videoItem.reload_image_after_scale()
            # pixMap = None
            return videoItem

        elif itemType == shared.DOSYA_ITEM_TYPE:
            # rect = item["rect"]
            # pixMap = QPixmap(item["filePath"]).scaled(rect.size().toSize(), Qt.KeepAspectRatio)
            # imageItem = Image(item["filePath"], pixMap, item["rect"], item["arkaPlanRengi"], item["pen"])

            if itemDict["isEmbeded"]:
                filePath = os.path.join(self.cScene.tempDirPath, "files",
                                        os.path.basename(itemDict["filePath"].replace("\\", os.sep)))
                dosyaNesnesi = DosyaNesnesi(filePath, itemDict["pos"], itemDict["rect"], itemDict["yaziRengi"],
                                            itemDict["arkaPlanRengi"],
                                            itemDict["pen"], itemDict["font"], pixmap=None, isEmbeded=True)
                dosyaNesnesi.originalSourceFilePath = itemDict["originalSourceFilePath"]
            else:
                dosyaNesnesi = DosyaNesnesi(itemDict["filePath"], itemDict["pos"], itemDict["rect"],
                                            itemDict["yaziRengi"],
                                            itemDict["arkaPlanRengi"],
                                            itemDict["pen"], itemDict["font"], pixmap=None, isEmbeded=True)

            dosyaNesnesi.isEmbeded = itemDict["isEmbeded"]
            dosyaNesnesi.setPos(itemDict["pos"])
            dosyaNesnesi.setRotation(itemDict["rotation"])
            dosyaNesnesi.setScale(itemDict["scale"])
            dosyaNesnesi.setZValue(itemDict["zValue"])
            # dosyaNesnesi.imageOpacity = itemDict["imageOpacity"]
            dosyaNesnesi.isPinned = itemDict["isPinned"]
            # dosyaNesnesi.isMirrorX = itemDict["isMirrorX"]
            # dosyaNesnesi.isMirrorY = itemDict["isMirrorY"]
            if itemDict.get("yaziHiza", None):
                dosyaNesnesi.painterTextOption.setAlignment(Qt.Alignment(itemDict.get("yaziHiza")))
            dosyaNesnesi._text = itemDict["text"]
            dosyaNesnesi._command = itemDict["command"]
            # dosyaNesnesi.reload_image_after_scale()

            if isPaste:
                dosyaNesnesi._kim = shared.kim(kac_basamak=16)
                undoRedo.undoableAddItem(self.cScene.undoStack, "_paste", self.cScene, dosyaNesnesi)
            else:
                dosyaNesnesi._kim = itemDict.get("kim")
                # self.cScene.addItem(dosyaNesnesi)
                # undoRedo.undoableAddItem(self.cScene.undoStack, "_dosya_yukleme", self.cScene, dosyaNesnesi)
                self.cScene.addItem(dosyaNesnesi)
            # videoItem.reload_image_after_scale()
            # pixMap = None
            return dosyaNesnesi

    # ---------------------------------------------------------------------
    def dict_to_scene_recursive_parent(self, itemDictList, parentItem, isInGroup=False):

        for childDict in itemDictList:

            if childDict["type"] == shared.GROUP_ITEM_TYPE:
                group = self.add_item_to_scene_from_dict(childDict)
                self.dict_to_scene_recursive_group(childDict["group_children"], group)
                group.setParentItem(parentItem)

                # before parented scale / after parented scale
                group.scaleWithOffset(childDict["scale"] / group.scale())

                if parentItem.type() == shared.GROUP_ITEM_TYPE:
                    parentItem.parentedWithParentOperation.append(group)
                if isInGroup:
                    group.setFlag(group.ItemIsSelectable, False)
                    group.setFlag(group.ItemIsMovable, False)
                    group.setFlag(group.ItemIsFocusable, False)

                if "children" in childDict:
                    self.dict_to_scene_recursive_parent(childDict["children"], group)
            else:
                c = self.add_item_to_scene_from_dict(childDict)
                c.setParentItem(parentItem)

                # before parented scale / after parented scale
                # c.scaleWithOffset(childDict["scale"] / c.scale())

                if parentItem.type() == shared.GROUP_ITEM_TYPE:
                    parentItem.parentedWithParentOperation.append(c)
                if isInGroup:
                    c.setFlag(c.ItemIsSelectable, False)
                    c.setFlag(c.ItemIsMovable, False)
                    c.setFlag(c.ItemIsFocusable, False)

                if "children" in childDict:
                    self.dict_to_scene_recursive_parent(childDict["children"], c)

        if parentItem.type() == shared.GROUP_ITEM_TYPE:
            parentItem.updateBoundingRect()

    # ---------------------------------------------------------------------
    def dict_to_scene_recursive_group(self, groupedItemsDictList, group):
        for groupedItemDict in groupedItemsDictList:
            if groupedItemDict["type"] == shared.GROUP_ITEM_TYPE:
                groupedGroup = self.add_item_to_scene_from_dict(groupedItemDict)
                self.dict_to_scene_recursive_group(groupedItemDict["group_children"], groupedGroup)

                if "children" in groupedItemDict:
                    self.dict_to_scene_recursive_parent(groupedItemDict["children"], groupedGroup, isInGroup=True)

                group.addSingleItemToGroup(groupedGroup)

            else:
                groupedItem = self.add_item_to_scene_from_dict(groupedItemDict)
                if "children" in groupedItemDict:
                    self.dict_to_scene_recursive_parent(groupedItemDict["children"], groupedItem, isInGroup=True)
                group.addSingleItemToGroup(groupedItem)
                if group.rotation():
                    groupedItem.rotateWithOffset(groupedItem.rotation() + group.rotation())

        # eklemeyi sonlara tasidigimizdan gerek kalmadi.
        # group.updateBoundingRect()

    # ---------------------------------------------------------------------
    def _dict_to_scene(self, sceneDict, parent, altSayfaSeklindeEkle):
        if altSayfaSeklindeEkle:
            sayfa = self.tw_alt_sayfa_ekle(parentItem=parent)
        else:
            sayfa = self.tw_sayfa_ekle(parentItem=parent)

        sayfa.adi = sceneDict["sayfaAdi"]
        sayfa._kim = sceneDict.get("sayfaKim", None)
        self.sayfalarDWTreeView.get_current_sayfa().adi = sceneDict["sayfaAdi"]
        self.sayfalarDWTreeView.get_current_sayfa()._kim = sceneDict.get("sayfaKim", None)

        # self.tv_sayfa_degistir(self.sayfalarDWTreeView.currentItem(), 0)

        self.cScene.sonZDeger = sceneDict.get("sonZDeger", 0)
        self.cScene.setSceneRect(sceneDict["sceneRect"])
        self.cScene.arac_ozellikleri_yukle(sceneDict.get("aracOzellikleriSozluk", None))
        self.cView.setBackgroundBrush(sceneDict["backgroundBrush"])
        if sceneDict["backgroundImagePath"]:
            self.cView.set_background_image(os.path.join(self.cScene.tempDirPath, "images",
                                                         os.path.basename(
                                                             sceneDict["backgroundImagePath"].replace("\\", os.sep))))
        self.cView.backgroundImagePathIsEmbeded = sceneDict.get("backgroundImagePathIsEmbeded", False)
        # self.cView.setMatrix(sceneDict["viewMatrix"])
        self.cView.setTransform(sceneDict["viewTransform"])
        self.cView.horizontalScrollBar().setValue(sceneDict["viewHorizontalScrollBarValue"])
        self.cView.verticalScrollBar().setValue(sceneDict["viewVerticalScrollBarValue"])

        # self.cScene.undoStack.beginMacro(self.tr("load_page_{}".format(sceneDict["sayfaAdi"])))
        for itemDict in sceneDict["itemList"]:

            if itemDict["type"] == shared.GROUP_ITEM_TYPE:
                group = self.add_item_to_scene_from_dict(itemDict)
                self.dict_to_scene_recursive_group(itemDict["group_children"], group)

                if "children" in itemDict:
                    self.dict_to_scene_recursive_parent(itemDict["children"], group)
                group.updateBoundingRect()
                group.setScale(itemDict["scale"])

            else:
                item = self.add_item_to_scene_from_dict(itemDict)
                if "children" in itemDict:
                    self.dict_to_scene_recursive_parent(itemDict["children"], item)
        # self.cScene.undoStack.endMacro()

        ustSayfa = sayfa
        self.oklari_bagla()
        self.tw_sayfa_guncelle()
        if "ic_sayfalar" in sceneDict:
            # parent = True  # ic_sayfalar ayni seviyede ayni parenta sahip olduklari icin
            # ilk donguden sonra parent false ediyoruz ki, ilk dongude alt sayfa ekliyor,
            # daha sonrakilerde az onceki tw_alt_sayfa_ekle ile eklenenle ayni seviyeye ekleniyorlar.
            for ic_sayfa_sceneDict in sceneDict["ic_sayfalar"]:
                self._dict_to_scene(ic_sayfa_sceneDict, parent=ustSayfa, altSayfaSeklindeEkle=True)
                # parent = False

                # bir de anasayfa ekle ozelligi lazim belki root sayfa ekle gibisinden,,
                # cunku bir katman asagi inince parent olmasa bile ayni katmandan devam ediyor.
            # parent = sayfa.ustSayfa()

    # ---------------------------------------------------------------------
    def oklari_bagla(self):
        for nesne in self.cScene.items():
            # if nesne.type() == LineItem.Type:
            if nesne.type() == shared.LINE_ITEM_TYPE and nesne.baglanmis_nesneler:
                for baglanan_nesne_kimligi, nokta in nesne.baglanmis_nesneler.items():
                    baglanan_nesne = self.cScene._kimlik_nesne_sozluk[baglanan_nesne_kimligi]
                    if 1 == nokta:
                        p1ScenePos = nesne.mapToScene(nesne._line.p1())
                        baglanan_nesne.ok_ekle(nesne, p1ScenePos, 1)
                    if 2 == nokta:
                        p2ScenePos = nesne.mapToScene(nesne._line.p2())
                        baglanan_nesne.ok_ekle(nesne, p2ScenePos, 2)

    # ---------------------------------------------------------------------
    def dokumanDict_to_dokuman(self, dokumanDict, tempDirPath):

        # self.create_tab(tempDirPath)
        # -----------------------------------------------------------------------------------------------------------
        # create_tab kullaniyorduk onceden simdi daha basit bir versiyonunu direkt yazdik.
        self.cModel = self.tabWidget.model_ekle(tempDirPath)
        self.cModel.nesneDegisti.connect(self.tv_nesne_degisti)
        with signals_blocked(self.sayfalarDWTreeView):
            self.sayfalarDWTreeView.setModel(self.cModel)

        # scene, view = self.create_scene(self.cModel.tempDirPath)
        tempWidgetViewYerine = QWidget()
        with signals_blocked(self.tabWidget):  # focus_current_tab_and_change_window_name cagirmasin diye
            self.tabWidget.tab_olustur(tempWidgetViewYerine, self.cModel.fileName, "gecici sayfa")
        # create_tab bitis // asagida tempWidgetViewYerine.deletLater() ve de; del tempWidgetViewYerine var.
        # -----------------------------------------------------------------------------------------------------------

        self.cModel.saveFilePath = dokumanDict["saveFilePath"]
        self.cModel.fileName = dokumanDict["fileName"]
        self.cModel.embededImageCounter = dokumanDict.get("embededImageCounter", 10)
        self.cModel.embededVideoCounter = dokumanDict.get("embededVideoCounter", 10)
        self.cModel.embededFileCounter = dokumanDict.get("embededFileCounter", 0)

        self.cModel.treeViewIkonBoyutu = dokumanDict.get("treeViewIkonBoyutu", QSize(48, 48))
        self.sayfalarDWTreeView.setIconSize(self.cModel.treeViewIkonBoyutu)

        # self.ekranKutuphane.setBackgroundBrush(dokumanDict["kutuphaneBackgroundBrush"])
        self.ekranKutuphane.setBackgroundBrush(dokumanDict.get("kutuphaneBackgroundBrush", Qt.lightGray))
        # self.cDokuman.enSonAktifSayfa = dokumanDict["enSonAktifSayfa"]

        # ilk sayfa create_tab ile ekleniyor, o da dokuman olustuurlurken ekleniyor
        # burdan boyle bir cozum daha basit.

        # print(dokumanDict)
        # for a in dokumanDict["anaSayfalarList"]:
        #     print(a)
        #     if "ic_sayfalar" in a:
        #         for ii in a["ic_sayfalar"]:
        #             print("     ", ii)

        for sceneDict in dokumanDict["anaSayfalarList"]:
            # self._dict_to_scene de, parenti false ediyoruz dongu icinde, ilk item parenta ekleniyor
            # digerleri son eklenen item secili oldugu ve de parent false oldugu icin, parent icindeki
            # item ile ayni seviyede ekleniyorlar.
            # ve tekrar buraya donuluyor burdan az once giden sayfanin ic_sayfalari bitince,
            # bunlar da anasayfalar oldugundan, en top level itemi seciyoruz ve de top levele donmus oluyoruz
            # cunku tw_sayfa_ekle secili itemin seviyesine ekliyor yeni itemlari.
            # sinyalleri simdilik blocklamaya gerek yok selectionChanged signali kullanmiyoruz cunku.
            # self.sayfalarDWTreeView.blockSignals(True)
            # self.sayfalarDWTreeView.setCurrentItem(self.sayfalarDWTreeView.topLevelItem(0))
            # self.sayfalarDWTreeView.sayfayi_sec_ve_current_index_yap(self.sayfalarDWTreeView.model().satirdaki_sayfa(0))
            # self.sayfalarDWTreeView.blockSignals(False)
            self._dict_to_scene(sceneDict, parent=self.cModel.kokSayfa, altSayfaSeklindeEkle=False)

        sayfa_kim = dokumanDict.get("enSonAktifSayfaKim", None)
        sayfa = self.cModel.kimlikten_sayfa(sayfa_kim)
        if sayfa:
            self.sayfalarDWTreeView.sayfayi_sec_ve_current_index_yap(sayfa)

        tempWidgetViewYerine.deleteLater()
        del tempWidgetViewYerine

        self.ekle_sil_butonlari_guncelle()

    # ---------------------------------------------------------------------
    def eveet(self, sceneDict, sayfa):

        # genel olarak sayfa adlari key olarak kullanilmasin..
        ic_sayfa_list = []
        for ic_sayfa in sayfa.ic_sayfalar():
            ic_sayfa_sceneDict = self.scene_to_dict_binary(ic_sayfa.scene)
            ic_sayfa_sceneDict["sayfaAdi"] = ic_sayfa.adi
            ic_sayfa_sceneDict["sayfaKim"] = ic_sayfa._kim
            ic_sayfa_list.append(ic_sayfa_sceneDict)

            # sayfalarDict[sayfa.adi]["ic_sayfalar"] ={"{}".format(ic_sayfa.adi): ic_sayfa_sceneDict}
            if ic_sayfa.ic_sayfa_var_mi():
                self.eveet(ic_sayfa_sceneDict, ic_sayfa)
        sceneDict["ic_sayfalar"] = ic_sayfa_list
        # return sceneDict

    # ---------------------------------------------------------------------
    def dokuman_to_dokumanDict(self):
        # dokumanDict =self.cModel.get_properties_for_save()
        # z = {**x, 'foo': 1, 'bar': 2, **y}  # sozlukleri birlestirmek icin
        dokumanDict = self.cModel.get_properties_for_save()

        # kutuphane ekrani arkaplan rengi
        dokumanDict["kutuphaneBackgroundBrush"] = self.ekranKutuphane.backgroundBrush()
        anaSayfalarList = []
        for ic_sayfa in self.cModel.kokSayfa.ic_sayfalar():
            sceneDict = self.scene_to_dict_binary(ic_sayfa.scene)
            sceneDict["sayfaAdi"] = ic_sayfa.adi
            sceneDict["sayfaKim"] = ic_sayfa._kim
            if ic_sayfa.ic_sayfa_var_mi():
                # return etmeye gerek yok, ama explicit olmasi acisindan belki dondursek mi
                # sceneDict = self.eveet(sceneDict, sayfa)
                self.eveet(sceneDict, ic_sayfa)
            anaSayfalarList.append(sceneDict)

        dokumanDict["anaSayfalarList"] = anaSayfalarList

        return dokumanDict

        # sayfalar klasoru olur, imajlar, videolar falan
        # sayfalar birarada olur hiyerarşi yok gibi diyelim
        # bi tane de sayfa hiyerarsisi belgesi olabilir
        # ayrica sayfa isimleri de bir base64 islemden gecsin. ve de bi maz uzunluk mesele 50 karakter.
        #     hmm ayrica filename collison olma durumu var bas 64 ile bi ek yapmak gerekebilir.

    # https://stackoverflow.com/questions/7406102/create-sane-safe-filename-from-any-unsafe-string

    # https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename

    # https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8

    # ---------------------------------------------------------------------
    def scene_to_dict_binary_recursive(self, children):
        childList = []
        for c in children:
            cPropDict = c.get_properties_for_save_binary()
            if c.childItems():
                if c.type() == shared.GROUP_ITEM_TYPE:
                    cPropDict["children"] = self.scene_to_dict_binary_recursive(c.parentedWithParentOperation)
                    cPropDict["group_children"] = self.scene_to_dict_binary_recursive(c.allFirstLevelGroupChildren)
                else:
                    cPropDict["children"] = self.scene_to_dict_binary_recursive(c.childItems())
            childList.append(cPropDict)
        return childList

    # ---------------------------------------------------------------------
    def scene_to_dict_binary(self, scene):

        # sceneDict = self.cScene.get_properties_for_save()
        sceneDict = scene.get_properties_for_save()

        itemList = []
        for item in scene.items():
            if not item.parentItem():  # root itemlari isliyoruz sadece
                itemPropDict = item.get_properties_for_save_binary()
                if item.childItems():
                    if item.type() == shared.GROUP_ITEM_TYPE:
                        itemPropDict["children"] = self.scene_to_dict_binary_recursive(item.parentedWithParentOperation)
                        itemPropDict["group_children"] = self.scene_to_dict_binary_recursive(
                            item.allFirstLevelGroupChildren)
                    else:
                        itemPropDict["children"] = self.scene_to_dict_binary_recursive(item.childItems())
                    # itemPropDict["children"] = self.scene_to_dict_binary_recursive(item)
                itemList.append(itemPropDict)

        sceneDict["itemList"] = itemList

        return sceneDict

    # ---------------------------------------------------------------------
    def lutfen_bekleyin_goster(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.lutfenBekleyinWidget.show()
        # Ozellikle QThread kullanmiyoruz.
        # Bunlar kullanıcının arayuze bu islemler boyunca etki etmemesinin
        # daha iyi olacagi durumlarda cagriliyor. 
        # Belki bazi islemler icin, o islem QThreade taşınıp
        # yuzde gosteren ve de işlemi iptal edebilecek QProgressBarDialog() eklenebilir. 
        # self.setEnabled(False)
        QApplication.processEvents()

    # ---------------------------------------------------------------------
    def lutfen_bekleyin_gizle(self):
        self.lutfenBekleyinWidget.hide()
        # self.setEnabled(True)
        QApplication.restoreOverrideCursor()

    # ---------------------------------------------------------------------
    def save_file(self, zipDosyaTamAdres, cModel, varsa_ayni_adresteki_dosya_silinsin_mi, isSaveAs=False):
        self.lutfen_bekleyin_goster()
        # mesela imaj paste edildiginde veya embed edildiginde
        # if not os path exists directory olustur sonra da oraya kaydet.async ve de sonra da zip et.
        # şimdi bu methodun sonunda da zip etmek lazim.
        # acarken de oce zipi ac . ama memoryde ac. yukle .kapat memory falan. belki ?

        # burda tempe yonlendir, bu dosya ise zaten temp klasorde acik.
        # bu opendanfilePath = os.path.join(self.cScene.tempDirPath, os.path.basename(zipFilePath))

        if isSaveAs:
            tempDirPath = tempfile.mkdtemp(prefix="defter-tmp")
            try:
                # !! deprecated distutils.dir_util.copy_tree - python3.10
                # !! distutils.dir_util.copy_tree(self.cModel.tempDirPath, tempDirPath)
                # once acik sahne temp klasorunu tamamen kopyaliyoruz yeni bir temp klasore
                shutil.copytree(self.cModel.tempDirPath, tempDirPath, dirs_exist_ok=True)
                # Eger var ise (yani dosya kaydedilmis bir dosya ise yani untitled degil ise)
                # yeni temp klasorden save as edilecek orjinal dosyanin def soyasini siliyoruz.
                # daha sonra save as ismiyle yeniden kayit edecegiz. dosya degismis olabilir o yuzden rename etmiyoruz.

                # saveas de self.cModel kullanabilrdik ama tutarlilik olsun diye parametreyi kullandik burda da.
                copiedSceneDefFile = os.path.join(tempDirPath, cModel.fileName)
                if os.path.isfile(copiedSceneDefFile):
                    os.remove(copiedSceneDefFile)
            # except Exception as e:
            except Exception as e:
                self.lutfen_bekleyin_gizle()
                QMessageBox.warning(self,
                                    'Defter',
                                    self.tr('Could not save file as '
                                            '"{}" : "{}"').format(zipDosyaTamAdres, str(e)))
                return False

        else:
            # self.cModel kullanmiyoruz. aktif olmayan tabin x dugmesine tiklanip kaydet secilebilme ihtimali var.
            tempDirPath = cModel.tempDirPath
        # fileName = os.path.basename(zipDosyaTamAdres)
        fileName = "sayfa"
        filePathInTempDir = os.path.join(tempDirPath, fileName)
        # HTMLFilePathInTempDir = os.path.join(tempDirPath, "index.html")
        HTMLFilePathInTempDir = tempDirPath

        # for sayfa in self.cModel.degismis_sayfalarin_listesi():
        #     print(sayfa._kayit_adi)

        # _file = QFile(filePath)
        # _file = QSaveFile(filePath)
        _file = QSaveFile(filePathInTempDir)
        # if not _file.open( QFile.WriteOnly):
        # if not _file.open(QIODevice.WriteOnly | QIODevice.Text): # QIODevice.Text - eger json save edersek diye.
        if not _file.open(QIODevice.WriteOnly):
            self.lutfen_bekleyin_gizle()
            QMessageBox.warning(self,
                                'Defter',
                                self.tr('Could not save file as '
                                        '"{0:s}" : "{1:s}"').format(zipDosyaTamAdres,
                                                                    _file.errorString()))
            return False

        # yukariyi try icine alirsak hata algilanmiyor ve hata mesaji vermiyor. o yuzden bu sekilde ayirdik.
        try:
            tempBArray = QByteArray()
            tempStream = QDataStream(tempBArray, QIODevice.WriteOnly)
            tempStream.setVersion(QDataStream.Qt_5_7)

            # self.cModel kullanmiyoruz. aktif olmayan tabin x dugmesine tiklanip kaydet secilebilme ihtimali var.
            cModel.saveFilePath = zipDosyaTamAdres
            cModel.fileName = os.path.basename(zipDosyaTamAdres)
            cModel.kaydedince_butun_yildizlari_sil()
            tempStream.writeQVariant(self.dokuman_to_dokumanDict())

            compressedBArray = qCompress(tempBArray)

            toFileStream = QDataStream(_file)
            toFileStream.setVersion(QDataStream.Qt_5_7)
            toFileStream.writeInt32(DEF_MAGIC_NUMBER)
            toFileStream.writeInt16(DEF_FILE_VERSION)

            # onceden writeRawData kullaniyorduk, PySide6 ye gecince << kullanmak gerekti.
            # o yuzden bytearray lengthe de ihtiyac kalmadi. (Okurken problem oluyor.)
            # write byteArrayLength
            # toFileStream.writeUInt64(compressedBArray.size())
            # toFileStream.writeRawData(compressedBArray.data() )
            toFileStream << compressedBArray

            # _file.flush()
            # _file.close()
            _file.commit()
            self.act_export_document_as_html(HTMLFilePathInTempDir)
            try:
                # arsivleme programlarında -u update kullanmaya baslayınca
                # kaydederken var olan bir dosya adresi secilirse, eskisini silmek lazım artik.
                # yoksa eski belgenin gomulu dosyaları yeni def dosyasında kalıyor.
                if varsa_ayni_adresteki_dosya_silinsin_mi:
                    os.remove(zipDosyaTamAdres)
                self.ziple(self.arsivleme_programi_adres, zipDosyaTamAdres, tempDirPath)
            except Exception as e:
                try:
                    # burdaki remove, zipte hata olur da yarım dosya oluşursa diye
                    os.remove(zipDosyaTamAdres)
                except Exception as ee:
                    pass

                # shutil.move(zipDosyaTamAdres)
                self.lutfen_bekleyin_gizle()
                QMessageBox.warning(self,
                                    'Defter',
                                    self.tr('Could not save file as '
                                            '"{0:s}" : "{1:s}" ').format(zipDosyaTamAdres,
                                                                         str(e)))
                return False

            if isSaveAs:
                # TODO: bu niye asagida?
                try:
                    shutil.rmtree(tempDirPath)
                except Exception as e:
                    pass

            self.log(self.tr('{0:s} succesfully saved!').format(zipDosyaTamAdres), 5000, 1)

            self.lutfen_bekleyin_gizle()
            return True

        except Exception as e:
            self.lutfen_bekleyin_gizle()
            QMessageBox.warning(self,
                                'Defter',
                                self.tr('Could not save file as "{0:s}" : "{1:s}" ').format(
                                    zipDosyaTamAdres, str(e)))

            # buna ihtiyacımız yok aslında commit cagrilmaz ise zaten QSave in olusturdugu temp dosya siliniyor
            # eger bu noktadan sonra bir commit cagrilcak olsaydi ve cancelWriting deseydik
            #  o zaman o commit gecersiz olacakti, ama burdan sonra da commit cagrilmiyor zaten.
            # _file.cancelWriting()
            return False

    # ---------------------------------------------------------------------
    @Slot()
    def act_save_def_file(self):
        varsa_ayni_adresteki_dosya_silinsin_mi = False
        path = self.cModel.saveFilePath
        if not path:
            path, varsa_ayni_adresteki_dosya_silinsin_mi = self._get_def_file_save_path()
        if path:
            self.save_file(zipDosyaTamAdres=path,
                           cModel=self.cModel,
                           varsa_ayni_adresteki_dosya_silinsin_mi=varsa_ayni_adresteki_dosya_silinsin_mi,
                           isSaveAs=False)
            self.move_or_append_left_in_recent_files_queue(path)

    # ---------------------------------------------------------------------
    @Slot()
    def act_save_as_def_file(self):
        varsa_ayni_adresteki_dosya_silinsin_mi = False
        path, varsa_ayni_adresteki_dosya_silinsin_mi = self._get_def_file_save_path()
        if path:
            self.save_file(zipDosyaTamAdres=path,
                           cModel=self.cModel,
                           varsa_ayni_adresteki_dosya_silinsin_mi=varsa_ayni_adresteki_dosya_silinsin_mi,
                           isSaveAs=True)
            self.move_or_append_left_in_recent_files_queue(path)

    # ---------------------------------------------------------------------
    @Slot()
    def _get_def_file_save_path(self):
        filtre = self.tr("*.def files (*.def);;All Files (*)")
        fn = QFileDialog.getSaveFileName(self,
                                         self.tr("Save as"),
                                         self.sonKlasor,  # hem sonklasor hem dosyaadi
                                         filtre
                                         )

        path = fn[0]
        varsa_ayni_adresteki_dosya_silinsin_mi = False
        if path:
            # TODO: uzanti kontrolu yap
            if not path.endswith(".def"):
                path = '%s.def' % path
            # arsivleme programlarında -u update kullanmaya baslayınca
            # kaydederken var olan bir dosya adresi secilirse, eskisini silmek lazım artik.
            # yoksa eski belgenin gomulu dosyaları yeni def dosyasında kalıyor.
            if os.path.isfile(path):  # getSaveFileName kullanildigi icin ayni isimde klasor durumu yok.
                varsa_ayni_adresteki_dosya_silinsin_mi = True
            self.sonKlasor = os.path.dirname(path)
        return path, varsa_ayni_adresteki_dosya_silinsin_mi

    # ---------------------------------------------------------------------
    def do_you_want_to_save(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(self.tr("Defter: Save file?"))
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(self.tr("The file has been modified!"))
        msgBox.setInformativeText(self.tr("Do you want to save your changes?"))

        saveButton = msgBox.addButton(self.tr("&Save"), QMessageBox.AcceptRole)
        discardButton = msgBox.addButton(self.tr("&Discard"), QMessageBox.DestructiveRole)
        cancelButton = msgBox.addButton(self.tr("&Cancel"), QMessageBox.RejectRole)
        # msgBox.addButton(QMessageBox.Cancel)
        msgBox.setDefaultButton(saveButton)
        msgBox.setEscapeButton(cancelButton)

        msgBox.exec()
        if msgBox.clickedButton() == saveButton:
            return "s"
        elif msgBox.clickedButton() == discardButton:
            return "d"
        elif msgBox.clickedButton() == cancelButton:
            return "c"
        else:
            pass

    # ---------------------------------------------------------------------
    def do_you_want_to_save_for_close_event(self):

        # self.fileChangeReport=""
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Defter")
        msgBox.setIcon(QMessageBox.Warning)
        # msgBox.setDetailedText(self.fileChangeReport)
        msgBox.setText(self.tr("There are unsaved files!"))
        msgBox.setInformativeText(self.tr("Your changes will be lost if you don't save them."))

        discardButton = msgBox.addButton(self.tr("Close &without saving"), QMessageBox.DestructiveRole)
        cancelButton = msgBox.addButton(self.tr("&Cancel"), QMessageBox.RejectRole)
        msgBox.setDefaultButton(cancelButton)
        msgBox.setEscapeButton(cancelButton)

        msgBox.exec()
        if msgBox.clickedButton() == discardButton:
            return "d"
        elif msgBox.clickedButton() == cancelButton:
            return "c"
        else:
            pass

    # ---------------------------------------------------------------------
    def ekle_hotkeys(self):

        hot_delete_item_with_backspace = QShortcut(QKeySequence(Qt.Key_Backspace),
                                                   self,
                                                   self.act_delete_item)
        hot_delete_item_with_backspace.setContext(Qt.ApplicationShortcut)

        hot_close_active_tab = QShortcut(QKeySequence("Ctrl+W"),
                                         self,
                                         lambda throw_away=0: self.close_selected_tab(self.tabWidget.currentIndex()))
        hot_close_active_tab.setContext(Qt.ApplicationShortcut)

        hot_stil_uygula_yuzen_listwidget_goster_gizle = QShortcut(QKeySequence("Alt+0"),
                                                                  self,
                                                                  self.stil_uygula_yuzen_listwidget_goster_gizle)
        hot_stil_uygula_yuzen_listwidget_goster_gizle.setContext(Qt.ApplicationShortcut)

        # lambda: self.toolsToolBar.setVisible(not self.toolsToolBar.isVisible())

        # hot_clean_mode = QShortcut(QKeySequence("Ctrl+H"),
        #                            self,
        #                            # lambda: self.actionCleanMode.setChecked(not self.actionCleanMode.isChecked()))
        #                            self.actionCleanMode.trigger)
        # hot_clean_mode.setContext(Qt.ApplicationShortcut)

    # ---------------------------------------------------------------------
    def olustur_status_bar(self):

        self._statusBar = QStatusBar(self)
        self.setStatusBar(self._statusBar)
        # self._statusBar.mouseDoubleClickEvent()

        self.lutfenBekleyinWidget = QWidget(self._statusBar)
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        layCubuk = QVBoxLayout()
        layCubuk.setContentsMargins(0, 4, 0, 0)
        self.lutfenBekleyinWidget.setLayout(lay)
        cubuk = QProgressBar(self._statusBar)
        cubuk.setMaximumWidth(200)
        cubuk.setMaximumHeight(7)
        cubuk.setMinimum(0)
        cubuk.setMaximum(0)

        etiket = QLabel(self.tr("Please wait"), self.lutfenBekleyinWidget)
        # etiket.move(30, 0)
        lay.addStretch()
        lay.addWidget(etiket)
        layCubuk.addWidget(cubuk)
        lay.addLayout(layCubuk)

        self.lutfenBekleyinWidget.hide()
        self._statusBar.addPermanentWidget(self.lutfenBekleyinWidget)

        zoomOutBtn = QPushButton(self._statusBar)  # "🔍"
        # zoomOutBtn.setIcon(QIcon(":/icons/zoom-out.png"))
        zoomOutBtn.setIcon(self.actionZoomOut.icon())
        zoomOutBtn.setFlat(True)
        zoomOutBtn.setMaximumWidth(25)
        zoomOutBtn.setMaximumHeight(20)
        zoomOutBtn.clicked.connect(self.cView.zoomOut)
        self._statusBar.addPermanentWidget(zoomOutBtn)

        zoomInBtn = QPushButton(self._statusBar)  # "🔎"
        # zoomInBtn.setIcon(QIcon(":/icons/zoom-in.png"))
        zoomInBtn.setIcon(self.actionZoomIn.icon())
        zoomInBtn.setFlat(True)
        zoomInBtn.setMaximumWidth(25)
        zoomInBtn.setMaximumHeight(20)
        zoomInBtn.clicked.connect(self.cView.zoomIn)
        self._statusBar.addPermanentWidget(zoomInBtn)

        self.zoomSBox = SpinBox(self._statusBar)
        self.zoomSBox.setPrefix("%")
        self.zoomSBox.setMinimum(1)
        self.zoomSBox.setMaximum(10000)
        self.zoomSBox.setSingleStep(10)
        self.zoomSBox.setValue(self.cView.transform().m11() * 100)
        self.zoomSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.cView.set_scale)
        self._statusBar.addPermanentWidget(self.zoomSBox)

        resetZoomBtn = QPushButton(self._statusBar)
        # resetZoomBtn.setIcon(QIcon(":/icons/zoom-reset.png"))
        resetZoomBtn.setIcon(self.actionResetZoom.icon())
        resetZoomBtn.setToolTip(self.tr("Reset Zoom"))
        resetZoomBtn.setFlat(True)
        resetZoomBtn.setMaximumWidth(25)
        resetZoomBtn.setMaximumHeight(20)
        resetZoomBtn.clicked.connect(self.cView.zoomInitial)
        self._statusBar.addPermanentWidget(resetZoomBtn)

        # btn = QPushButton("📜")
        # btn = QPushButton("📖")
        btn = QPushButton("☰", self._statusBar)
        btn.setFlat(True)
        btn.setMaximumWidth(25)
        btn.setMaximumHeight(20)
        btn.clicked.connect(self.act_toggle_log_viewer_dialog)
        # self._statusBar.addWidget(QCheckBox())
        self._statusBar.addPermanentWidget(btn)
        # self._statusBar.addAction(QAction("deneme"))
        # self._statusBar.addPermanentWidget(QPushButton("deneme"))

    # ---------------------------------------------------------------------
    def olustur_menu_bar(self):

        self.mBar = QMenuBar(self)
        self.mBar.setObjectName("menubar")
        self.setMenuBar(self.mBar)

        self.fileMenu = QMenu(self.tr("File"), self.mBar)

        self.actionNewFile = QAction(QIcon(':icons/file-base.png'), self.tr("New File"), self.mBar)
        self.actionNewFile.setShortcut(QKeySequence.New)
        self.actionNewFile.triggered.connect(self.create_tab)

        self.actionOpenFile = QAction(QIcon(':icons/folder-base.png'), self.tr("Open File"), self.mBar)
        self.actionOpenFile.setShortcut(QKeySequence.Open)
        self.actionOpenFile.triggered.connect(self.act_open_def_file)

        self.actionImportDefFiles = QAction(QIcon(':icons/file-base.png'), self.tr("Import def file(s)"), self.mBar)
        self.actionImportDefFiles.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.actionImportDefFiles.triggered.connect(self.act_import_def_files_into_current_def_file)

        self.recentFilesMenu = QMenu(self.tr("Recent Files"), self.mBar)
        # self.recentFilesMenu.setIcon(QIcon(':icons/open-rig.png'))
        self.recentFilesMenu.setIcon(QIcon(':icons/folder-recent.png'))
        self.recentFilesMenu.aboutToShow.connect(lambda throw_away=0: self.on_recent_files_menu_about_to_show())

        # self.actionClearRecentFiles = QAction(QIcon(':icons/warning.png'), "Clear recent files", self.mBar)
        # self.actionClearRecentFiles.triggered.connect(self.act_clear_recent_files_menu)

        self.actionReopenLastClosedTab = QAction(QIcon(':icons/reopen-last-closed-tab.png'),
                                                 self.tr("Reopen Last Closed Tab"),
                                                 self.fileMenu)
        self.actionReopenLastClosedTab.setShortcut(QKeySequence("Ctrl+Shift+T"))
        self.actionReopenLastClosedTab.triggered.connect(self.act_reopen_last_closed_tab)
        if not self.recentFilesQueue:
            self.actionReopenLastClosedTab.setEnabled(False)

        # self.actionSaveFile = QAction(QIcon(':icons/save.png'), "Save File", self.mBar)
        self.actionSaveFile = QAction(QIcon(':icons/file-save.png'), self.tr("Save File"), self.mBar)
        self.actionSaveFile.setShortcut(QKeySequence.Save)
        self.actionSaveFile.triggered.connect(self.act_save_def_file)
        self.actionSaveFile.setEnabled(False)

        # self.actionSaveAsFile = QAction(QIcon(':icons/save-as.png'), "Save as File", self.mBar)
        self.actionSaveAsFile = QAction(QIcon(':icons/file-save-as.png'), self.tr("Save as File"), self.mBar)
        self.actionSaveAsFile.setShortcut(QKeySequence("Shift+Ctrl+S"))
        self.actionSaveAsFile.triggered.connect(self.act_save_as_def_file)
        self.actionSaveAsFile.setEnabled(False)

        self.actionExportPageAsHTML = QAction(QIcon(':icons/file-save-as.png'), self.tr("Export Page as HTML"),
                                              self.mBar)
        # self.actionExportPageAsHTML.setShortcut(QKeySequence("Ctrl+E"))
        self.actionExportPageAsHTML.triggered.connect(self.act_export_page_as_html)

        self.actionExportDocumentAsHTML = QAction(QIcon(':icons/file-save-as.png'), self.tr("Export Document as HTML"),
                                                  self.mBar)
        # self.actionExportDocumentAsHTML.setShortcut(QKeySequence("Ctrl+E"))
        self.actionExportDocumentAsHTML.triggered.connect(self.act_export_document_as_html)

        self.actionExportSelectedTextItemContentAsPdf = QAction(QIcon(':icons/print.png'),
                                                                self.tr("Export Selected Text Item Content as PDF"),
                                                                self.mBar)
        self.actionExportSelectedTextItemContentAsPdf.setShortcut(QKeySequence("Ctrl+Shift+Alt+E"))
        self.actionExportSelectedTextItemContentAsPdf.triggered.connect(
            self.act_export_selected_text_item_content_as_pdf)

        self.actionPrintOrExportAsPdf = QAction(QIcon(':icons/print.png'),
                                                self.tr("Print && Export as PDF"), self.mBar)
        self.actionPrintOrExportAsPdf.setShortcut(QKeySequence("Ctrl+P"))
        self.actionPrintOrExportAsPdf.triggered.connect(self.act_print_document)

        self.actionExportPageAsImage = QAction(QIcon(':icons/file-image.png'),
                                               self.tr("Export Page as Image"), self.mBar)
        self.actionExportPageAsImage.setShortcut(QKeySequence("Ctrl+Shift+P"))
        self.actionExportPageAsImage.triggered.connect(self.act_export_page_as_image)

        self.actionPrintSelectedTextItemContent = QAction(QIcon(':icons/print.png'),
                                                          self.tr("Print Selected Text Item Content"), self.mBar)
        self.actionPrintSelectedTextItemContent.setShortcut(QKeySequence("Ctrl+Alt+P"))
        self.actionPrintSelectedTextItemContent.triggered.connect(self.act_print_selected_text_item_content)

        self.actionSetBackgroundImage = QAction(QIcon(':icons/background-set.png'), self.tr("Set Background Image"),
                                                self.mBar)
        self.actionSetBackgroundImage.setShortcut(QKeySequence("Alt+I"))
        self.actionSetBackgroundImage.triggered.connect(self.act_import_background_image)

        self.actionClearBackgroundImage = QAction(QIcon(':icons/background-clear.png'),
                                                  self.tr("Clear Background Image"),
                                                  self.mBar)
        self.actionClearBackgroundImage.setShortcut(QKeySequence("Shift+Alt+I"))
        self.actionClearBackgroundImage.triggered.connect(self.act_clear_background_image)
        self.addAction(self.actionClearBackgroundImage)

        self.actionEmbedBackgroundImage = QAction(QIcon(':icons/background-set.png'), self.tr("Embed Background Image"),
                                                  self.mBar)
        self.actionEmbedBackgroundImage.triggered.connect(self.act_embed_background_image)
        self.actionEmbedBackgroundImage.setVisible(False)

        self.actionChangeBackgroundColor = QAction(QIcon(':icons/color-wheel.png'), self.tr("Change Background Color"),
                                                   self.mBar)
        self.actionChangeBackgroundColor.setShortcut(QKeySequence("Shift+Alt+C"))
        self.actionChangeBackgroundColor.triggered.connect(self.act_change_background_color)
        self.addAction(self.actionChangeBackgroundColor)

        self.actionImportImages = QAction(QIcon(':icons/open-image.png'), self.tr("Import Image(s)"), self.mBar)
        self.actionImportImages.setShortcut(QKeySequence("Ctrl+I"))
        self.actionImportImages.triggered.connect(self.act_add_multiple_images)

        # self.actionImportVideos = QAction(QIcon(':icons/file-video.png'), "Import Video(s)", self.mBar)
        self.actionImportVideos = QAction(QIcon(':icons/open-video.png'), self.tr("Import Video(s)"), self.mBar)
        self.actionImportVideos.setShortcut(QKeySequence("Ctrl+Shift+Alt+I"))
        self.actionImportVideos.triggered.connect(self.act_add_multiple_videos)

        self.actionImportSVGs = QAction(QIcon(':icons/open-svg.png'), self.tr("~Import SVG(s)"), self.mBar)
        self.actionImportSVGs.setShortcut(QKeySequence("Ctrl+Shift+I"))
        self.actionImportSVGs.triggered.connect(self.act_add_multiple_images)
        self.actionImportSVGs.setDisabled(True)

        self.actionEkleBirCokDosya = QAction(QIcon(':icons/import-file.png'), self.tr("Import File(s)"), self.mBar)
        self.actionEkleBirCokDosya.setShortcut(QKeySequence("Ctrl+Shift+Alt+F"))
        self.actionEkleBirCokDosya.triggered.connect(self.act_ekle_bircok_dosya_nesnesi)

        self.actionExit = QAction(QIcon(':icons/quit.png'), self.tr("E&xit"), self.mBar)
        self.actionExit.setShortcut(QKeySequence("Ctrl+Q"))
        self.actionExit.triggered.connect(self.close)
        self.actionExit.setStatusTip(self.tr("Quit"))
        self.actionExit.setToolTip(self.tr("Quit"))

        self.fileMenu.addActions((self.actionNewFile,
                                  self.actionOpenFile,
                                  self.actionImportDefFiles,
                                  self.fileMenu.addMenu(self.recentFilesMenu),
                                  self.fileMenu.addSeparator(),
                                  self.actionSaveFile,
                                  self.actionSaveAsFile,
                                  self.fileMenu.addSeparator(),
                                  self.actionExportPageAsHTML,
                                  self.actionExportDocumentAsHTML,
                                  self.fileMenu.addSeparator(),
                                  self.actionPrintOrExportAsPdf,
                                  self.actionExportPageAsImage,
                                  self.fileMenu.addSeparator(),
                                  self.actionImportImages,
                                  self.actionImportVideos,
                                  self.actionImportSVGs,
                                  self.fileMenu.addSeparator(),
                                  self.actionEkleBirCokDosya,
                                  self.fileMenu.addSeparator(),
                                  self.actionExit))

        self.editMenu = QMenu(self.tr("Edit"), self.mBar)

        self.actionUndo = QAction(QIcon(':icons/undo.png'), self.tr("Undo"), self.editMenu)
        self.actionUndo.setShortcut(QKeySequence("Ctrl+Z"))
        self.actionUndo.triggered.connect(self.act_undo)
        self.actionUndo.setDisabled(True)
        # to be able to override the cursor to Qt.WaitCursor in undo and redo calls,
        # we did not use undoGroup.createRedoAction,
        # also we still need ordinary Qt.WaitCursor overrides all over the code.
        # becasue of we re not overriding QUndoGroup's or QUndoStack's redo and undo,
        # (because of merged commands and macros)
        # first redo() which called when QundoCommand pushed to the stack does not the override cursor.

        self.actionRedo = QAction(QIcon(':icons/redo.png'), self.tr("Redo"), self.editMenu)
        self.actionRedo.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        self.actionRedo.triggered.connect(self.act_redo)
        self.actionRedo.setDisabled(True)
        # to be able to override the cursor to Qt.WaitCursor in undo and redo calls,
        # we did not use undoGroup.createRedoAction,
        # also we still need ordinary Qt.WaitCursor overrides all over the code.
        # because of we re not overriding QUndoGroup's or QUndoStack's redo and undo,
        # (because of merged commands and macros)
        # first redo() which called when QundoCommand pushed to the stack does not override the cursor.

        self.actionCut = QAction(QIcon(':icons/cut.png'), self.tr("Cut"), self.editMenu)
        self.actionCut.setShortcut(QKeySequence("Ctrl+X"))
        self.actionCut.triggered.connect(self.act_cut)
        self.actionCut.setDisabled(True)

        self.actionCopy = QAction(QIcon(':icons/copy.png'), self.tr("Copy"), self.editMenu)
        self.actionCopy.setShortcut(QKeySequence("Ctrl+C"))
        self.actionCopy.triggered.connect(self.act_copy)
        self.actionCopy.setDisabled(True)

        self.actionPaste = QAction(QIcon(':icons/paste.png'), self.tr("Paste"), self.editMenu)
        self.actionPaste.setShortcut(QKeySequence("Ctrl+V"))
        self.actionPaste.triggered.connect(self.act_paste)
        # self.actionPaste.setDisabled(True)

        self.actionPasteAsPlainText = QAction(QIcon(':icons/paste-as-plain-text.png'), self.tr("Paste as Plain Text"),
                                              self.editMenu)
        self.actionPasteAsPlainText.setShortcut(QKeySequence("Shift+V"))
        self.actionPasteAsPlainText.triggered.connect(self.act_paste_as_plain_text)
        # self.actionPasteAsPlainText.setDisabled(True)

        # enables-disables actionPaste and actionPasteAsPlainText
        self.on_clipboard_data_changed()

        self.actionGroupItems = QAction(QIcon(':icons/group.png'), self.tr("Group"), self.editMenu)
        self.actionGroupItems.setShortcut(QKeySequence("G"))
        self.actionGroupItems.triggered.connect(self.act_group_items)
        self.actionGroupItems.setDisabled(True)

        self.actionUnGroupItems = QAction(QIcon(':icons/ungroup.png'), self.tr("Ungroup"), self.editMenu)
        self.actionUnGroupItems.setShortcut(QKeySequence("Shift+G"))
        self.actionUnGroupItems.triggered.connect(self.act_ungroup_items)
        self.actionUnGroupItems.setDisabled(True)

        self.actionParent = QAction(QIcon(':icons/parent.png'), self.tr("Parent"), self.editMenu)
        self.actionParent.setShortcut(QKeySequence("P"))
        self.actionParent.triggered.connect(self.act_parent_items)
        self.actionParent.setDisabled(True)

        self.actionUnParent = QAction(QIcon(':icons/unparent.png'), self.tr("Unparent"), self.editMenu)
        self.actionUnParent.setShortcut(QKeySequence("Shift+P"))
        self.actionUnParent.triggered.connect(self.act_unparent_items)
        self.actionUnParent.setDisabled(True)

        self.actionBringToFront = QAction(QIcon(':icons/bring-front.png'), self.tr("Bring to &Front"), self.editMenu)
        self.actionBringToFront.setShortcut(QKeySequence("Ctrl+Up"))
        self.actionBringToFront.setStatusTip(self.tr("Bring item to front"))
        self.actionBringToFront.setToolTip(self.tr("Bring item to front"))
        self.actionBringToFront.triggered.connect(self.act_bring_to_front)

        self.actionSendToBack = QAction(QIcon(':icons/send-back.png'), self.tr("Send to &Back"), self.editMenu)
        self.actionSendToBack.setShortcut(QKeySequence("Ctrl+Down"))
        self.actionSendToBack.setStatusTip(self.tr("Send item to back"))
        self.actionSendToBack.setToolTip(self.tr("Send item to back"))
        self.actionSendToBack.triggered.connect(self.act_send_to_back)

        self.actionDeleteItem = QAction(QIcon(':icons/delete.png'), self.tr("&Delete"), self.editMenu)
        self.actionDeleteItem.setShortcut(QKeySequence("Delete"))
        self.actionDeleteItem.setStatusTip(self.tr("Delete item"))
        self.actionDeleteItem.setToolTip(self.tr("Delete item"))
        self.actionDeleteItem.triggered.connect(self.act_delete_item)
        self.actionDeleteItem.setDisabled(True)

        self.actionSelectAll = QAction(QIcon(':icons/select-all.png'), self.tr("&Select All"), self.editMenu)
        self.actionSelectAll.setShortcut(QKeySequence("Ctrl+A"))
        self.actionSelectAll.setStatusTip(self.tr("Select All"))
        self.actionSelectAll.setToolTip(self.tr("Select All"))
        self.actionSelectAll.triggered.connect(self.act_select_all)

        self.editMenu.addActions((self.actionUndo,
                                  self.actionRedo,
                                  self.editMenu.addSeparator(),
                                  self.actionCut,
                                  self.actionCopy,
                                  self.actionPaste,
                                  self.actionPasteAsPlainText,
                                  self.editMenu.addSeparator(),
                                  self.actionGroupItems,
                                  self.actionUnGroupItems,
                                  self.editMenu.addSeparator(),
                                  self.actionParent,
                                  self.actionUnParent,
                                  self.editMenu.addSeparator(),
                                  self.actionBringToFront,
                                  self.actionSendToBack,
                                  self.editMenu.addSeparator(),
                                  self.actionDeleteItem,
                                  self.editMenu.addSeparator(),
                                  self.actionSelectAll
                                  ))

        self.viewMenu = QMenu(self.tr("View"), self.mBar)
        self.viewMenu.aboutToShow.connect(self.on_view_menu_about_to_show)

        toolBarsMenu = QMenu(self.tr("Toolbars"), self.viewMenu)
        toolBarsMenu.aboutToShow.connect(self.on_tool_bars_menu_about_to_show)

        self.actionTumAracCubuklariniGoster = QAction(QIcon(':icons/hepsini-goster.png'), self.tr('Show All'),
                                                      toolBarsMenu)
        self.actionTumAracCubuklariniGoster.setShortcut(QKeySequence("Ctrl+0"))
        self.actionTumAracCubuklariniGoster.triggered.connect(self.act_tum_arac_cubuklarini_goster)

        self.actionToggleToolsToolbar = QAction(QIcon(':icons/arrow.png'), self.tr('Tools'), toolBarsMenu)
        self.actionToggleToolsToolbar.setShortcut(QKeySequence("Ctrl+1"))
        self.actionToggleToolsToolbar.setCheckable(True)
        self.actionToggleToolsToolbar.triggered.connect(
            lambda: self.toolsToolBar.setVisible(not self.toolsToolBar.isVisible()))

        self.actionTogglePropertiesToolbar = QAction(QIcon(':icons/rectangle.png'), self.tr('Properties'),
                                                     toolBarsMenu)
        self.actionTogglePropertiesToolbar.setShortcut(QKeySequence("Ctrl+2"))
        self.actionTogglePropertiesToolbar.setCheckable(True)
        self.actionTogglePropertiesToolbar.triggered.connect(
            lambda: self.propertiesToolBar.setVisible(not self.propertiesToolBar.isVisible()))

        self.actionToggleFontToolbar = QAction(QIcon(':icons/t.png'), self.tr('Font'), toolBarsMenu)
        self.actionToggleFontToolbar.setShortcut(QKeySequence("Ctrl+3"))
        self.actionToggleFontToolbar.setCheckable(True)
        self.actionToggleFontToolbar.triggered.connect(
            lambda: self.fontToolBar.setVisible(not self.fontToolBar.isVisible()))

        self.actionTogglecizgiOzellikleriToolBar = QAction(QIcon(':icons/pen.png'), self.tr('Line'), toolBarsMenu)
        self.actionTogglecizgiOzellikleriToolBar.setShortcut(QKeySequence("Ctrl+4"))
        self.actionTogglecizgiOzellikleriToolBar.setCheckable(True)
        self.actionTogglecizgiOzellikleriToolBar.triggered.connect(
            lambda: self.cizgiOzellikleriToolBar.setVisible(not self.cizgiOzellikleriToolBar.isVisible()))

        self.actionToggleRenkAracCubugu = QAction(QIcon(':icons/color-wheel.png'), self.tr('Color'), toolBarsMenu)
        self.actionToggleRenkAracCubugu.setShortcut(QKeySequence("Ctrl+5"))
        self.actionToggleRenkAracCubugu.setCheckable(True)
        self.actionToggleRenkAracCubugu.triggered.connect(
            lambda: self.renkAracCubugu.setVisible(not self.renkAracCubugu.isVisible()))

        self.actionToggleAlignToolbar = QAction(QIcon(':icons/align-top-edges.png'),
                                                self.tr('Mirror - Align - Distribute'),
                                                toolBarsMenu)
        self.actionToggleAlignToolbar.setShortcut(QKeySequence("Ctrl+6"))
        self.actionToggleAlignToolbar.setCheckable(True)
        self.actionToggleAlignToolbar.triggered.connect(
            lambda: self.alignToolBar.setVisible(not self.alignToolBar.isVisible()))

        self.actionToggleUtilitiesToolbar = QAction(QIcon(':icons/properties.png'), self.tr('Utilities'), toolBarsMenu)
        self.actionToggleUtilitiesToolbar.setShortcut(QKeySequence("Ctrl+7"))
        self.actionToggleUtilitiesToolbar.setCheckable(True)
        self.actionToggleUtilitiesToolbar.triggered.connect(
            lambda: self.utilitiesToolBar.setVisible(not self.utilitiesToolBar.isVisible()))

        toolBarsMenu.addActions((self.actionTumAracCubuklariniGoster,
                                 self.actionToggleToolsToolbar,
                                 self.actionTogglePropertiesToolbar,
                                 self.actionToggleFontToolbar,
                                 self.actionTogglecizgiOzellikleriToolBar,
                                 self.actionToggleRenkAracCubugu,
                                 self.actionToggleAlignToolbar,
                                 self.actionToggleUtilitiesToolbar))

        dockWidgetsMenu = QMenu(self.tr("Panels"), self.viewMenu)
        dockWidgetsMenu.aboutToShow.connect(self.on_dock_widgets_menu_about_to_show)

        self.actionTumPanelleriGoster = QAction(QIcon(':icons/hepsini-goster.png'), self.tr('Show all'),
                                                dockWidgetsMenu)
        self.actionTumPanelleriGoster.setShortcut(QKeySequence("Ctrl+Alt+0"))
        self.actionTumPanelleriGoster.triggered.connect(self.act_tum_panelleri_goster)

        self.actionToggleSayfalarDW = QAction(QIcon(':icons/properties.png'), self.tr('Pages'), dockWidgetsMenu)
        self.actionToggleSayfalarDW.setShortcut(QKeySequence("Ctrl+Alt+1"))
        self.actionToggleSayfalarDW.setCheckable(True)
        self.actionToggleSayfalarDW.triggered.connect(
            lambda: self.sayfalarDW.setVisible(not self.sayfalarDW.isVisible()))

        self.actionToggleNesneOzellikleriDW = QAction(QIcon(':icons/properties.png'), self.tr('Item Properties'),
                                                      dockWidgetsMenu)
        self.actionToggleNesneOzellikleriDW.setShortcut(QKeySequence("Ctrl+Alt+2"))
        self.actionToggleNesneOzellikleriDW.setCheckable(True)
        self.actionToggleNesneOzellikleriDW.triggered.connect(
            lambda: self.nesneOzellikleriDW.setVisible(not self.nesneOzellikleriDW.isVisible()))

        self.actionToggleStillerDW = QAction(QIcon(':icons/properties.png'), self.tr('Style Presets'), dockWidgetsMenu)
        self.actionToggleStillerDW.setShortcut(QKeySequence("Ctrl+Alt+3"))
        self.actionToggleStillerDW.setCheckable(True)
        self.actionToggleStillerDW.triggered.connect(
            lambda: self.stillerDW.setVisible(not self.stillerDW.isVisible()))

        self.actionToggleKutuphaneDW = QAction(QIcon(':icons/properties.png'), self.tr('Library'), dockWidgetsMenu)
        self.actionToggleKutuphaneDW.setShortcut(QKeySequence("Ctrl+Alt+4"))
        self.actionToggleKutuphaneDW.setCheckable(True)
        self.actionToggleKutuphaneDW.triggered.connect(
            lambda: self.kutuphaneDW.setVisible(not self.kutuphaneDW.isVisible()))

        self.actionToggleBaskiSiniriCizimAyarlariDW = QAction(QIcon(':icons/properties.png'),
                                                              self.tr('Draw Print Borders'), dockWidgetsMenu)
        self.actionToggleBaskiSiniriCizimAyarlariDW.setShortcut(QKeySequence("Ctrl+Alt+5"))
        self.actionToggleBaskiSiniriCizimAyarlariDW.setCheckable(True)
        self.actionToggleBaskiSiniriCizimAyarlariDW.triggered.connect(
            lambda: self.baskiSiniriCizimAyarlariDW.setVisible(not self.baskiSiniriCizimAyarlariDW.isVisible()))

        dockWidgetsMenu.addActions((self.actionTumPanelleriGoster,
                                    self.actionToggleSayfalarDW,
                                    self.actionToggleKutuphaneDW,
                                    self.actionToggleStillerDW,
                                    self.actionToggleNesneOzellikleriDW,
                                    self.actionToggleBaskiSiniriCizimAyarlariDW))

        self.zoomMenu = QMenu(self.tr("Zoom"), self.viewMenu)
        self.zoomMenu.setIcon(QIcon(":/icons/zoom.png"))

        self.actionZoomIn = QAction(QIcon(":/icons/zoom-in.png"), self.tr("Zoom in"), self.zoomMenu)
        # self.actionZoomIn.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Plus))
        self.actionZoomIn.setShortcut(QKeySequence("Ctrl++"))
        self.actionZoomIn.setShortcutContext(Qt.ApplicationShortcut)
        self.actionZoomIn.triggered.connect(lambda: self.cView.zoomIn())

        self.actionZoomOut = QAction(QIcon(":/icons/zoom-out.png"), self.tr("Zoom out"), self.zoomMenu)
        # self.actionZoomOut.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Minus))
        self.actionZoomOut.setShortcut(QKeySequence("Ctrl+-"))
        self.actionZoomOut.setShortcutContext(Qt.ApplicationShortcut)
        self.actionZoomOut.triggered.connect(lambda: self.cView.zoomOut())

        self.actionZoomToFit = QAction(QIcon(":/icons/zoom-fit.png"), self.tr("Zoom to fit"), self.zoomMenu)
        self.actionZoomToFit.setShortcut(QKeySequence("Ctrl+/"))
        self.actionZoomToFit.setShortcutContext(Qt.ApplicationShortcut)
        self.actionZoomToFit.triggered.connect(lambda: self.cView.zoomToFit())

        self.actionZoomToSelection = QAction(QIcon(":/icons/zoom-select.png"), self.tr("Zoom to selection"),
                                             self.zoomMenu)
        self.actionZoomToSelection.setShortcut(QKeySequence("Ctrl+Shift+/"))
        self.actionZoomToSelection.setShortcutContext(Qt.ApplicationShortcut)
        self.actionZoomToSelection.triggered.connect(lambda: self.cView.zoomToSelection())

        self.actionResetZoom = QAction(QIcon(":/icons/zoom-reset.png"), self.tr("Reset zoom"), self.zoomMenu)
        self.actionResetZoom.setShortcut(QKeySequence("Ctrl+*"))
        self.actionResetZoom.setShortcutContext(Qt.ApplicationShortcut)
        self.actionResetZoom.triggered.connect(lambda: self.cView.zoomInitial())

        self.zoomMenu.addActions((self.actionZoomIn,
                                  self.actionZoomOut,
                                  self.actionZoomToFit,
                                  self.actionZoomToSelection,
                                  self.actionResetZoom))

        self.actionCleanMode = QAction(self.tr("Clean Mode"), self.viewMenu)
        self.actionCleanMode.setShortcut(QKeySequence("Ctrl+H"))
        self.actionCleanMode.setCheckable(True)
        self.actionCleanMode.setStatusTip(self.tr("Clean Mode"))
        self.actionCleanMode.setToolTip(self.tr("Clean Mode"))
        self.actionCleanMode.triggered.connect(self.act_clean_mode)
        # self.actionCleanMode.setShortcutContext(Qt.ApplicationShortcut)
        self.addAction(self.actionCleanMode)

        self.actionToggleStatusBar = QAction(self.tr("Status Bar"), self.viewMenu)
        self.actionToggleStatusBar.setShortcut(QKeySequence("Alt+S"))
        self.actionToggleStatusBar.setCheckable(True)
        self.actionToggleStatusBar.setStatusTip(self.tr("Toggles status bar visibility."))
        self.actionToggleStatusBar.setToolTip(self.tr("Toggles status bar visibility."))
        self.actionToggleStatusBar.triggered.connect(
            lambda: self._statusBar.setVisible(not self._statusBar.isVisible()))
        # self.actionToggleStatusBar.setShortcutContext(Qt.ApplicationShortcut)
        # self.addAction(self.actionToggleStatusBar)

        self.actionToggleMenuBar = QAction(self.tr("Menu bar"), self.viewMenu)
        self.actionToggleMenuBar.setShortcut(QKeySequence("Alt+M"))
        self.actionToggleMenuBar.setCheckable(True)
        self.actionToggleMenuBar.setStatusTip(self.tr("Toggles menu bar visibility."))
        self.actionToggleMenuBar.setToolTip(self.tr("Toggles menu bar visibility."))
        self.actionToggleMenuBar.triggered.connect(
            lambda: self.mBar.setVisible(not self.mBar.isVisible()))

        self.viewMenu.addActions((self.viewMenu.addMenu(self.zoomMenu),
                                  self.viewMenu.addSeparator(),
                                  self.viewMenu.addMenu(toolBarsMenu),
                                  self.viewMenu.addSeparator(),
                                  self.viewMenu.addMenu(dockWidgetsMenu),
                                  self.viewMenu.addSeparator(),
                                  self.actionToggleStatusBar,
                                  self.actionToggleMenuBar,
                                  self.actionCleanMode,
                                  self.viewMenu.addSeparator(),
                                  self.actionSetBackgroundImage,
                                  self.actionClearBackgroundImage,
                                  self.actionEmbedBackgroundImage,
                                  self.actionChangeBackgroundColor,
                                  self.viewMenu.addSeparator(),
                                  self.actionReopenLastClosedTab
                                  ))

        self.toolsMenu = QMenu(self.tr("Tools"), self.mBar)

        self.toolsMenu.addActions((self.actionSwitchToSelectionTool,
                                   self.actionAddRectItem,
                                   self.actionAddEllipseItem,
                                   self.actionDrawLineItem,
                                   self.actionAddTextItem,
                                   self.actionDrawPathItem,
                                   self.actionAddImageItem,
                                   self.actionAddVideoItem,
                                   self.actionEkleDosyaNesnesi,
                                   self.toolsMenu.addSeparator(),
                                   self.actionWebBrowserAc))

        helpMenu = QMenu(self.tr("Help"), self.mBar)
        actionAbout = QAction(QIcon(":icons/info.png"), self.tr("About Defter"), helpMenu)
        actionAbout.setMenuRole(QAction.AboutRole)
        actionAbout.triggered.connect(self.act_about)

        actionAboutQt = QAction(self.tr("About Qt"), helpMenu)
        # actionAboutQt.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        actionAboutQt.triggered.connect(QApplication.aboutQt)
        actionAboutQt.setMenuRole(QAction.AboutQtRole)
        helpMenu.addActions((actionAbout, actionAboutQt))

        self.mBar.addMenu(self.fileMenu)
        self.mBar.addMenu(self.editMenu)
        self.mBar.addMenu(self.viewMenu)
        self.mBar.addMenu(self.toolsMenu)
        self.mBar.addMenu(helpMenu)

        # self.undoGroup.cleanChanged.connect(self.modify_status)
        self.undoGroup.canRedoChanged.connect(lambda x: self.actionRedo.setEnabled(x))
        self.undoGroup.canUndoChanged.connect(lambda x: self.actionUndo.setEnabled(x))
        self.undoGroup.redoTextChanged.connect(lambda x: self.actionRedo.setText(self.tr("Redo {}").format(x)))
        self.undoGroup.undoTextChanged.connect(lambda x: self.actionUndo.setText(self.tr("Undo {}").format(x)))
        self.undoGroup.cleanChanged.connect(self.clean_changed)

    # ---------------------------------------------------------------------
    def olustur_item_context_menus_and_actions(self):
        self.itemContextMenu = QMenu(self.tr("Item Menu"), self)

        self.actionPinItem = QAction(QIcon(":icons/pin.png"), self.tr("Pin"), self.itemContextMenu)
        self.actionPinItem.setShortcut(QKeySequence("k"))
        # self.actionPinItem.setShortcutContext(Qt.ApplicationShortcut)
        self.actionPinItem.triggered.connect(self.act_pin_item)

        self.actionUnPinItem = QAction(QIcon(":icons/unpin.png"), self.tr("Unpin"), self.itemContextMenu)
        self.actionUnPinItem.setShortcut(QKeySequence("Shift+k"))
        self.actionUnPinItem.triggered.connect(self.act_unpin_item)

        self.actionEditCommand = QAction(QIcon(":icons/command.png"), self.tr("~Edit Command"), self.itemContextMenu)
        self.actionEditCommand.setShortcut(QKeySequence("Shift+C"))
        self.actionEditCommand.triggered.connect(lambda: self.act_edit_command(self.cScene.activeItem))
        # self.actionEditCommand.setShortcutContext(Qt.WindowShortcut)
        self.actionEditCommand.setDisabled(True)

        self.actionAddSelectedItemStyleAsAPreset = QAction(QIcon(':icons/icons/text-html.png'),
                                                           self.tr("Add selected item's style as a preset"),
                                                           self.itemContextMenu)
        self.actionAddSelectedItemStyleAsAPreset.triggered.connect(self.act_add_style_preset)

        self.actionSeciliNesneStiliniSeciliAracaUygula = QAction(QIcon(':icons/icons/text-html.png'),
                                                                 self.tr(
                                                                     "Apply selected item's style to the active tool"),
                                                                 self.itemContextMenu)
        self.actionSeciliNesneStiliniSeciliAracaUygula.triggered.connect(
            self.act_secili_nesne_stilini_secili_araca_uygula)

        self.actionSeciliNesneStiliniKendiAracinaUygula = QAction(QIcon(':icons/icons/text-html.png'),
                                                                 self.tr(
                                                                     "Set selected item's style as tool default"),
                                                                 self.itemContextMenu)
        self.actionSeciliNesneStiliniKendiAracinaUygula.triggered.connect(
            self.act_secili_nesne_stilini_kendi_aracina_uygula)

        self.actionShowInFileManager = QAction(QIcon(':icons/icons/text-html.png'), self.tr("Show in file manager"),
                                               self.itemContextMenu)
        self.actionShowInFileManager.triggered.connect(self.act_show_in_file_manager)

        # ---------------------------------------------------------------------

        self.actionConvertToPlainText = QAction(QIcon(":icons/command.png"),
                                                self.tr("Convert selected item(s) to plain text"),
                                                self.itemContextMenu)
        self.actionConvertToPlainText.setShortcut(QKeySequence("Ctrl+Alt+P"))
        self.actionConvertToPlainText.triggered.connect(self.act_convert_to_plain_text)

        self.actionShowHTMLSource = QAction(QIcon(':icons/icons/text-html.png'), self.tr("Show HTML source"),
                                            self.itemContextMenu)
        self.actionShowHTMLSource.triggered.connect(self.act_show_html_source)

        self.actionLocalizeHtml = QAction(QIcon(':icons/icons/text-html.png'), self.tr("Localize HTML"),
                                          self.itemContextMenu)
        self.actionLocalizeHtml.triggered.connect(self.act_localize_html)

        self.actionResizeTextItemToFitView = QAction(QIcon(':icons/icons/text-html.png'),
                                                     self.tr("Resize to fit in view"), self.itemContextMenu)
        self.actionResizeTextItemToFitView.triggered.connect(self.act_resize_text_item_to_fit_view)

        self.actionShowAsWebPage = QAction(QIcon(':icons/icons/text-html.png'), self.tr("Show as web page"),
                                           self.itemContextMenu)
        self.actionShowAsWebPage.triggered.connect(self.act_show_as_web_page)

        self.actionConvertToWebItem = QAction(QIcon(':icons/icons/text-html.png'),
                                              self.tr("~Convert to web item (Experimental && Slow)"),
                                              self.itemContextMenu)
        self.actionConvertToWebItem.triggered.connect(self.act_convert_to_web_item)
        self.actionConvertToWebItem.setDisabled(True)

        # ---------------------------------------------------------------------
        self.actionEmbedImage = QAction(QIcon(":icons/command.png"), self.tr("Embed image(s) to document"),
                                        self.itemContextMenu)
        # self.actionEmbedImage.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self.actionEmbedImage.triggered.connect(self.act_embed_images)

        self.actionExportImage = QAction(QIcon(":icons/command.png"), self.tr("Export image(s)"), self.itemContextMenu)
        # self.actionExportImage.setShortcut(QKeySequence("Ctrl+Shift+I"))
        self.actionExportImage.triggered.connect(self.act_export_image)

        self.actionShowImageInfo = QAction(QIcon(':icons/info.png'), self.tr("Show image info"), self.itemContextMenu)
        self.actionShowImageInfo.triggered.connect(self.act_show_image_info)

        self.actionCrop = QAction(QIcon(':icons/info.png'), self.tr("Crop Image"), self.itemContextMenu)
        self.actionCrop.setShortcut(QKeySequence("Alt+C"))
        self.actionCrop.triggered.connect(lambda: self.act_crop(self.cScene.activeItem))

        # ---------------------------------------------------------------------
        self.actionEmbedVideo = QAction(QIcon(":icons/command.png"), self.tr("Embed video(s) to document"),
                                        self.itemContextMenu)
        # self.actionEmbedVideo.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self.actionEmbedVideo.triggered.connect(self.act_embed_video)

        self.actionExportVideo = QAction(QIcon(":icons/command.png"), self.tr("Export video(s)"), self.itemContextMenu)
        # self.actionExportVideo.setShortcut(QKeySequence("Ctrl+Shift+I"))
        self.actionExportVideo.triggered.connect(self.act_export_video)

        self.actionShowVideoInfo = QAction(QIcon(':icons/info.png'), self.tr("Show video info"), self.itemContextMenu)
        self.actionShowVideoInfo.triggered.connect(self.act_show_video_info)

        # ---------------------------------------------------------------------
        self.actionEmbedDosya = QAction(QIcon(":icons/command.png"), self.tr("Embed file(s) to document"),
                                        self.itemContextMenu)
        # self.actionEmbedDosya.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self.actionEmbedDosya.triggered.connect(self.act_embed_dosya)

        self.actionExportDosya = QAction(QIcon(":icons/command.png"), self.tr("Export file(s)"), self.itemContextMenu)
        # self.actionExportDosya.setShortcut(QKeySequence("Ctrl+Shift+I"))
        self.actionExportDosya.triggered.connect(self.act_export_dosya)

        self.actionShowDosyaInfo = QAction(QIcon(':icons/info.png'), self.tr("Show file info"), self.itemContextMenu)
        self.actionShowDosyaInfo.triggered.connect(self.act_show_dosya_info)

        self.itemContextMenu.addActions((self.actionPinItem,
                                         self.actionUnPinItem,
                                         self.itemContextMenu.addSeparator(),
                                         self.actionCut,
                                         self.actionCopy,
                                         self.itemContextMenu.addSeparator(),
                                         self.actionBringToFront,
                                         self.actionSendToBack,
                                         self.itemContextMenu.addSeparator(),
                                         self.actionGroupItems,
                                         self.actionUnGroupItems,
                                         self.itemContextMenu.addSeparator(),
                                         self.actionParent,
                                         self.actionUnParent,
                                         self.itemContextMenu.addSeparator(),
                                         self.actionEditCommand,
                                         self.itemContextMenu.addSeparator(),
                                         self.actionConvertToPlainText,
                                         self.actionEmbedImage,
                                         self.actionExportImage,
                                         self.actionShowImageInfo,
                                         self.actionCrop,
                                         self.actionEmbedVideo,
                                         self.actionExportVideo,
                                         self.actionShowVideoInfo,
                                         self.actionEmbedDosya,
                                         self.actionExportDosya,
                                         self.actionShowDosyaInfo,
                                         self.actionShowHTMLSource,
                                         self.actionLocalizeHtml,
                                         self.actionShowInFileManager,
                                         self.actionResizeTextItemToFitView,
                                         self.actionShowAsWebPage,
                                         self.actionConvertToWebItem,
                                         self.itemContextMenu.addSeparator(),
                                         self.actionExportSelectedTextItemContentAsPdf,
                                         self.actionPrintSelectedTextItemContent,
                                         self.itemContextMenu.addSeparator(),
                                         self.actionAddSelectedItemStyleAsAPreset,
                                         self.actionSeciliNesneStiliniSeciliAracaUygula,
                                         self.actionSeciliNesneStiliniKendiAracinaUygula
                                         ))

        self.groupContextMenu = QMenu(self.tr("Group Menu"), self)
        # self.groupContextMenu.aboutToShow.connect(lambda: self.on_group_item_context_menu_about_to_show(group))

        self.groupContextMenu.addActions((self.actionPinItem,
                                          self.actionUnPinItem,
                                          self.groupContextMenu.addSeparator(),
                                          self.actionCut,
                                          self.actionCopy,
                                          self.groupContextMenu.addSeparator(),
                                          self.actionBringToFront,
                                          self.actionSendToBack,
                                          self.groupContextMenu.addSeparator(),
                                          self.actionGroupItems,
                                          self.actionUnGroupItems,
                                          self.groupContextMenu.addSeparator(),
                                          self.actionParent,
                                          self.actionUnParent))

        # ---------------------------------------------------------------------
        self.kutuphaneEkranContextMenu = QMenu(self.tr("Library Item Menu"), self)

        self.kutuphaneZoomMenu = QMenu(self.tr("Zoom"), self.viewMenu)
        self.kutuphaneZoomMenu.setIcon(QIcon(":/icons/zoom.png"))

        self.actionKutEkrYenileBelgeGomuluVeLinkli = QAction(QIcon(':icons/refresh.png'),
                                                             self.tr("Both linked and embeded - document"),
                                                             self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileBelgeGomuluVeLinkli.setToolTip(
            self.tr("List both linked and embeded images in the document"))
        self.actionKutEkrYenileBelgeGomuluVeLinkli.setShortcut(QKeySequence("Ctrl+F1"))
        self.actionKutEkrYenileBelgeGomuluVeLinkli.triggered.connect(
            self.act_kut_belgedeki_linkli_ve_gomulu_dosyalari_goster)

        self.actionKutEkrYenileSahneGomuluVeLinkli = QAction(QIcon(':icons/refresh.png'),
                                                             self.tr("Both linked and embeded - page"),
                                                             self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileSahneGomuluVeLinkli.setToolTip(
            self.tr("List both linked and embeded images in the page"))
        self.actionKutEkrYenileSahneGomuluVeLinkli.setShortcut(QKeySequence("Ctrl+F2"))
        self.actionKutEkrYenileSahneGomuluVeLinkli.triggered.connect(
            self.act_kut_sahnedeki_linkli_ve_gomulu_dosyalari_goster)

        self.actionKutEkrYenileBelgeLinkli = QAction(QIcon(':icons/refresh.png'),
                                                     self.tr("Linked - document"),
                                                     self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileBelgeLinkli.setToolTip(self.tr("List linked images in the document"))
        self.actionKutEkrYenileBelgeLinkli.setShortcut(QKeySequence("Ctrl+F3"))
        self.actionKutEkrYenileBelgeLinkli.triggered.connect(
            self.act_kut_belgedeki_linkli_dosyalari_goster)

        self.actionKutEkrYenileSahneLinkli = QAction(QIcon(':icons/refresh.png'),
                                                     self.tr("Linked - page"),
                                                     self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileSahneLinkli.setToolTip(self.tr("List linked images in the page"))
        self.actionKutEkrYenileSahneLinkli.setShortcut(QKeySequence("Ctrl+F4"))
        self.actionKutEkrYenileSahneLinkli.triggered.connect(
            self.act_kut_sahnedeki_linkli_dosyalari_goster)

        self.actionKutEkrYenileBelgeGomulu = QAction(QIcon(':icons/refresh.png'),
                                                     self.tr("Embeded - document"),
                                                     self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileBelgeGomulu.setToolTip(self.tr("List embeded images in the document"))
        self.actionKutEkrYenileBelgeGomulu.setShortcut(QKeySequence("Ctrl+F5"))
        self.actionKutEkrYenileBelgeGomulu.triggered.connect(self.act_kut_belgedeki_gomulu_dosyalari_goster)

        self.actionKutEkrYenileSahneGomulu = QAction(QIcon(':icons/refresh.png'),
                                                     self.tr("Embeded - page"),
                                                     self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileSahneGomulu.setToolTip(self.tr("List embeded images in the page"))
        self.actionKutEkrYenileSahneGomulu.setShortcut(QKeySequence("Ctrl+F6"))
        self.actionKutEkrYenileSahneGomulu.triggered.connect(self.act_kut_sahnedeki_gomulu_dosyalari_goster)

        self.actionKutEkrYenileBelgedeOlmayanGomulu = QAction(QIcon(':icons/refresh.png'),
                                                              self.tr("Unused embeded - document"),
                                                              self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileBelgedeOlmayanGomulu.setToolTip(self.tr("List unused embeded images in the document"))
        self.actionKutEkrYenileBelgedeOlmayanGomulu.setShortcut(QKeySequence("Ctrl+F7"))
        self.actionKutEkrYenileBelgedeOlmayanGomulu.triggered.connect(
            self.act_kut_belgede_kullanilmayan_gomulu_dosyalari_goster)

        self.actionKutEkrYenileSahnedeOlmayanGomulu = QAction(QIcon(':icons/refresh.png'),
                                                              self.tr("Unused embeded - page"),
                                                              self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileSahnedeOlmayanGomulu.setToolTip(self.tr("List unused embeded images in the page"))
        self.actionKutEkrYenileSahnedeOlmayanGomulu.setShortcut(QKeySequence("Ctrl+F8"))
        self.actionKutEkrYenileSahnedeOlmayanGomulu.triggered.connect(
            self.act_kut_sahnede_kullanilmayan_gomulu_dosyalari_goster)

        self.actionKutEkrYenileBelgeHtmlImajTumu = QAction(QIcon(':icons/refresh.png'),
                                                           self.tr("All Html images"),
                                                           self.kutuphaneEkranContextMenu)
        self.actionKutEkrYenileBelgeHtmlImajTumu.setToolTip(
            self.tr("List all images downloaded with HTML localization"), )
        self.actionKutEkrYenileBelgeHtmlImajTumu.setShortcut(QKeySequence("Ctrl+F9"))
        self.actionKutEkrYenileBelgeHtmlImajTumu.triggered.connect(self.act_kut_belgedeki_html_imajlari_goster)

        self.actionKutEkrSilBelgedeOlmayanlar = QAction(QIcon(':icons/delete.png'),
                                                        self.tr("Delete unused embeded - document"),
                                                        self.kutuphaneEkranContextMenu)
        self.actionKutEkrSilBelgedeOlmayanlar.setToolTip(self.tr("Delete unused embeded images in the document"))
        self.actionKutEkrSilBelgedeOlmayanlar.setShortcut(QKeySequence("Ctrl+F10"))
        self.actionKutEkrSilBelgedeOlmayanlar.triggered.connect(
            self.act_kut_belgede_kullanilmayan_gomulu_dosyalari_sil)

        self.actionKutEkrChangeBackgroundColor = QAction(QIcon(':icons/color-wheel.png'),
                                                         self.tr("Change Background Color"),
                                                         self.mBar)
        self.actionKutEkrChangeBackgroundColor.setToolTip(self.tr("Change Background Color"))
        self.actionKutEkrChangeBackgroundColor.setShortcut(QKeySequence("Shift+Alt+C"))
        self.actionKutEkrChangeBackgroundColor.triggered.connect(self.act_kut_change_background_color)

        self.kutuphaneEkranContextMenu.addActions((self.actionKutEkrYenileBelgeGomuluVeLinkli,
                                                   self.actionKutEkrYenileSahneGomuluVeLinkli,
                                                   self.kutuphaneEkranContextMenu.addSeparator(),
                                                   self.actionKutEkrYenileBelgeLinkli,
                                                   self.actionKutEkrYenileSahneLinkli,
                                                   self.kutuphaneEkranContextMenu.addSeparator(),
                                                   self.actionKutEkrYenileBelgeGomulu,
                                                   self.actionKutEkrYenileSahneGomulu,
                                                   self.kutuphaneEkranContextMenu.addSeparator(),
                                                   self.actionKutEkrYenileBelgedeOlmayanGomulu,
                                                   self.actionKutEkrYenileSahnedeOlmayanGomulu,
                                                   self.kutuphaneEkranContextMenu.addSeparator(),
                                                   self.actionKutEkrYenileBelgeHtmlImajTumu,
                                                   self.kutuphaneEkranContextMenu.addSeparator(),
                                                   self.actionKutEkrSilBelgedeOlmayanlar,
                                                   self.kutuphaneEkranContextMenu.addSeparator(),
                                                   self.actionKutEkrChangeBackgroundColor,
                                                   self.kutuphaneEkranContextMenu.addSeparator(),
                                                   self.kutuphaneEkranContextMenu.addMenu(self.kutuphaneZoomMenu),
                                                   ))

        # ---------------------------------------------------------------------

        self.actionKutuphaneZoomIn = QAction(QIcon(":/icons/zoom-in.png"), self.tr("Zoom in"), self.kutuphaneZoomMenu)
        self.actionKutuphaneZoomIn.triggered.connect(lambda: self.ekranKutuphane.zoomIn())
        # self.actionZoomIn.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Plus))
        # self.actionZoomIn.setShortcutContext(Qt.ApplicationShortcut)

        self.actionKutuphaneZoomOut = QAction(QIcon(":/icons/zoom-out.png"), self.tr("Zoom out"),
                                              self.kutuphaneZoomMenu)
        self.actionKutuphaneZoomOut.triggered.connect(lambda: self.ekranKutuphane.zoomOut())
        # self.actionZoomOut.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Minus))
        # self.actionZoomOut.setShortcutContext(Qt.ApplicationShortcut)

        self.actionKutuphaneZoomToFit = QAction(QIcon(":/icons/zoom-fit.png"), self.tr("Zoom to fit"),
                                                self.kutuphaneZoomMenu)
        self.actionKutuphaneZoomToFit.triggered.connect(lambda: self.ekranKutuphane.zoomToFit())
        # self.actionZoomToFit.setShortcut(QKeySequence("Ctrl+F"))
        # self.actionZoomToFit.setShortcutContext(Qt.ApplicationShortcut)

        self.actionKutuphaneResetZoom = QAction(QIcon(":/icons/zoom-reset.png"), self.tr("Reset zoom"),
                                                self.kutuphaneZoomMenu)
        self.actionKutuphaneResetZoom.triggered.connect(lambda: self.ekranKutuphane.zoomInitial())
        # self.actionResetZoom.setShortcut(QKeySequence("Ctrl+0"))
        # self.actionResetZoom.setShortcutContext(Qt.ApplicationShortcut)

        self.kutuphaneZoomMenu.addActions((self.actionKutuphaneZoomIn,
                                           self.actionKutuphaneZoomOut,
                                           self.actionKutuphaneZoomToFit,
                                           self.actionKutuphaneResetZoom))

        # ---------------------------------------------------------------------
        self.kutuphaneNesneContextMenu = QMenu(self.tr("Library Item Menu"), self)

        self.actionKutuphaneNesneSil = QAction(QIcon(":icons/remove.png"), self.tr("Delete"),
                                               self.kutuphaneNesneContextMenu)
        # self.actionKutuphaneNesneSil.setShortcut(QKeySequence("P"))
        # self.actionPinItem.setShortcutContext(Qt.ApplicationShortcut)
        self.actionKutuphaneNesneSil.triggered.connect(self.act_kutuphaneden_nesne_sil)

        self.actionKutuphaneDosyaYonetcisindeGoster = QAction(QIcon(":icons/icons/text-html.png"),
                                                              self.tr("Show in file manager"),
                                                              self.kutuphaneNesneContextMenu)
        # self.actionKutuphaneDosyaYonetcisindeGoster.setShortcut(QKeySequence("P"))
        # self.actionKutuphaneDosyaYonetcisindeGoster.setShortcutContext(Qt.ApplicationShortcut)
        self.actionKutuphaneDosyaYonetcisindeGoster.triggered.connect(self.act_kut_dosya_yoneticisinde_goster)

        self.actionKutuphaneSahnedeGoster = QAction(QIcon(":icons/icons/text-html.png"), self.tr("~Show in scene"),
                                                    self.kutuphaneNesneContextMenu)
        # self.actionKutuphaneDosyaYonetcisindeGoster.setShortcut(QKeySequence("P"))
        # self.actionKutuphaneDosyaYonetcisindeGoster.setShortcutContext(Qt.ApplicationShortcut)
        self.actionKutuphaneSahnedeGoster.triggered.connect(self.act_kut_dosya_yoneticisinde_goster)
        self.actionKutuphaneSahnedeGoster.setDisabled(True)

        self.kutuphaneNesneContextMenu.addActions((self.actionKutuphaneNesneSil,
                                                   self.actionKutuphaneDosyaYonetcisindeGoster,
                                                   self.actionKutuphaneSahnedeGoster))

    # ---------------------------------------------------------------------
    def olustur_dummy_widget_for_actions(self):

        dummyWidgetForActions = QWidget(self)
        dummyWidgetForActions.setGeometry(0, 0, 0, 0)
        dummyWidgetForActions.addActions((self.actionPinItem,
                                          self.actionUnPinItem,
                                          self.actionEditCommand,
                                          self.actionConvertToPlainText,
                                          self.actionEmbedImage,
                                          self.actionExportImage,
                                          self.actionShowImageInfo,
                                          self.actionCrop,
                                          self.actionEmbedVideo,
                                          self.actionExportVideo,
                                          self.actionShowVideoInfo,
                                          self.actionEmbedDosya,
                                          self.actionExportDosya,
                                          self.actionShowDosyaInfo,
                                          self.actionShowHTMLSource,
                                          self.actionLocalizeHtml,
                                          self.actionResizeTextItemToFitView,
                                          self.actionShowAsWebPage,
                                          self.actionConvertToWebItem,
                                          self.actionAddSelectedItemStyleAsAPreset,
                                          self.actionSeciliNesneStiliniSeciliAracaUygula,
                                          self.actionSeciliNesneStiliniKendiAracinaUygula,
                                          self.actionExportSelectedTextItemContentAsPdf,
                                          self.actionPrintSelectedTextItemContent,
                                          # file menu actions
                                          self.actionNewFile,
                                          self.actionOpenFile,
                                          self.actionImportDefFiles,
                                          self.actionReopenLastClosedTab,
                                          self.actionSaveFile,
                                          self.actionSaveAsFile,
                                          self.actionExportPageAsHTML,
                                          self.actionExportDocumentAsHTML,
                                          self.actionPrintOrExportAsPdf,
                                          self.actionExportPageAsImage,
                                          self.actionSetBackgroundImage,
                                          self.actionImportImages,
                                          self.actionImportVideos,
                                          self.actionImportSVGs,
                                          self.actionEkleBirCokDosya,
                                          self.actionExit,
                                          # edit menu actions
                                          self.actionUndo,
                                          self.actionRedo,
                                          self.actionCut,
                                          self.actionCopy,
                                          self.actionPaste,
                                          self.actionPasteAsPlainText,
                                          self.actionGroupItems,
                                          self.actionUnGroupItems,
                                          self.actionParent,
                                          self.actionUnParent,
                                          self.actionBringToFront,
                                          self.actionSendToBack,
                                          self.actionDeleteItem,
                                          self.actionSelectAll,
                                          # tool bar menu actions
                                          self.actionTumAracCubuklariniGoster,
                                          self.actionToggleToolsToolbar,
                                          self.actionTogglePropertiesToolbar,
                                          self.actionToggleAlignToolbar,
                                          self.actionToggleFontToolbar,
                                          self.actionToggleRenkAracCubugu,
                                          self.actionTogglecizgiOzellikleriToolBar,
                                          self.actionToggleUtilitiesToolbar,
                                          # dockWidgetsMenu actions
                                          self.actionTumPanelleriGoster,
                                          self.actionToggleSayfalarDW,
                                          self.actionToggleNesneOzellikleriDW,
                                          self.actionToggleStillerDW,
                                          self.actionToggleKutuphaneDW,
                                          self.actionToggleBaskiSiniriCizimAyarlariDW,
                                          # view menu actions
                                          self.actionToggleStatusBar,
                                          self.actionToggleMenuBar,
                                          self.actionCleanMode,
                                          # zoom menu actions
                                          self.actionZoomIn,
                                          self.actionZoomOut,
                                          self.actionZoomToFit,
                                          self.actionZoomToSelection,
                                          self.actionResetZoom,
                                          # tools menu actions
                                          self.actionSwitchToSelectionTool,
                                          self.actionDrawLineItem,
                                          self.actionAddRectItem,
                                          self.actionAddEllipseItem,
                                          self.actionDrawPathItem,
                                          self.actionAddTextItem,
                                          self.actionAddImageItem,
                                          self.actionAddVideoItem,
                                          self.actionEkleDosyaNesnesi,
                                          self.actionWebBrowserAc,
                                          # align tool bar actions
                                          self.actionMirrorX,
                                          self.actionMirrorY,
                                          self.actionAlignLeft,
                                          self.actionAlignRight,
                                          self.actionAlignVerticalCenter,
                                          self.actionAlignTop,
                                          self.actionAlignBottom,
                                          self.actionAlignHorizontalCenter,
                                          self.actionEqualizeHorizontalGaps,
                                          self.actionEqualizeVerticalGaps,
                                          self.actionDistributeItemsVertically,
                                          self.actionDistributeItemsHorizontally,
                                          # utilities menu
                                          self.actionSecimEkranGoruntusuAlCmOn
                                          ))

    # ---------------------------------------------------------------------
    def view_context_menu_goster(self, pos):
        menu = QMenu()

        if self.cView.backgroundImagePath and not self.cView.backgroundImagePathIsEmbeded:
            self.actionEmbedBackgroundImage.setVisible(True)
        else:
            self.actionEmbedBackgroundImage.setVisible(False)

        menu.addActions((self.actionPaste,
                         self.actionPasteAsPlainText,
                         menu.addSeparator(),
                         self.actionSetBackgroundImage,
                         self.actionClearBackgroundImage,
                         self.actionEmbedBackgroundImage,
                         menu.addSeparator(),
                         self.actionChangeBackgroundColor,
                         menu.addSeparator(),
                         menu.addMenu(self.zoomMenu),
                         menu.addSeparator(),
                         self.actionCleanMode
                         ))

        menu.exec(pos)  # sync, blocks main loop, modal
        # baska yerlerde popup kullaniyoruz, viewda olmuyor, menu acilip hemen kapaniyor.
        # menu.popup(pos)  # async , does not block main lopp, non modal

    # ---------------------------------------------------------------------
    def ekran_kutuphane_context_menu_goster(self, pos):

        self.kutuphaneEkranContextMenu.exec(pos)  # sync, blocks main loop, modal
        # baska yerlerde popup kullaniyoruz, viewda olmuyor, menu acilip hemen kapaniyor.
        # menu.popup(pos)  # async , does not block main lopp, non modal

    # ---------------------------------------------------------------------
    def stil_uygula_yuzen_listwidget_goster_gizle(self):

        # if not self.yuzenStylePresetsListWidget.isVisible():
        if not self.stillerYuzenWidget.isVisible():
            self.stillerYuzenWidget.move(self.cView.mapFromGlobal(QCursor.pos()))
            # self.yuzenStylePresetsListWidget.resize(250, self.yuzenStylePresetsListWidget.count() * 21)
            # self.stillerYuzenWidget.adjustSize()
            self.stillerYuzenWidget.setVisible(True)
        else:
            self.stillerYuzenWidget.setVisible(False)

    # ---------------------------------------------------------------------
    def stil_uygula_yuzen_listwidget_goster_gizle2(self):

        # if not self.yuzenStylePresetsListWidget.isVisible():
        if not self.stillerDW.isVisible():
            self.stillerDW.setFloating(True)
            self.stillerDW.move(self.cView.mapFromGlobal(QCursor.pos()))
            # self.yuzenStylePresetsListWidget.resize(250, self.yuzenStylePresetsListWidget.count() * 21)
            # self.stillerYuzenWidget.adjustSize()
            self.stillerDW.setVisible(True)
        else:
            self.stillerDW.setVisible(False)

    # ---------------------------------------------------------------------
    def nesne_ozellikleriYW_goster_gizle(self):

        # if not self.yuzenStylePresetsListWidget.isVisible():
        if not self.nesneOzellikleriYW.isVisible():
            self.nesneOzellikleriYW.move(self.cView.mapFromGlobal(QCursor.pos()))
            # self.yuzenStylePresetsListWidget.resize(250, self.yuzenStylePresetsListWidget.count() * 21)
            # self.stillerYuzenWidget.adjustSize()
            self.nesneOzellikleriYW.setVisible(True)
        else:
            self.nesneOzellikleriYW.setVisible(False)

    # ---------------------------------------------------------------------
    def olustur_nesne_ozellikleriYW(self):

        # self.arkaPlanRengi vs iptal edilince, nesneye bile tiklasak, secim aracina geciyor, sahneye tiklasa yine ayni
        # kalemde iken de kalem secili zaten
        self.nesneOzellikleriYW = NesneOzellikleriYuzenWidget(self.cScene.aktifArac.arkaPlanRengi, # secim toolu
                                                              self.cScene.aktifArac.yaziRengi, 
                                                              self.cScene.aktifArac.cizgiRengi,
                                                              self.cScene.aktifArac.cizgiKalinligi, self)
        self.nesneOzellikleriYW.hide()
        self.nesneOzellikleriYW.arkaPlanRengiDegisti.connect(self.act_set_item_background_color)
        self.nesneOzellikleriYW.yaziRengiDegisti.connect(self.act_set_item_text_color)
        self.nesneOzellikleriYW.cizgiRengiDegisti.connect(self.act_set_item_line_color)
        self.nesneOzellikleriYW.cizgiKalinligiDegisti.connect(self.act_cizgi_kalinligi_degistir)
        self.nesneOzellikleriYW.cizgiKalinligiDegisti.connect(
            lambda x: self.cizgiKalinligiDSliderWithDSBox_tbar.setValue(x * 10))

    # ---------------------------------------------------------------------
    def olustur_tools_toolbar(self):
        self.toolsToolBar = QToolBar(self)
        self.toolsToolBar.setObjectName("toolsToolBar")
        self.toolsToolBar.setWindowTitle(self.tr("Tools Tool Bar"))
        self.toolsToolBar.setIconSize(QSize(16, 16))

        actionGroup = QActionGroup(self)

        self.actionSwitchToSelectionTool = QAction(QIcon(':icons/arrow.png'), self.tr("Select"), actionGroup)
        self.actionSwitchToSelectionTool.setShortcut(QKeySequence("Q"))
        self.actionSwitchToSelectionTool.triggered.connect(self.act_switch_to_selection_tool)
        self.actionSwitchToSelectionTool.setCheckable(True)

        self.actionAddTextItem = QAction(QIcon(':icons/t.png'), self.tr("Add Text"), actionGroup)
        self.actionAddTextItem.setShortcut(QKeySequence("T"))
        self.actionAddTextItem.triggered.connect(self.act_add_text_item)
        self.actionAddTextItem.setCheckable(True)

        self.actionAddRectItem = QAction(QIcon(':icons/rectangle.png'), self.tr("Add Rectangle"), actionGroup)
        self.actionAddRectItem.setShortcut(QKeySequence("R"))
        self.actionAddRectItem.triggered.connect(self.act_add_rect_item)
        self.actionAddRectItem.setCheckable(True)

        self.actionAddEllipseItem = QAction(QIcon(':icons/circle.png'), self.tr("Add Ellipse"), actionGroup)
        self.actionAddEllipseItem.setShortcut(QKeySequence("E"))
        self.actionAddEllipseItem.triggered.connect(self.act_add_ellipse_item)
        self.actionAddEllipseItem.setCheckable(True)

        self.actionDrawLineItem = QAction(QIcon(':icons/line.png'), self.tr("Draw Line"), actionGroup)
        self.actionDrawLineItem.setShortcut(QKeySequence("L"))
        self.actionDrawLineItem.triggered.connect(self.act_draw_line_item)
        self.actionDrawLineItem.setCheckable(True)

        self.actionDrawPathItem = QAction(QIcon(':icons/pen.png'), self.tr("Draw Path"), actionGroup)
        self.actionDrawPathItem.setShortcut(QKeySequence("D"))
        self.actionDrawPathItem.triggered.connect(self.act_draw_path_item)
        self.actionDrawPathItem.setCheckable(True)

        # self.actionAddImageItem = QAction(QIcon(':icons/file-image.png'), self.tr("Add Image"), actionGroup)
        # self.actionAddImageItem.setShortcut(QKeySequence("I"))
        # self.actionAddImageItem.triggered.connect(self.act_add_image_item)
        # self.actionAddImageItem.setCheckable(True)
        # self.recentImagesMenu.setEnabled(False)
        # self.actionAddImageItem.setMenu(self.recentImagesMenu)
        self.recentImagesMenu = QMenu(self.toolsToolBar)
        self.recentImagesMenu.setIcon(QIcon(':icons/file-image.png'))
        self.recentImagesMenu.setTitle(self.tr("Add Image"))
        self.actionAddImageItem = self.recentImagesMenu.menuAction()
        self.actionAddImageItem.setShortcut(QKeySequence("I"))
        self.actionAddImageItem.triggered.connect(self.act_add_image_item)
        self.recentImagesMenu.aboutToShow.connect(self.on_recent_images_menu_about_to_show)

        self.actionAddVideoItem = QAction(QIcon(':icons/file-video.png'), self.tr("Add Video"), actionGroup)
        self.actionAddVideoItem.setShortcut(QKeySequence("V"))
        self.actionAddVideoItem.triggered.connect(self.act_add_video_item)
        self.actionAddVideoItem.setCheckable(True)

        self.actionEkleDosyaNesnesi = QAction(QIcon(':icons/import-file.png'), self.tr("Add File"), actionGroup)
        self.actionEkleDosyaNesnesi.setShortcut(QKeySequence("O"))
        self.actionEkleDosyaNesnesi.triggered.connect(self.act_ekle_dosya_nesnesi)
        self.actionEkleDosyaNesnesi.setCheckable(True)

        self.actionWebBrowserAc = QAction(QIcon(':icons/web-browser.png'), self.tr("Web Browser"), actionGroup)
        self.actionWebBrowserAc.setShortcut(QKeySequence("W"))
        self.actionWebBrowserAc.triggered.connect(self.act_web_browser_ac)
        # self.actionWebBrowserAc.setCheckable(True)

        self.toolsToolBar.addActions((self.actionSwitchToSelectionTool,
                                      self.actionAddRectItem,
                                      self.actionAddEllipseItem,
                                      self.actionDrawLineItem,
                                      self.actionAddTextItem,
                                      self.actionDrawPathItem,
                                      self.actionAddImageItem,
                                      self.actionAddVideoItem,
                                      self.actionEkleDosyaNesnesi,
                                      self.actionWebBrowserAc,
                                      ))

        self.addToolBar(self.toolsToolBar)

    # ---------------------------------------------------------------------
    def olustur_properties_toolbar(self):
        self.propertiesToolBar = QToolBar(self)
        self.propertiesToolBar.setObjectName("propertiesToolBar")
        self.propertiesToolBar.setWindowTitle(self.tr("Item Properties Tool Bar"))
        self.propertiesToolBar.setIconSize(QSize(16, 16))

        self.itemWidthSBox_tbar = SpinBox(self.propertiesToolBar)
        self.itemWidthSBox_tbar.setSuffix(" w")
        self.itemWidthSBox_tbar.setMinimum(1)
        self.itemWidthSBox_tbar.setMaximum(99999)
        self.itemWidthSBox_tbar.setSingleStep(1)
        self.itemWidthSBox_tbar.setValue(int(self.itemSize.width()))
        self.itemWidthSBox_tbar.setToolTip(self.tr("Width"))
        self.itemWidthSBox_tbar.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_item_width)

        self.itemHeightSBox_tbar = SpinBox(self.propertiesToolBar)
        self.itemHeightSBox_tbar.setSuffix(" h")
        self.itemHeightSBox_tbar.setMinimum(1)
        self.itemHeightSBox_tbar.setMaximum(99999)
        self.itemHeightSBox_tbar.setSingleStep(1)
        self.itemHeightSBox_tbar.setValue(int(self.itemSize.height()))
        self.itemHeightSBox_tbar.setToolTip(self.tr("Height"))
        self.itemHeightSBox_tbar.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_item_height)

        self.itemRotationSBox_tbar = SpinBoxForRotation(self.propertiesToolBar)
        self.itemRotationSBox_tbar.setSuffix(u"\u00b0")
        self.itemRotationSBox_tbar.setValue(0)
        self.itemRotationSBox_tbar.setMinimum(-1)
        self.itemRotationSBox_tbar.setMaximum(360)
        self.itemRotationSBox_tbar.setSingleStep(1)
        self.itemRotationSBox_tbar.setToolTip(self.tr("Rotation"))
        self.itemRotationSBox_tbar.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_item_rotation)

        self.itemWidthSBoxAction = self.propertiesToolBar.addWidget(self.itemWidthSBox_tbar)
        self.itemHeightSBoxAction = self.propertiesToolBar.addWidget(self.itemHeightSBox_tbar)
        self.itemRotationSBoxAction = self.propertiesToolBar.addWidget(self.itemRotationSBox_tbar)

        self.addToolBar(self.propertiesToolBar)

    # ---------------------------------------------------------------------
    def olustur_cizgi_ozellikleri_toolbar(self):
        self.cizgiOzellikleriToolBar = QToolBar(self)
        self.cizgiOzellikleriToolBar.setObjectName("cizgiOZellikleriToolBar")
        self.cizgiOzellikleriToolBar.setWindowTitle(self.tr("Line && Pen Properties Tool Bar"))
        self.cizgiOzellikleriToolBar.setIconSize(QSize(16, 16))

        # ---- cizgi kalinligi -----------------------------------------------------------------

        # ---- cizgi kalinligi -----------------------------------------------------------------
        self.cizgiKalinligiDSliderWithDSBox_tbar = SliderDoubleWithDoubleSpinBox(yerlesim=Qt.Horizontal,
                                                                                 parent=self.cizgiOzellikleriToolBar)
        # self.cizgiKalinligiSBox.setSuffix(" h")
        self.cizgiKalinligiDSliderWithDSBox_tbar.setMaximumWidth(150)
        self.cizgiKalinligiDSliderWithDSBox_tbar.setMinimum(0)
        self.cizgiKalinligiDSliderWithDSBox_tbar.setMaximum(100)
        self.cizgiKalinligiDSliderWithDSBox_tbar.setSingleStep(0.1)
        self.cizgiKalinligiDSliderWithDSBox_tbar.setValue(self.cScene.aktifArac.cizgiKalinligi * 10)
        # self.cizgiKalinligiSBox.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_item_height)
        self.cizgiKalinligiDSliderWithDSBox_tbar.setToolTip(self.tr("Line Width"))
        self.cizgiKalinligiDSliderWithDSBox_tbar.degerDegisti.connect(self.act_cizgi_kalinligi_degistir)

        self.cizgiOzellikleriToolBar.addWidget(self.cizgiKalinligiDSliderWithDSBox_tbar)

        self.addToolBar(self.cizgiOzellikleriToolBar)

    # ---------------------------------------------------------------------
    def olustur_font_toolbar(self):
        self.fontToolBar = QToolBar(self.tr("Font Tool Bar"), self)
        self.fontToolBar.setObjectName("fontToolBar")
        self.fontToolBar.setWindowTitle(self.tr("Font Tool Bar"))
        self.fontToolBar.setIconSize(QSize(16, 16))

        self.fontCBox_tbar = FontComboBox(self.fontToolBar)
        # self.fontCBox_tbar.activated[str].connect(self.act_set_current_font)
        # self.fontCBox_tbar.currentFontChanged.connect(self.set_text_family)
        # self.fontCBox_tbar.currentIndexChanged.connect(self.act_change_font)
        self.fontCBox_tbar.setCurrentFont(self.currentFont)
        self.fontCBox_tbar.valueChangedFromFontComboBoxGuiNotByCode.connect(self.act_set_current_font)

        # self.textSizeSBox_tbar = QSpinBox(self.fontToolBar)
        self.textSizeSBox_tbar = SpinBox(self.fontToolBar)
        self.textSizeSBox_tbar.setSuffix(" pt")
        self.textSizeSBox_tbar.setValue(self.textSize)
        self.textSizeSBox_tbar.setMinimum(5)
        self.textSizeSBox_tbar.setMaximum(999)
        self.textSizeSBox_tbar.setSingleStep(1)
        # self.textSizeSBox_tbar.valueChanged[int].connect(self.act_change_item_size)
        self.textSizeSBox_tbar.valueChangedFromSpinBoxGuiNotBySetValue.connect(self.act_change_text_size)
        self.textSizeSBox_tbar.setToolTip(self.tr("Text Size"))

        self.actionBold = QAction(QIcon(':icons/bold.png'),
                                  self.tr("Bold"),
                                  self, priority=QAction.LowPriority,
                                  shortcut=Qt.CTRL + Qt.Key_B,
                                  triggered=self.act_bold,
                                  checkable=True)
        # bold = QFont()
        # bold.setBold(True)
        # self.actionBold.setFont(bold)

        self.actionItalic = QAction(QIcon(':icons/italic.png'),
                                    self.tr("Italic"),
                                    self, priority=QAction.LowPriority,
                                    shortcut=Qt.CTRL + Qt.Key_I,
                                    triggered=self.act_italic,
                                    checkable=True)
        # italic = QFont()
        # italic.setItalic(True)
        # self.actionItalic.setFont(italic)

        self.actionUnderline = QAction(QIcon(':icons/underline.png'),
                                       self.tr("Underline"),
                                       self,
                                       priority=QAction.LowPriority,
                                       shortcut=Qt.CTRL + Qt.Key_U,
                                       triggered=self.act_underline,
                                       checkable=True)
        # underline = QFont()
        # underline.setUnderline(True)
        # self.actionUnderline.setFont(underline)

        self.actionStrikeOut = QAction(QIcon(':icons/strikeout.png'),
                                       self.tr("Strike Out"),
                                       self,
                                       priority=QAction.LowPriority,
                                       shortcut=Qt.CTRL + Qt.Key_U,
                                       triggered=self.act_strikeout,
                                       checkable=True)
        # strikeout = QFont()
        # strikeout.setStrikeOut(True)
        # self.actionUnderline.setFont(strikeout)

        self.actionOverline = QAction(QIcon(':icons/overline.png'),
                                      self.tr("Overline"),
                                      self,
                                      priority=QAction.LowPriority,
                                      shortcut=Qt.CTRL + Qt.Key_U,
                                      triggered=self.act_overline,
                                      checkable=True)
        # overline = QFont()
        # overline.setOverline(True)
        # self.actionOverline.setFont(overline)

        grp = QActionGroup(self.fontToolBar)
        grp.triggered.connect(self.act_yazi_hizala_action)

        self.actionYaziHizalaSola = QAction(QIcon(':icons/yazi-hizala-sola.png'),
                                            self.tr("Align Left"), grp)

        self.actionYaziHizalaOrtala = QAction(QIcon(':icons/yazi-hizala-ortala.png'),
                                              self.tr("Centered"), grp)

        self.actionYaziHizalaSaga = QAction(QIcon(':icons/yazi-hizala-saga.png'),
                                            self.tr("Align Right"), grp)

        self.actionYaziHizalaSigdir = QAction(QIcon(':icons/yazi-hizala-sigdir.png'),
                                              self.tr("Justify"), grp)

        self.actionYaziHizalaSola.setShortcut(Qt.CTRL + Qt.Key_L)
        self.actionYaziHizalaSola.setCheckable(True)
        self.actionYaziHizalaSola.setPriority(QAction.LowPriority)
        # self.actionYaziHizalaSola.hovered.connect(lambda: self._statusBar.showMessage("sola yanastir", 500))

        self.actionYaziHizalaOrtala.setShortcut(Qt.CTRL + Qt.Key_E)
        self.actionYaziHizalaOrtala.setCheckable(True)
        self.actionYaziHizalaOrtala.setPriority(QAction.LowPriority)

        self.actionYaziHizalaSaga.setShortcut(Qt.CTRL + Qt.Key_R)
        self.actionYaziHizalaSaga.setCheckable(True)
        self.actionYaziHizalaSaga.setPriority(QAction.LowPriority)

        self.actionYaziHizalaSigdir.setShortcut(Qt.CTRL + Qt.Key_J)
        self.actionYaziHizalaSigdir.setCheckable(True)
        self.actionYaziHizalaSigdir.setPriority(QAction.LowPriority)

        # self.fontToolBar.addSeparator()
        self.fontCBox_tbarAction = self.fontToolBar.addWidget(self.fontCBox_tbar)
        self.textSizeSBox_tbarAction = self.fontToolBar.addWidget(self.textSizeSBox_tbar)

        self.fontToolBar.addActions((
            self.fontToolBar.addSeparator(),
            self.actionBold,
            self.actionItalic,
            self.actionUnderline,
            self.actionStrikeOut,
            self.actionOverline,
            self.fontToolBar.addSeparator(),
            self.actionYaziHizalaSola,
            self.actionYaziHizalaOrtala,
            self.actionYaziHizalaSaga,
            self.actionYaziHizalaSigdir,
        ))

        self.addToolBar(self.fontToolBar)
        self.addToolBarBreak(Qt.TopToolBarArea)

    # ---------------------------------------------------------------------
    def olustur_renk_toolbar(self):

        self.renkAracCubugu = QToolBar(self.tr("Color Tool Bar"), self)
        self.renkAracCubugu.setObjectName("renkAracCubugu")
        self.renkAracCubugu.setWindowTitle(self.tr("Color Tool Bar"))
        self.renkAracCubugu.setIconSize(QSize(16, 16))

        self.actionItemBackgroundColor = QAction(QIcon(), self.tr("Item's Background Color"),
                                                 self.renkAracCubugu)
        self.actionItemBackgroundColor.triggered.connect(self.act_set_item_background_color)

        self.actionItemTextColor = QAction(QIcon(), self.tr("Text Color"), self.renkAracCubugu)
        self.actionItemTextColor.triggered.connect(self.act_set_item_text_color)
        self.degistir_yazi_rengi_ikonu()

        self.actionItemLineColor = QAction(QIcon(), self.tr("Line Color"), self.renkAracCubugu)
        self.actionItemLineColor.triggered.connect(self.act_set_item_line_color)
        self.degistir_cizgi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=True)

        self.renkAracCubugu.addActions((
            self.actionItemLineColor,
            self.actionItemTextColor,
            self.actionItemBackgroundColor,

        ))

        self.addToolBar(self.renkAracCubugu)
        self.addToolBarBreak(Qt.TopToolBarArea)

    # ---------------------------------------------------------------------
    def karakter_bicimi_degisti(self, sozluk=None):

        if not sozluk:
            sozluk = self.cScene.activeItem.ver_karakter_bicimi()
            # self.currentFont = QFont(self.cScene.activeItem.font())
            # self.cScene.setFont(self.currentFont)

        self.actionBold.setChecked(sozluk["b"])
        self.actionItalic.setChecked(sozluk["i"])
        self.actionUnderline.setChecked(sozluk["u"])
        self.actionStrikeOut.setChecked(sozluk["s"])
        self.actionOverline.setChecked(sozluk["o"])

        self.btnBold.setChecked(sozluk["b"])
        self.btnItalic.setChecked(sozluk["i"])
        self.btnUnderline.setChecked(sozluk["u"])
        self.btnStrikeOut.setChecked(sozluk["s"])
        self.btnOverline.setChecked(sozluk["o"])

    # ---------------------------------------------------------------------
    def yazi_nesnesi_iceriginin_karakter_bicimini_degistir(self, bicim):
        # bu degisiklikleri yazi nesnesinin documentinin undo redo stacki takip eder.
        if len(self.cScene.selectionQueue) == 1:
            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                if self.cScene.activeItem.hasFocus():
                    cursor = self.cScene.activeItem.textCursor()
                    if not cursor.hasSelection():
                        cursor.select(QTextCursor.WordUnderCursor)
                    cursor.mergeCharFormat(bicim)
                    self.cScene.activeItem.setTextCursor(cursor)
                    return

    # ---------------------------------------------------------------------
    def nesne_duzeyinde_karakter_bicimi_degistir(self, aciklama):

        sozluk = {"b": self.actionBold.isChecked(),
                  "i": self.actionItalic.isChecked(),
                  "u": self.actionUnderline.isChecked(),
                  "s": self.actionStrikeOut.isChecked(),
                  "o": self.actionOverline.isChecked(),
                  }

        if self.cScene.selectionQueue:
            startedMacro = False
            for item in self.cScene.selectionQueue:
                if item.type() == shared.GROUP_ITEM_TYPE:
                    continue
                if not startedMacro:
                    self.cScene.undoStack.beginMacro(aciklama)
                    startedMacro = True
                undoRedo.undoableSetCharacterFormat(self.cScene.undoStack, aciklama, item, sozluk)
            if startedMacro:
                self.cScene.undoStack.endMacro()

    # ---------------------------------------------------------------------
    def act_bold(self, from_button=False):

        if from_button:
            self.actionBold.setChecked(self.btnBold.isChecked())
        else:
            self.btnBold.setChecked(self.actionBold.isChecked())

        if len(self.cScene.selectionQueue) == 0:
            self.currentFont.setBold(self.actionBold.isChecked())
            self.cScene.setFont(QFont(self.currentFont))
            self.karakter_bicimi_sozluk["b"] = self.actionBold.isChecked()

        aciklama = self.tr("bold")
        if len(self.cScene.selectionQueue) == 1:
            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                if self.cScene.activeItem.hasFocus():
                    # text item secili ve focuslanmis iken degisiklikleri text itemin undoredo stacki takip etsin diye
                    fmt = QTextCharFormat()
                    # fmt.setFontWeight(self.actionBold.isChecked() and QFont.Bold or QFont.Normal)
                    fmt.setFontWeight(self.actionBold.isChecked())
                    self.yazi_nesnesi_iceriginin_karakter_bicimini_degistir(fmt)
                    return

        self.nesne_duzeyinde_karakter_bicimi_degistir(aciklama)

    # ---------------------------------------------------------------------
    def act_underline(self, from_button=False):

        if from_button:
            self.actionUnderline.setChecked(self.btnUnderline.isChecked())
        else:
            self.btnUnderline.setChecked(self.actionUnderline.isChecked())

        if len(self.cScene.selectionQueue) == 0:
            self.currentFont.setUnderline(self.actionUnderline.isChecked())
            self.cScene.setFont(QFont(self.currentFont))
            self.karakter_bicimi_sozluk["u"] = self.actionUnderline.isChecked()

        aciklama = self.tr("underline")
        if len(self.cScene.selectionQueue) == 1:
            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                if self.cScene.activeItem.hasFocus():
                    # text item secili ve focuslanmis iken degisiklikleri text itemin undoredo stacki takip etsin diye
                    fmt = QTextCharFormat()
                    # fmt.setFontWeight(self.actionBold.isChecked() and QFont.Bold or QFont.Normal)
                    fmt.setFontWeight(self.actionUnderline.isChecked())
                    self.yazi_nesnesi_iceriginin_karakter_bicimini_degistir(fmt)
                    return

        self.nesne_duzeyinde_karakter_bicimi_degistir(aciklama)

    # ---------------------------------------------------------------------
    def act_italic(self, from_button=False):

        if from_button:
            self.actionItalic.setChecked(self.btnItalic.isChecked())
        else:
            self.btnItalic.setChecked(self.actionItalic.isChecked())

        if len(self.cScene.selectionQueue) == 0:
            self.currentFont.setItalic(self.actionItalic.isChecked())
            self.cScene.setFont(QFont(self.currentFont))
            self.karakter_bicimi_sozluk["i"] = self.actionItalic.isChecked()

        aciklama = self.tr("italic")
        if len(self.cScene.selectionQueue) == 1:
            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                if self.cScene.activeItem.hasFocus():
                    # text item secili ve focuslanmis iken degisiklikleri text itemin undoredo stacki takip etsin diye
                    fmt = QTextCharFormat()
                    # fmt.setFontWeight(self.actionBold.isChecked() and QFont.Bold or QFont.Normal)
                    fmt.setFontWeight(self.actionItalic.isChecked())
                    self.yazi_nesnesi_iceriginin_karakter_bicimini_degistir(fmt)
                    return

        self.nesne_duzeyinde_karakter_bicimi_degistir(aciklama)

    # ---------------------------------------------------------------------
    def act_strikeout(self, from_button=False):

        if from_button:
            self.actionStrikeOut.setChecked(self.btnStrikeOut.isChecked())
        else:
            self.btnStrikeOut.setChecked(self.actionStrikeOut.isChecked())

        if len(self.cScene.selectionQueue) == 0:
            self.currentFont.setStrikeOut(self.actionStrikeOut.isChecked())
            self.cScene.setFont(QFont(self.currentFont))
            self.karakter_bicimi_sozluk["s"] = self.actionStrikeOut.isChecked()

        aciklama = self.tr("strikeout")
        if len(self.cScene.selectionQueue) == 1:
            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                if self.cScene.activeItem.hasFocus():
                    # text item secili ve focuslanmis iken degisiklikleri text itemin undoredo stacki takip etsin diye
                    fmt = QTextCharFormat()
                    # fmt.setFontWeight(self.actionBold.isChecked() and QFont.Bold or QFont.Normal)
                    fmt.setFontWeight(self.actionStrikeOut.isChecked())
                    self.yazi_nesnesi_iceriginin_karakter_bicimini_degistir(fmt)
                    return

        self.nesne_duzeyinde_karakter_bicimi_degistir(aciklama)

    # ---------------------------------------------------------------------
    def act_overline(self, from_button=False):

        if from_button:
            self.actionOverline.setChecked(self.btnOverline.isChecked())
        else:
            self.btnOverline.setChecked(self.actionOverline.isChecked())

        if len(self.cScene.selectionQueue) == 0:
            self.currentFont.setOverline(self.actionOverline.isChecked())
            self.cScene.setFont(QFont(self.currentFont))
            self.karakter_bicimi_sozluk["o"] = self.actionOverline.isChecked()

        aciklama = self.tr("overline")
        if len(self.cScene.selectionQueue) == 1:
            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                if self.cScene.activeItem.hasFocus():
                    # text item secili ve focuslanmis iken degisiklikleri text itemin undoredo stacki takip etsin diye
                    fmt = QTextCharFormat()
                    # fmt.setFontWeight(self.actionBold.isChecked() and QFont.Bold or QFont.Normal)
                    fmt.setFontWeight(self.actionOverline.isChecked())
                    self.yazi_nesnesi_iceriginin_karakter_bicimini_degistir(fmt)
                    return

        self.nesne_duzeyinde_karakter_bicimi_degistir(aciklama)

    # ---------------------------------------------------------------------
    def act_set_text_style(self, styleIndex):
        # cursor = self.cTab.textCursor()

        if len(self.cScene.selectionQueue) == 1:
            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                # if self.cScene.activeItem.hasFocus():
                cursor = self.cScene.activeItem.textCursor()
                if styleIndex:
                    styleDict = {
                        1: QTextListFormat.ListDisc,
                        2: QTextListFormat.ListCircle,
                        3: QTextListFormat.ListSquare,
                        4: QTextListFormat.ListDecimal,
                        5: QTextListFormat.ListLowerAlpha,
                        6: QTextListFormat.ListUpperAlpha,
                        7: QTextListFormat.ListLowerRoman,
                        8: QTextListFormat.ListUpperRoman,
                    }

                    style = styleDict.get(styleIndex, QTextListFormat.ListDisc)
                    cursor.beginEditBlock()
                    blockFmt = cursor.blockFormat()
                    listFmt = QTextListFormat()

                    if cursor.currentList():
                        listFmt = cursor.currentList().format()
                    else:
                        listFmt.setIndent(blockFmt.indent() + 1)
                        blockFmt.setIndent(0)
                        cursor.setBlockFormat(blockFmt)

                    listFmt.setStyle(style)
                    cursor.createList(listFmt)
                    cursor.endEditBlock()
                else:
                    bfmt = QTextBlockFormat()
                    bfmt.setObjectIndex(-1)
                    cursor.mergeBlockFormat(bfmt)

    # ---------------------------------------------------------------------
    @Slot(QAction)
    def act_yazi_hizala_action(self, action):
        aciklama = self.tr("align")
        if action == self.actionYaziHizalaSola:
            self.btnYaziHizalaSola.setChecked(True)
            aciklama = self.tr("align left")
            hiza = Qt.AlignLeft
        elif action == self.actionYaziHizalaOrtala or action == self.btnYaziHizalaOrtala:
            self.btnYaziHizalaOrtala.setChecked(True)
            aciklama = self.tr("align center")
            hiza = Qt.AlignCenter
        elif action == self.actionYaziHizalaSaga or action == self.btnYaziHizalaSaga:
            self.btnYaziHizalaSaga.setChecked(True)
            aciklama = self.tr("align right")
            hiza = Qt.AlignRight
        elif action == self.actionYaziHizalaSigdir or action == self.btnYaziHizalaSigdir:
            self.btnYaziHizalaSigdir.setChecked(True)
            aciklama = self.tr("align justify")
            hiza = Qt.AlignJustify
        else:
            hiza = Qt.AlignLeft

        self._yazi_hizala(hiza, aciklama)

    # ---------------------------------------------------------------------
    @Slot(QAction)
    def act_yazi_hizala_btn(self, btn):
        aciklama = self.tr("align")
        if btn == self.btnYaziHizalaSola:
            self.actionYaziHizalaSola.setChecked(True)
            aciklama = self.tr("align left")
            hiza = Qt.AlignLeft
        elif btn == self.btnYaziHizalaOrtala:
            self.actionYaziHizalaOrtala.setChecked(True)
            aciklama = self.tr("align center")
            hiza = Qt.AlignCenter
        elif btn == self.btnYaziHizalaSaga:
            self.actionYaziHizalaSaga.setChecked(True)
            aciklama = self.tr("align right")
            hiza = Qt.AlignRight
        elif btn == self.btnYaziHizalaSigdir:
            self.actionYaziHizalaSigdir.setChecked(True)
            aciklama = self.tr("align justify")
            hiza = Qt.AlignJustify
        else:
            hiza = Qt.AlignLeft

        self._yazi_hizala(hiza, aciklama)

    # ---------------------------------------------------------------------
    def _yazi_hizala(self, hiza, aciklama):
        if not self.cScene.selectionQueue:
            self.yazi_hizasi = hiza

        else:
            startedMacro = False
            for item in self.cScene.selectionQueue:
                if item.type() == shared.GROUP_ITEM_TYPE:
                    continue
                if not startedMacro:
                    self.cScene.undoStack.beginMacro(aciklama)
                    startedMacro = True
                undoRedo.undoableSetTextAlignment(self.cScene.undoStack, aciklama, item, hiza)
            if startedMacro:
                self.cScene.undoStack.endMacro()

    # ---------------------------------------------------------------------
    def yazi_hizalama_degisti(self, hiza=None):
        if not hiza:
            hiza = self.cScene.activeItem.ver_yazi_hizasi()

        if hiza == Qt.AlignLeft or hiza == Qt.AlignLeft | Qt.AlignVCenter:
            self.actionYaziHizalaSola.setChecked(True)
            self.btnYaziHizalaSola.setChecked(True)
        if hiza == Qt.AlignCenter or hiza == Qt.AlignCenter | Qt.AlignVCenter:
            self.actionYaziHizalaOrtala.setChecked(True)
            self.btnYaziHizalaOrtala.setChecked(True)
        if hiza == Qt.AlignRight or hiza == Qt.AlignRight | Qt.AlignVCenter:
            self.actionYaziHizalaSaga.setChecked(True)
            self.btnYaziHizalaSaga.setChecked(True)
        if hiza == Qt.AlignJustify or hiza == Qt.AlignJustify | Qt.AlignVCenter:
            self.actionYaziHizalaSigdir.setChecked(True)
            self.btnYaziHizalaSigdir.setChecked(True)

    # ---------------------------------------------------------------------
    def olustur_align_toolbar(self):
        self.alignToolBar = QToolBar(self)
        self.alignToolBar.setObjectName("alignToolBar")
        self.alignToolBar.setWindowTitle(self.tr("Align Tool Bar"))
        self.alignToolBar.setIconSize(QSize(16, 16))

        self.actionMirrorX = QAction(QIcon(':icons/mirror-x.png'), self.tr("Mirror X"), self.alignToolBar)
        self.actionMirrorX.setShortcut(QKeySequence("M"))
        self.actionMirrorX.triggered.connect(self.act_pre_mirror_x)

        self.actionMirrorY = QAction(QIcon(':icons/mirror-y.png'), self.tr("Mirror Y"), self.alignToolBar)
        self.actionMirrorY.setShortcut(QKeySequence("B"))
        self.actionMirrorY.triggered.connect(self.act_pre_mirror_y)

        self.actionAlignLeft = QAction(QIcon(':icons/align-left-edges.png'), self.tr("Align left edges"),
                                       self.alignToolBar)
        self.actionAlignLeft.setShortcut(QKeySequence("Shift+Ctrl+Left"))
        self.actionAlignLeft.triggered.connect(self.act_align_left)

        self.actionAlignRight = QAction(QIcon(':icons/align-right-edges.png'), self.tr("Align right edges"),
                                        self.alignToolBar)
        self.actionAlignRight.setShortcut(QKeySequence("Shift+Ctrl+Right"))
        self.actionAlignRight.triggered.connect(self.act_align_right)

        self.actionAlignTop = QAction(QIcon(':icons/align-top-edges.png'), self.tr("Align top edges"),
                                      self.alignToolBar)
        self.actionAlignTop.setShortcut(QKeySequence("Shift+Ctrl+Up"))
        self.actionAlignTop.triggered.connect(self.act_align_top)

        self.actionAlignBottom = QAction(QIcon(':icons/align-bottom-edges.png'), self.tr("Align bottom edges"),
                                         self.alignToolBar)
        self.actionAlignBottom.setShortcut(QKeySequence("Shift+Ctrl+Down"))
        self.actionAlignBottom.triggered.connect(self.act_align_bottom)

        self.actionAlignVerticalCenter = QAction(QIcon(':icons/align-centers-vertically.png'),
                                                 self.tr("Align centers vertically"), self.alignToolBar)
        self.actionAlignVerticalCenter.setShortcut(QKeySequence("Shift+Ctrl+V"))
        self.actionAlignVerticalCenter.triggered.connect(self.act_align_vertical_center)

        self.actionAlignHorizontalCenter = QAction(QIcon(':icons/align-centers-horizontally.png'),
                                                   self.tr("Align centers horizontally"), self.alignToolBar)
        self.actionAlignHorizontalCenter.setShortcut(QKeySequence("Shift+Ctrl+H"))
        self.actionAlignHorizontalCenter.triggered.connect(self.act_align_horizontal_center)

        self.actionEqualizeHorizontalGaps = QAction(QIcon(':icons/equalize-horizontal-gaps.png'),
                                                    self.tr("Make horizontal gaps between objects equal"),
                                                    self.alignToolBar)
        self.actionEqualizeHorizontalGaps.setShortcut(QKeySequence("Shift+Ctrl+X"))
        self.actionEqualizeHorizontalGaps.triggered.connect(self.act_equalize_horizontal_gaps)

        self.actionEqualizeVerticalGaps = QAction(QIcon(':icons/equalize-vertical-gaps.png'),
                                                  self.tr("Make vertical gaps between objects equal"),
                                                  self.alignToolBar)
        self.actionEqualizeVerticalGaps.setShortcut(QKeySequence("Shift+Ctrl+Y"))
        self.actionEqualizeVerticalGaps.triggered.connect(self.act_equalize_vertical_gaps)

        self.actionDistributeItemsVertically = QAction(QIcon(':icons/distribute-vertically.png'),
                                                       self.tr("Distribute objects"),
                                                       self.alignToolBar)
        self.actionDistributeItemsVertically.setShortcut(QKeySequence("Shift+Ctrl+D"))
        self.actionDistributeItemsVertically.triggered.connect(self.act_distribute_items_vertically)

        self.actionDistributeItemsHorizontally = QAction(QIcon(':icons/distribute-horizontally.png'),
                                                         self.tr("Distribute objects"), self.alignToolBar)
        self.actionDistributeItemsHorizontally.setShortcut(QKeySequence("Shift+Ctrl+F"))
        self.actionDistributeItemsHorizontally.triggered.connect(self.act_distribute_items_horizontally)

        self.alignToolBar.addActions((self.actionMirrorX,
                                      self.actionMirrorY,
                                      self.actionAlignLeft,
                                      self.actionAlignVerticalCenter,
                                      self.actionAlignRight,
                                      self.actionEqualizeVerticalGaps,
                                      self.actionAlignTop,
                                      self.actionAlignHorizontalCenter,
                                      self.actionAlignBottom,
                                      self.actionEqualizeHorizontalGaps,
                                      self.actionDistributeItemsVertically,
                                      self.actionDistributeItemsHorizontally

                                      ))

        # alignLeft, right, top ,bottom, yatay merkez , dikey merkez

        # distribute yatay(ust - merkez -alt) dikey(ust-merkez-alt)

        # distrubute space(yatay dikey , spacing , bu boslugu boluyor,)

        self.addToolBar(self.alignToolBar)

        # self.alignMenu = QMenu()

    # ---------------------------------------------------------------------
    def olustur_utilities_toolbar(self):
        self.utilitiesToolBar = QToolBar(self)
        self.utilitiesToolBar.setObjectName("utilitiesToolBar")
        self.utilitiesToolBar.setWindowTitle(self.tr("Utilities Tool Bar"))
        self.utilitiesToolBar.setIconSize(QSize(16, 16))

        # self.actionAlwaysOnTopToggle = QCheckBox(self.tr("±"), self.utilitiesToolBar)
        # self.actionAlwaysOnTopToggle = QCheckBox(self.tr("📌"), self.utilitiesToolBar)
        # self.actionAlwaysOnTopToggle.setIconSize(QSize(16, 16))
        # self.actionAlwaysOnTopToggle.toggled.connect(self.act_toggle_always_on_top)
        # self.actionAlwaysOnTopToggle.setToolTip(self.tr("If checked on, Defter will stay on top of other windows."))

        self.actionAlwaysOnTopToggle = QAction(QIcon(":icons/pin.png"), self.tr("Always on Top"), self.utilitiesToolBar)
        self.actionAlwaysOnTopToggle.setCheckable(True)
        self.actionAlwaysOnTopToggle.setShortcut(QKeySequence("Shift+Ctrl+Alt+T"))
        self.actionAlwaysOnTopToggle.triggered.connect(self.act_toggle_always_on_top)
        self.actionAlwaysOnTopToggle.setToolTip(self.tr("If checked on, Defter will stay on top of other windows."))

        spacerWidget = QWidget(self.utilitiesToolBar)
        spacerWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        ekranGoruntusuMenuPB = QPushButton(self.utilitiesToolBar)
        ekranGoruntusuMenuPB.setFlat(True)
        ekranGoruntusuMenuPB.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        ekranGoruntusuMenuPB.setText(self.tr("ScreenShot"))
        ekranGoruntusuMenu = QMenu(self.utilitiesToolBar)
        ekranGoruntusuMenu.aboutToShow.connect(self.on_ekranGoruntusuMenu_about_to_show)
        ekranGoruntusuMenuPB.setMenu(ekranGoruntusuMenu)

        self.actionSecimEkranGoruntusuAlCmOn = QAction(self.tr("Selected Area (Comp On)"), self.utilitiesToolBar)
        self.actionSecimEkranGoruntusuAlCmOn.setShortcut(QKeySequence(Qt.Key_Print))
        self.actionSecimEkranGoruntusuAlCmOn.triggered.connect(self.act_ekran_goruntusu_secim_cm_on)

        self.actionSecimEkranGoruntusuAlCmOff = QAction(self.tr("Selected Area (Comp Off)"), self.utilitiesToolBar)
        # self.actionSecimEkranGoruntusuAlCmOff.setShortcut(QKeySequence(Qt.Key_Print))
        self.actionSecimEkranGoruntusuAlCmOff.triggered.connect(self.act_ekran_goruntusu_secim_cm_off)

        self.actionScreenshotFullscreen = QAction(self.tr("Fullscreen"), ekranGoruntusuMenu)
        self.actionScreenshotFullscreen.triggered.connect(self.act_ekran_goruntusu_tam_ekran)

        ekranGoruntusuMenu.addActions((self.actionSecimEkranGoruntusuAlCmOn,
                                       self.actionSecimEkranGoruntusuAlCmOff,
                                       self.actionScreenshotFullscreen))

        self.utilitiesToolBar.addWidget(spacerWidget)
        # self.utilitiesToolBar.addWidget(self.actionAlwaysOnTopToggle)
        self.utilitiesToolBar.addWidget(ekranGoruntusuMenuPB)
        self.utilitiesToolBar.addAction(self.actionToggleBaskiSiniriCizimAyarlariDW)
        self.utilitiesToolBar.addAction(self.actionAlwaysOnTopToggle)

        self.addToolBar(self.utilitiesToolBar)

    # ---------------------------------------------------------------------
    @Slot()
    def on_style_presets_menu_about_to_show(self):
        self.actionSaveStylePrests.setEnabled(self.stylePresetsListWidget.count())
        self.clearStylePresetsMenu.setEnabled(self.stylePresetsListWidget.count())

    # ---------------------------------------------------------------------
    @Slot()
    def on_view_menu_about_to_show(self):
        self.actionToggleStatusBar.setChecked(self._statusBar.isVisible())
        self.actionToggleMenuBar.setChecked(self.mBar.isVisible())

    # ---------------------------------------------------------------------
    @Slot()
    def on_tool_bars_menu_about_to_show(self):
        self.actionToggleToolsToolbar.setChecked(self.toolsToolBar.isVisible())
        self.actionTogglePropertiesToolbar.setChecked(self.propertiesToolBar.isVisible())
        self.actionToggleUtilitiesToolbar.setChecked(self.utilitiesToolBar.isVisible())
        self.actionToggleAlignToolbar.setChecked(self.alignToolBar.isVisible())
        self.actionToggleFontToolbar.setChecked(self.fontToolBar.isVisible())
        self.actionToggleRenkAracCubugu.setChecked(self.renkAracCubugu.isVisible())
        self.actionTogglecizgiOzellikleriToolBar.setChecked(self.cizgiOzellikleriToolBar.isVisible())

    # ---------------------------------------------------------------------
    def act_tum_arac_cubuklarini_goster(self):
        self.toolsToolBar.setVisible(True)
        self.propertiesToolBar.setVisible(True)
        self.utilitiesToolBar.setVisible(True)
        self.alignToolBar.setVisible(True)
        self.fontToolBar.setVisible(True)
        self.renkAracCubugu.setVisible(True)
        self.cizgiOzellikleriToolBar.setVisible(True)

    # ---------------------------------------------------------------------
    @Slot()
    def on_dock_widgets_menu_about_to_show(self):
        self.actionToggleSayfalarDW.setChecked(self.sayfalarDW.isVisible())
        self.actionToggleNesneOzellikleriDW.setChecked(self.nesneOzellikleriDW.isVisible())
        self.actionToggleStillerDW.setChecked(self.stillerDW.isVisible())
        self.actionToggleKutuphaneDW.setChecked(self.kutuphaneDW.isVisible())
        self.actionToggleBaskiSiniriCizimAyarlariDW.setChecked(self.baskiSiniriCizimAyarlariDW.isVisible())

    # ---------------------------------------------------------------------
    def act_tum_panelleri_goster(self):
        self.sayfalarDW.setVisible(True)
        self.kutuphaneDW.setVisible(True)
        self.nesneOzellikleriDW.setVisible(True)
        self.stillerDW.setVisible(True)
        self.baskiSiniriCizimAyarlariDW.setVisible(True)

    # ---------------------------------------------------------------------
    # @Slot() # this is called directly from base's overriden contextMenuEvent
    def on_item_context_menu_about_to_show(self, item):

        self.actionShowInFileManager.setVisible(False)

        if item.type() == shared.TEXT_ITEM_TYPE:
            self.actionResizeTextItemToFitView.setVisible(True)
            # self.actionShowInFileManager.setVisible(True)
            self.actionExportSelectedTextItemContentAsPdf.setVisible(True)
            self.actionPrintSelectedTextItemContent.setVisible(True)

            if not item.isPlainText:
                self.actionConvertToPlainText.setVisible(True)
                self.actionShowHTMLSource.setVisible(True)
                self.actionLocalizeHtml.setVisible(True)
                self.actionShowAsWebPage.setVisible(True)
                self.actionConvertToWebItem.setVisible(True)
            else:
                self.actionShowHTMLSource.setVisible(False)
                self.actionLocalizeHtml.setVisible(False)
                self.actionConvertToPlainText.setVisible(False)
                self.actionShowAsWebPage.setVisible(False)
                self.actionConvertToWebItem.setVisible(False)

        else:
            self.actionResizeTextItemToFitView.setVisible(False)
            self.actionShowHTMLSource.setVisible(False)
            self.actionLocalizeHtml.setVisible(False)
            self.actionConvertToPlainText.setVisible(False)
            self.actionShowAsWebPage.setVisible(False)
            self.actionConvertToWebItem.setVisible(False)
            self.actionExportSelectedTextItemContentAsPdf.setVisible(False)
            self.actionPrintSelectedTextItemContent.setVisible(False)

        if item.type() == shared.IMAGE_ITEM_TYPE:
            self.actionShowInFileManager.setVisible(True)
            # self.actionEmbedImage.setVisible(True)
            self.actionExportImage.setVisible(True)
            self.actionShowImageInfo.setVisible(True)
            self.actionCrop.setVisible(True)
            if item.isEmbeded:
                # self.actionEmbedImage.setEnabled(False)
                self.actionEmbedImage.setVisible(False)
            else:
                # self.actionEmbedImage.setEnabled(True)
                self.actionEmbedImage.setVisible(True)
        else:
            self.actionExportImage.setVisible(False)
            self.actionEmbedImage.setVisible(False)
            self.actionShowImageInfo.setVisible(False)
            self.actionCrop.setVisible(False)

        if item.type() == shared.VIDEO_ITEM_TYPE:
            self.actionShowInFileManager.setVisible(True)
            # self.actionEmbedVideo,
            # self.actionExportVideo,
            # self.actionShowVideoInfo,
            self.actionExportVideo.setVisible(True)
            self.actionShowVideoInfo.setVisible(True)
            if item.isEmbeded:
                # self.actionEmbedImage.setEnabled(False)
                self.actionEmbedVideo.setVisible(False)
            else:
                # self.actionEmbedImage.setEnabled(True)
                self.actionEmbedVideo.setVisible(True)
        else:
            self.actionExportVideo.setVisible(False)
            self.actionEmbedVideo.setVisible(False)
            self.actionShowVideoInfo.setVisible(False)

        if item.isPinned:
            self.actionPinItem.setEnabled(False)
            self.actionUnPinItem.setEnabled(True)
        else:
            self.actionPinItem.setEnabled(True)
            self.actionUnPinItem.setEnabled(False)

        if item.type() == shared.DOSYA_ITEM_TYPE:
            # self.actionConvertToWebItem.setVisible(True)
            # self.actionShowAsWebPage.setVisible(True)
            self.actionShowInFileManager.setVisible(True)
            self.actionExportDosya.setVisible(True)
            self.actionShowDosyaInfo.setVisible(True)
            if item.isEmbeded:
                self.actionEmbedDosya.setVisible(False)
            else:
                self.actionEmbedDosya.setVisible(True)
        else:
            # self.actionConvertToWebItem.setVisible(True)
            # self.actionShowAsWebPage.setVisible(False)
            self.actionExportDosya.setVisible(False)
            self.actionShowDosyaInfo.setVisible(False)
            self.actionEmbedDosya.setVisible(False)

    # ---------------------------------------------------------------------
    # @Slot() # this is called directly from groups's overriden contextMenuEvent
    def on_group_item_context_menu_about_to_show(self, group):

        if group.isPinned:
            self.actionPinItem.setEnabled(False)
            self.actionUnPinItem.setEnabled(True)
        else:
            self.actionPinItem.setEnabled(True)
            self.actionUnPinItem.setEnabled(False)

    # ---------------------------------------------------------------------
    @Slot()
    def on_recent_images_menu_about_to_show(self):
        for action in self.recentImagesMenu.actions():
            if not os.path.exists(action.toolTip()):
                # self.recentImagesMenu.removeAction(action)
                action.setDisabled(True)
                action.setStatusTip(self.tr("Warning: Could not locate the file!"))

    # ---------------------------------------------------------------------
    @Slot()
    def on_scene_selection_changed(self):
        # TODO: bu item_selected ve deselectedlara tasinabilir.
        #   ve de duzenlemek lazim biraz
        # print(self.cScene.selectionQueue)
        # print(self.cScene.selectedItems())

        if self.cScene.selectedItems():
            # self.actionCut.setEnabled(True)
            self.actionCopy.setEnabled(True)
            self.actionBringToFront.setEnabled(True)
            self.actionSendToBack.setEnabled(True)
            self.actionDeleteItem.setEnabled(True)
            if self.cScene.activeItem.type() == shared.GROUP_ITEM_TYPE:
                self.actionUnGroupItems.setEnabled(True)
            else:
                self.actionUnGroupItems.setEnabled(False)

            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                self.yaziListeBicimiCBox.setEnabled(True)
            else:
                self.yaziListeBicimiCBox.setEnabled(False)

            if len(self.cScene.selectedItems()) > 1:
                self.actionParent.setEnabled(True)
                self.actionGroupItems.setEnabled(True)

            else:
                self.actionParent.setEnabled(False)
                self.actionUnParent.setEnabled(True)
                if self.cScene.activeItem.type() == shared.GROUP_ITEM_TYPE:
                    if not (self.cScene.activeItem.parentItem() or self.cScene.activeItem.parentedWithParentOperation):
                        self.actionUnParent.setEnabled(False)
                else:
                    if not (self.cScene.activeItem.parentItem() or self.cScene.activeItem.childItems()):
                        self.actionUnParent.setEnabled(False)

        else:
            # self.cScene.activeItem = None
            # self.actionCut.setEnabled(False)
            self.actionCopy.setEnabled(False)
            self.actionGroupItems.setEnabled(False)
            self.actionUnGroupItems.setEnabled(False)
            self.actionParent.setEnabled(False)
            self.actionUnParent.setEnabled(False)
            self.actionBringToFront.setEnabled(False)
            self.actionSendToBack.setEnabled(False)
            self.actionDeleteItem.setEnabled(False)
            self.yaziListeBicimiCBox.setEnabled(False)

            self.kur_sahne_arac_degerleri()

    # ---------------------------------------------------------------------
    @Slot()
    def on_recent_files_menu_about_to_show(self):

        """ populates recent files menu
        """

        self.recentFilesMenu.clear()

        for dosya in self.recentFilesQueue:
            if os.path.isfile(dosya):
                # icon = self.fsModel.fileIcon(self.fsModel.index(dosya))
                # action = QAction(icon, os.path.basename(dosya), self.recentFilesMenu)
                action = QAction(os.path.basename(dosya), self.recentFilesMenu)

                # self.connect(action, SIGNAL('triggered()'), lambda dosya=dosya: self.open_file_in_new_TAB(dosya))
                # action.triggered.connect(lambda dosya=dosya: self.open_file_in_new_TAB(dosya))

                def make_callback(_dosya):
                    return lambda: self.act_open_def_file(_dosya)

                action.triggered.connect(make_callback(dosya))

                self.recentFilesMenu.addAction(action)

    #     if self.recentFilesQueue:
    #         self.recentFilesMenu.addSeparator()
    #         self.recentFilesMenu.addAction(self.actionClearRecentFiles)
    #
    # # ---------------------------------------------------------------------
    # @Slot()
    # def act_clear_recent_files_menu(self):
    #     self.recentFilesQueue.clear()
    #     self.recentFilesMenu.clear()

    # ---------------------------------------------------------------------
    @Slot()
    def act_redo(self):
        self.lutfen_bekleyin_goster()
        self.log(self.actionRedo.text(), 5000, toStatusBarOnly=True)
        self.undoGroup.redo()
        # self.cScene.undoStack.redo()
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_undo(self):
        self.lutfen_bekleyin_goster()
        self.log(self.actionUndo.text(), 5000, toStatusBarOnly=True)
        self.undoGroup.undo()
        # self.cScene.undoStack.undo()
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_reopen_last_closed_tab(self):
        for dosya in self.recentFilesQueue:
            if os.path.isfile(dosya):
                if not self.tabWidget.set_current_widget_with_path(dosya):
                    self.act_open_def_file(dosya)
                    break

    # ---------------------------------------------------------------------
    @Slot()
    def act_switch_to_selection_tool(self):
        # print(self.theme)
        # print(self.theme.user_preferences.themes[0])
        # print(self.theme"user_preferences".themes[0])
        # self.itemWidthSBoxAction.setVisible(False)
        # self.itemHeightSBoxAction.setVisible(False)
        # self.itemRotationSBoxAction.setVisible(False)
        # self.textSizeSBox_tbarAction.setVisible(False)
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.SecimAraci)
        self.actionSwitchToSelectionTool.setChecked(True)
        self.cScene.clearSelection()
        self.radioArkaplan.setChecked(True)
        self.act_radio_secim_degisti(self.radioArkaplan)

    # ---------------------------------------------------------------------
    @Slot()
    def act_draw_line_item(self):
        # print(self.theme)
        # print(self.theme.user_preferences.themes[0])
        # print(self.theme"user_preferences".themes[0])
        # self.itemWidthSBoxAction.setVisible(False)
        # self.itemHeightSBoxAction.setVisible(False)
        # self.itemRotationSBoxAction.setVisible(False)
        # self.textSizeSBox_tbarAction.setVisible(False)
        if self.cScene.OkAraci.kalem.style() == Qt.PenStyle.NoPen:
            self.act_cizgi_tipi_degistir(Qt.SolidLine)
            self.change_line_style_options(self.cScene.OkAraci.kalem)
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.OkAraci)
        self.actionDrawLineItem.setChecked(True)
        self.cScene.clearSelection()
        self.radioCizgi.setChecked(True)
        self.act_radio_secim_degisti(self.radioCizgi)

    # ---------------------------------------------------------------------
    @Slot()
    def act_add_rect_item(self):
        # self.itemWidthSBoxAction.setVisible(True)
        # self.itemHeightSBoxAction.setVisible(True)
        # self.itemRotationSBoxAction.setVisible(True)
        # self.textSizeSBox_tbarAction.setVisible(False)
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.DortgenAraci)
        self.actionAddRectItem.setChecked(True)
        self.cScene.clearSelection()
        self.radioArkaplan.setChecked(True)
        self.act_radio_secim_degisti(self.radioArkaplan)

    # ---------------------------------------------------------------------
    @Slot()
    def act_add_ellipse_item(self):
        # self.itemWidthSBoxAction.setVisible(True)
        # self.itemHeightSBoxAction.setVisible(True)
        # self.itemRotationSBoxAction.setVisible(True)
        # self.textSizeSBox_tbarAction.setVisible(False)
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.YuvarlakAraci)
        self.actionAddEllipseItem.setChecked(True)
        self.cScene.clearSelection()
        self.radioArkaplan.setChecked(True)
        self.act_radio_secim_degisti(self.radioArkaplan)

    # ---------------------------------------------------------------------
    @Slot()
    def act_draw_path_item(self):
        # self.itemWidthSBoxAction.setVisible(False)
        # self.itemHeightSBoxAction.setVisible(False)
        # self.itemRotationSBoxAction.setVisible(True)
        # self.textSizeSBox_tbarAction.setVisible(False)
        if self.cScene.KalemAraci.kalem.style() == Qt.PenStyle.NoPen:
            self.act_cizgi_tipi_degistir(Qt.SolidLine)
            self.change_line_style_options(self.cScene.KalemAraci.kalem)
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.KalemAraci)
        self.actionDrawPathItem.setChecked(True)
        self.cScene.clearSelection()
        self.radioCizgi.setChecked(True)
        self.act_radio_secim_degisti(self.radioCizgi)

    # ---------------------------------------------------------------------
    @Slot()
    def act_add_text_item(self):
        # self.itemWidthSBoxAction.setVisible(False)
        # self.itemHeightSBoxAction.setVisible(False)
        # self.itemRotationSBoxAction.setVisible(True)
        # self.textSizeSBox_tbarAction.setVisible(True)
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.YaziAraci, itemText="text")
        self.actionAddTextItem.setChecked(True)
        self.cScene.clearSelection()
        self.radioYazi.setChecked(True)
        self.act_radio_secim_degisti(self.radioYazi)

    # # ---------------------------------------------------------------------
    # def toggle_transforms_for_base(self):
    #     self.itemWidthSBoxAction.setVisible(True)
    #     self.itemHeightSBoxAction.setVisible(True)
    #     self.itemRotationSBoxAction.setVisible(True)
    #     self.textSizeSBox_tbarAction.setVisible(False)

    # ---------------------------------------------------------------------
    @Slot(Image)
    def act_crop(self, item):

        if item and item.type() == shared.IMAGE_ITEM_TYPE:  # hotkeyden item none gelirse diye
            self.cScene.aktif_arac_degistir(aktifArac=self.cScene.ResimKirpAraci)
        else:
            self.log(self.tr("No active image item!"), 5000, toStatusBarOnly=True)

    # ---------------------------------------------------------------------
    @Slot()
    def act_add_image_item(self):
        # self.itemWidthSBoxAction.setVisible(True)
        # self.itemHeightSBoxAction.setVisible(True)
        # self.itemRotationSBoxAction.setVisible(True)
        # self.textSizeSBox_tbarAction.setVisible(False)
        fn = QFileDialog.getOpenFileName(self,
                                         self.tr("Open Image File..."),
                                         self.sonKlasorResimler,
                                         self.supportedImageFormats)

        # if fn:
        if fn[0]:
            filePath = fn[0]
            self.cScene.aktif_arac_degistir(aktifArac=self.cScene.ResimAraci, dosyaYolu=filePath)
            self.actionAddImageItem.setChecked(True)

            add = True

            for a in self.recentImagesMenu.actions():  # iki defa eklememek icin
                if filePath == a.toolTip():
                    add = False
                    break
            if add:
                action = QAction(QIcon(filePath), os.path.basename(filePath), self.recentImagesMenu)
                action.setToolTip(filePath)
                action.setStatusTip(filePath)
                action.triggered.connect(lambda: self.cScene.aktif_arac_degistir(aktifArac=self.cScene.ResimAraci, dosyaYolu=filePath))
                action.triggered.connect(lambda: self.actionAddImageItem.setChecked(True))
                count = len(self.recentImagesMenu.actions())
                if count < 9:
                    action.setShortcut(QKeySequence("Alt+Shift+{}".format(count + 1)))
                # action.triggered.connect(self.toggle_transforms_for_base)
                self.recentImagesMenu.addAction(action)
            self.sonKlasorResimler = os.path.dirname(filePath)

    # ---------------------------------------------------------------------
    @Slot()
    def act_add_multiple_images(self, pos=None, imgPaths=None, isEmbeded=False):

        if not pos:  # means called from qaction, if pos exists: means called from drag and drop from self.cScene
            pos = self.get_mouse_scene_pos()

            fn = QFileDialog.getOpenFileNames(self,
                                              self.tr("Open Image Files..."),
                                              self.sonKlasorResimler,
                                              self.supportedImageFormats)

            # if fn:
            if fn[0]:
                imgPaths = fn[0]

                self.sonKlasorResimler = os.path.dirname(imgPaths[0])

            else:
                return

        # for filePath in fn[0]:
        # TODO: bu macro biraz sallantıda begin dedikten sonra loop bi sekilde
        #   bitmez ise, acik kalacak..
        # !!!!!!! try except ekleyebiliriz, except: end macro gibisinden
        self.lutfen_bekleyin_goster()
        self.cScene.undoStack.beginMacro(self.tr("Add {} image(s)").format(len(imgPaths)))
        for filePath in imgPaths:
            self.ekle_resim_direkt(filePath, pos, isEmbeded)
            pos += QPoint(20, 20)

            add = True
            for a in self.recentImagesMenu.actions():  # iki defa eklememek icin
                if filePath == a.toolTip():
                    add = False
                    break  # bu ic loop tamamlanmadigi icin dis loop geri kalan kodu calistirmiyor.

            if add:
                action = QAction(QIcon(filePath), os.path.basename(filePath), self.recentImagesMenu)
                action.setToolTip(filePath)
                action.setStatusTip(filePath)

                # action.triggered.connect(lambda: self.cScene.aktif_arac_degistir(aktifArac=self.cScene.ResimAraci,
                #                                                                  dosyaYolu=filePath))
                # action.triggered.connect(lambda: self.actionAddImageItem.setChecked(True))

                def make_callback(_toolType, _dosyaYolu):
                    return lambda: self.cScene.aktif_arac_degistir(aktifArac=_toolType, dosyaYolu=_dosyaYolu)

                action.triggered.connect(make_callback(self.cScene.ResimAraci, filePath))
                action.triggered.connect(lambda: self.actionAddImageItem.setChecked(True))
                count = len(self.recentImagesMenu.actions())
                if count < 9:
                    action.setShortcut(QKeySequence("Ctrl+{}".format(count + 1)))
                # action.triggered.connect(self.toggle_transforms_for_base)

                self.recentImagesMenu.addAction(action)
        self.cScene.undoStack.endMacro()

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    def ekle_resim_direkt(self, dosyaYolu, pos, isEmbeded=False):

        # yeni TODO: simdi bi de pixmap dosya boyutu icin lazim .. alternatif bi şeyler dusunelim.
        # pixMap = QPixmap(dosyaYolu)
        # pixMap = QPixmap(dosyaYolu).scaled(self.sceneRect().size().toSize() / 1.5, Qt.KeepAspectRatio)
        viewRectSize = self.cScene.views()[0].get_visible_rect().size().toSize()
        pixMap = QPixmap(dosyaYolu).scaled(viewRectSize / 1.5, Qt.KeepAspectRatio)
        rectf = QRectF(pixMap.rect())
        # rectf.moveTo(pos)
        item = Image(dosyaYolu, pos, rectf, 
                     self.cScene.aktifArac.yaziRengi, 
                     self.cScene.aktifArac.arkaPlanRengi,
                     self.cScene.aktifArac.kalem, 
                     self.font(),
                     isEmbeded=isEmbeded)
        self.increase_zvalue(item)
        # self.addItem(item)
        # TODO: macro undo redo
        undoRedo.undoableAddItem(self.cScene.undoStack, description=self.tr("add image"), scene=self.cScene, item=item)
        self.cScene.unite_with_scene_rect(item.sceneBoundingRect())
        pixMap = None

    # ---------------------------------------------------------------------
    @Slot()
    def act_add_video_item(self):
        filtre = self.tr("All Files (*)")
        fn = QFileDialog.getOpenFileName(self,
                                         self.tr("Open Video File..."),
                                         self.sonKlasorVideolar,
                                         filtre
                                         )

        # if fn:
        if fn[0]:
            filePath = fn[0]
            self.cScene.aktif_arac_degistir(aktifArac=self.cScene.VideoAraci, dosyaYolu=filePath)
            self.actionAddVideoItem.setChecked(True)

            self.sonKlasorVideolar = os.path.dirname(filePath)

    # ---------------------------------------------------------------------
    @Slot()
    def act_add_multiple_videos(self, pos=None, videoPaths=None):

        if not pos:  # means called from qaction, if pos exists: means called from drag and drop from self.cScene
            pos = self.get_mouse_scene_pos()
            filtre = self.tr("All Files (*)")
            fn = QFileDialog.getOpenFileNames(self,
                                              self.tr("Open Video Files..."),
                                              self.sonKlasorVideolar,
                                              filtre
                                              )

            # if fn:
            if fn[0]:
                videoPaths = fn[0]

                self.sonKlasorVideolar = os.path.dirname(videoPaths[0])

            else:
                return

        # for filePath in fn[0]:
        # TODO: bu macro biraz sallantıda begin dedikten sonra loop bi sekilde
        #   bitmez ise, acik kalacak..
        # !!!!!!! try except ekleyebiliriz, except: end macro gibisinden
        self.lutfen_bekleyin_goster()
        self.cScene.undoStack.beginMacro(self.tr("Add {} video(s)").format(len(videoPaths)))
        for filePath in videoPaths:
            self.ekle_video_direkt(filePath, pos)
            pos += QPoint(20, 20)
        self.cScene.undoStack.endMacro()

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    def ekle_video_direkt(self, dosyaYolu, pos):

        # viewRectSize = self.views()[0].get_visible_rect().size().toSize()
        # pixMap = QPixmap(dosyaYolu).scaled(viewRectSize / 1.5, Qt.KeepAspectRatio)
        # rectf = QRectF(pixMap.rect())
        # rectf.moveTo(pos)

        item = VideoItem(dosyaYolu, pos, QRectF(0, 0, 320, 240),
                         self.cScene.VideoAraci.yaziRengi,
                         self.cScene.VideoAraci.arkaPlanRengi, #QColor.fromRgbF(0, 0, 0, 0),
                         self.cScene.VideoAraci.kalem,
                         self.cScene.VideoAraci.yaziTipi)
        self.increase_zvalue(item)
        # self.addItem(item)
        # TODO: macro undo redo
        item.player.setParent(self.cView)
        undoRedo.undoableAddItem(self.cScene.undoStack, description=self.tr("add video"), scene=self.cScene, item=item)
        self.cScene.unite_with_scene_rect(item.sceneBoundingRect())
        # pixMap = None

    # ---------------------------------------------------------------------
    def act_ekle_dosya_nesnesi(self):
        filtre = self.tr("All Files (*)")
        fn = QFileDialog.getOpenFileName(self,
                                         self.tr("Open File..."),
                                         self.sonKlasorDosyalar,
                                         filtre
                                         )

        # if fn:
        if fn[0]:
            filePath = fn[0]
            self.cScene.aktif_arac_degistir(aktifArac=self.cScene.DosyaAraci, dosyaYolu=filePath)
            self.actionEkleDosyaNesnesi.setChecked(True)

            self.sonKlasorDosyalar = os.path.dirname(filePath)

    # ---------------------------------------------------------------------
    @Slot()
    def act_ekle_bircok_dosya_nesnesi(self, pos=None, dosyaAdresleri=None, isEmbeded=False):

        if not pos:  # means called from qaction, if pos exists: means called from drag and drop from self.cScene
            pos = self.get_mouse_scene_pos()
            filtre = self.tr("All Files (*)")
            fn = QFileDialog.getOpenFileNames(self,
                                              self.tr("Open Files..."),
                                              self.sonKlasorDosyalar,
                                              filtre
                                              )

            # if fn:
            if fn[0]:
                dosyaAdresleri = fn[0]

                self.sonKlasorDosyalar = os.path.dirname(dosyaAdresleri[0])

            else:
                return

        # for filePath in fn[0]:
        # TODO: bu macro biraz sallantıda begin dedikten sonra loop bi sekilde
        #   bitmez ise, acik kalacak..
        # !!!!!!! try except ekleyebiliriz, except: end macro gibisinden
        self.lutfen_bekleyin_goster()
        self.cScene.undoStack.beginMacro(self.tr("Add {} file(s)").format(len(dosyaAdresleri)))
        for dosyaAdresi in dosyaAdresleri:
            self.ekle_dosya_direkt(dosyaAdresi, pos)
            pos += QPoint(20, 20)
        self.cScene.undoStack.endMacro()

        self.lutfen_bekleyin_gizle()

        # print(dosyaAdresleri)

    # ---------------------------------------------------------------------
    def ekle_dosya_direkt(self, dosyaAdresi, pos):

        # viewRectSize = self.views()[0].get_visible_rect().size().toSize()
        # pixMap = QPixmap(dosyaYolu).scaled(viewRectSize / 1.5, Qt.KeepAspectRatio)
        # rectf = QRectF(pixMap.rect())
        # rectf.moveTo(pos)

        # web = QWebEngineView(self)
        # web.setAttribute(Qt.WA_DontShowOnScreen)
        # web.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        # web.settings().setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        # web.load(QUrl.fromLocalFile(dosyaAdresi))
        # # web.show()
        #
        # image = QImage(200,300,QImage.Format_ARGB32)
        # left = 0
        # top = 0
        # width = 768
        # height= 1024
        # rg = QRegion(left,top,width,height)
        # painter = QPainter(image)
        # web.page().view().render(painter, QPoint(), rg)
        # # self.render(painter, QPoint(), rg)
        # painter.end()
        # pixmap = QPixmap().fromImage(image)
        #
        # # pixmap=QPixmap(200,300)
        # # web.page().view().render(pixmap)
        # # self.render(pixmap)
        #
        # """
        #
        # QByteArray ba;
        # QBuffer bu(&ba);
        # bu.open(QBuffer::ReadWrite);
        # image->save(&bu, "JPG",80);
        # item->setVisible(true);
        # QString imgBase64 = ba.toBase64();
        # bu.close();
        # """
        nesne = DosyaNesnesi(dosyaAdresi, pos, QRectF(0, 0, 125, 160), 
                             self.cScene.aktifArac.yaziRengi, 
                             self.cScene.aktifArac.arkaPlanRengi,
                             self.cScene.aktifArac.kalem,
                             self.font(),
                             pixmap=None)
        self.increase_zvalue(nesne)
        # self.addItem(item)
        # TODO: macro undo redo
        undoRedo.undoableAddItem(self.cScene.undoStack, description=self.tr("add file"), scene=self.cScene, item=nesne)
        self.cScene.unite_with_scene_rect(nesne.sceneBoundingRect())
        # pixMap = None

    # ---------------------------------------------------------------------
    @Slot()
    def act_delete_item(self):
        # The ownership of item is passed on to the caller
        # (i.e., PySide.QtGui.QGraphicsScene will no longer delete item when destroyed).
        tempItems = self.cScene.selectedItems()
        if tempItems:
            self.lutfen_bekleyin_goster()
            self.cScene.undoStack.beginMacro(self.tr("Delete"))
            # items = [x for x in tempItems if not x.parentItem() in tempItems]  #slower
            # items = []
            # for i in tempItems:
            #     # self.cScene.selectionQueue.remove(i)
            #     if i.parentItem() in tempItems:
            #         continue
            #     items.append(i)
            for item in tempItems:

                # parent item listede once gelip silinse bile, hala tempItem listesinde olacagi icin
                # burdan yeni bir undo komutu olusturulmayacak. o yuzden yukarda ayıklamaya yapmaya gerek yok
                # bu for dongusunden once.
                # ayrica bunu UndoableRemoveItem classinda halletmek daha dogru ama
                # tekrardan recursive loop etmek gerekecek.
                if item.parentItem() in tempItems:
                    continue
                # if not item.parentItem():
                #     self.cScene.unGroupedRootItems.discard(item)
                addToUnGroupedRootItems = False
                if item in self.cScene.unGroupedRootItems:
                    addToUnGroupedRootItems = True
                undoRedo.undoableRemoveItem(self.cScene.undoStack, self.tr("_remove"), self.cScene, item,
                                            addToUnGroupedRootItems)

            self.cScene.undoStack.endMacro()
            if not self.cScene.items():
                self.cScene.setSceneRect(self.cView.get_visible_rect())
            self.lutfen_bekleyin_gizle()

            self.tw_sayfa_guncelle()

        self.sahneKutuphane.kullanilmayanlari_isaretle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_select_all(self):
        self.lutfen_bekleyin_goster()
        # for item in self.cScene.items():
        #     # if not item.isSelected():
        #     item.setSelected(True)

        # bu daha hizli
        path = QPainterPath()
        path.addRect(self.cScene.itemsBoundingRect())
        self.cScene.setSelectionArea(path)
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_cut(self):
        pass

    # def clearClipboard():
    #     # There is a small race condition here where we could clear
    #     # somebody else's contents but there's nothing we can do about it.
    #     if not clipboard.ownsClipboard() or clipboard.text != text:
    #         return
    #     clipboard.clear()

    # ---------------------------------------------------------------------
    def selected_to_dict_for_copy(self, item):

        # for item in self.cScene.items():
        # if not item.parentItem():
        itemPropDict = item.get_properties_for_save_binary()
        if item.childItems():
            if item.type() == shared.GROUP_ITEM_TYPE:
                itemPropDict["children"] = self.scene_to_dict_binary_recursive(item.parentedWithParentOperation)
                itemPropDict["group_children"] = self.scene_to_dict_binary_recursive(item.allFirstLevelGroupChildren)
            else:
                itemPropDict["children"] = self.scene_to_dict_binary_recursive(item.childItems())
            # itemPropDict["children"] = self.scene_to_dict_binary_recursive(item)

        return itemPropDict

    # ---------------------------------------------------------------------
    @Slot()
    def act_copy(self, isMirroring=False):
        self.lutfen_bekleyin_goster()
        eskiMimeData = self.clipboard.mimeData()
        eskiClipboardText = eskiMimeData.text()
        eskiClipboardHtml = eskiMimeData.html()
        eskiClipboardUrls = eskiMimeData.urls()
        eskiClipboardColor = eskiMimeData.colorData()
        eskiClipboardImageData = eskiMimeData.imageData()
        # clipboard.setText(yeniText)

        if isMirroring:
            self.beforeMirrorCopyMimeData = QMimeData()
            if eskiMimeData.data('scene/items'):
                self.beforeMirrorCopyMimeData.setData('scene/items', eskiMimeData.data('scene/items'))
            if eskiClipboardText:
                self.beforeMirrorCopyMimeData.setText(eskiClipboardText)
            if eskiClipboardHtml:
                self.beforeMirrorCopyMimeData.setHtml(eskiClipboardHtml)
            if eskiClipboardUrls:
                self.beforeMirrorCopyMimeData.setUrls(eskiClipboardUrls)
            if eskiClipboardColor:
                self.beforeMirrorCopyMimeData.setColorData(eskiClipboardColor)
            if eskiClipboardImageData:
                self.beforeMirrorCopyMimeData.setImageData(eskiClipboardImageData)

        # "If Qt expects a QByteArray then PySide6 will also accept a bytes"
        # http://pyqt.sourceforge.net/Docs/PySide6/gotchas.html
        # mimeData.setData('sceneCopiedFrom/TempFolder', self.cScene.tempDirPath.encode())
        mimeData = QMimeData()
        # mimeData.setData('sceneCopiedFrom/tempFolder', b"asdasdasd")
        mimeData.setData('sceneCopiedFrom/tempFolder', self.cScene.tempDirPath.encode())

        # itemData = QByteArray()
        # dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        # pixmap = QPixmap()
        # point = QPoint()
        # dataStream << pixmap << point

        # >>> buf = QByteArray(b)
        # >>> c = QTextStream(buf).readAll()
        # >>> c
        # PyQt4.QtCore.QString('hello')

        itemData = QByteArray()
        stream = QDataStream(itemData, QIODevice.WriteOnly)
        # selectedItems = self.cScene.selectedItems()

        for item in self.cScene.selectionQueue:
            # rect = rect.unite(item.boundingRect())
            # stream << item

            # if not item.parentItem():
            #     stream.writeQVariant(self.selected_to_dict_for_copy(item))
            parentItem = item.parentItem()
            if parentItem:
                if parentItem in self.cScene.selectionQueue:
                    continue
                else:
                    itemDict = self.selected_to_dict_for_copy(item)
                    itemDict["pos"] = item.scenePos()
                    # to get actual sceneRotation
                    yeniRot = 0
                    # yeniScale = 1
                    while parentItem:
                        yeniRot += parentItem.rotation()
                        # yeniScale /= parentItem.scale()
                        parentItem = parentItem.parentItem()
                    itemDict["rotation"] += yeniRot
                    # itemDict["scale"] *= yeniScale
                    stream.writeQVariant(itemDict)
            else:
                # hiyerarsi self.selected_to_dict_for_copy de kuruluyor.
                stream.writeQVariant(self.selected_to_dict_for_copy(item))

            # group.addToGroup(item)
            # stream.writeQVariant(item.get_properties_for_save_binary())
        # stream.device().reset()

        # stream.writeQVariant(rect)
        mimeData.setData('scene/items', itemData)

        # itemList = []
        # for item in self.cScene.selectedItems():
        #     itemList.append(item.get_properties_for_save_binary())
        # mimeData.setData("itemList", itemData)

        if eskiClipboardText:
            mimeData.setText(eskiClipboardText)
        if eskiClipboardHtml:
            mimeData.setHtml(eskiClipboardHtml)
        if eskiClipboardUrls:
            mimeData.setUrls(eskiClipboardUrls)
        if eskiClipboardColor:
            mimeData.setColorData(eskiClipboardColor)
        if eskiClipboardImageData:
            mimeData.setImageData(eskiClipboardImageData)
        self.clipboard.setMimeData(mimeData)
        # self.actionPaste.setEnabled(True)
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_paste_as_plain_text(self):
        mimeData = self.clipboard.mimeData()
        if not mimeData.hasText() or not mimeData.hasHtml():
            return
        self.lutfen_bekleyin_goster()
        textItem = Text(self.get_mouse_scene_pos(), 
                        self.cScene.YaziAraci.yaziRengi, 
                        self.cScene.YaziAraci.arkaPlanRengi, 
                        self.cScene.YaziAraci.kalem, 
                        self.cScene.YaziAraci.yaziTipi)
        textItem.set_document_url(self.cScene.tempDirPath)

        if mimeData.hasText():
            textItem.setPlainText(mimeData.text())
            textItem.textItemFocusedOut.connect(lambda: self.cScene.is_text_item_empty(textItem))
            self.increase_zvalue(textItem)
            undoRedo.undoableAddItem(self.cScene.undoStack, self.tr("_paste"), self.cScene, textItem)
            textItem.setTextInteractionFlags(Qt.NoTextInteraction)
            cursor = textItem.textCursor()
            cursor.clearSelection()
            textItem.setTextCursor(cursor)
            # return
        elif mimeData.hasHtml():
            textItem.setHtml(mimeData.html())
            text = textItem.toPlainText()
            textItem.document().clear()
            textItem.setPlainText(text)
            textItem.isPlainText = True
            textItem.textItemFocusedOut.connect(lambda: self.cScene.is_text_item_empty(textItem))
            self.increase_zvalue(textItem)
            undoRedo.undoableAddItem(self.cScene.undoStack, self.tr("_paste"), self.cScene, textItem)
            textItem.setTextInteractionFlags(Qt.NoTextInteraction)
            cursor = textItem.textCursor()
            cursor.clearSelection()
            textItem.setTextCursor(cursor)
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_paste(self):
        self.lutfen_bekleyin_goster()
        mimeData = self.clipboard.mimeData()
        # eskiTempDir = None
        # if mimeData.hasFormat('sceneCopiedFrom/tempFolder'):
        # print(mimeData.data('sceneCopiedFrom/tempFolder').data().decode('utf-8'))
        eskiTempDir = mimeData.data('sceneCopiedFrom/tempFolder').data().decode('utf-8')
        # eskiTempDir=mimeData.data('sceneCopiedFrom/tempFolder').data().decode('utf-8')

        # if mimeData.hasFormat('application/x-dnditemdata'):
        #     itemData = mimeData.data('application/x-dnditemdata')
        #     dataStream = QDataStream(itemData, QIODevice.ReadOnly)
        #
        #     pixmap = QPixmap()
        #     offset = QPoint()
        #     dataStream >> pixmap >> offset

        # if not mimeData.hasFormat('scene/items'):
        #     return

        itemData = mimeData.data('scene/items')

        # to prevent empty paste(actually is does not paste, but because of undoStack macro below,
        # it creates an undo.)
        if not itemData:
            # return
            # cUrls = mimeData.urls()
            # print(cUrls)

            # print(mimeData.formats())
            #
            # for f in mimeData.formats():
            #     print(f, mimeData.data(f))

            # if mimeData.imageData():
            if mimeData.hasImage():
                # it may also have text/html, if it copied from web browser.

                # pixMap = QPixmap(item["filePath"]).scaled(rect.size().toSize(), Qt.KeepAspectRatio)
                # filePath = "/home/n00/CODE/pyCharm/Defter/imaaaj.jpg"

                #  burda QImage icine almak lazimi, yoksa image none olabiliyor, if mimeData.imageData()
                #  veya  if mimeData.hasImage() dogru dondursede QImage icine almazsak none oluyor image.
                image = QImage(mimeData.imageData())
                # print(mimeData.imageData())
                # print(image.byteCount())
                imageSavePath = self.cScene.get_unique_path_for_embeded_image("pasted_image.jpg")
                image.save(imageSavePath)
                pixMap = QPixmap(imageSavePath)
                # pixMap = QPixmap(image)
                rect = QRectF(pixMap.rect())
                imageItem = Image(imageSavePath, self.get_mouse_scene_pos(), rect, 
                                  self.cScene.ResimAraci.yaziRengi, 
                                  self.cScene.ResimAraci.arkaPlanRengi,
                                  self.cScene.ResimAraci.kalem,
                                  self.cScene.ResimAraci.yaziTipi)

                imageItem.isEmbeded = True

                self.increase_zvalue(imageItem)
                undoRedo.undoableAddItem(self.cScene.undoStack, self.tr("_paste"), self.cScene, imageItem)
                imageItem.reload_image_after_scale()
                self.cScene.unite_with_scene_rect(imageItem.sceneBoundingRect())

                # pixMap = None
                # return imageItem

            elif mimeData.hasHtml():
                textItem = Text(self.get_mouse_scene_pos(), 
                                self.cScene.YaziAraci.yaziRengi, 
                                self.cScene.YaziAraci.arkaPlanRengi, 
                                self.cScene.YaziAraci.kalem,
                                self.cScene.YaziAraci.yaziTipi)
                textItem.set_document_url(self.cScene.tempDirPath)
                textItem.setHtml(mimeData.html())
                textItem.isPlainText = False
                textItem.textItemFocusedOut.connect(lambda: self.cScene.is_text_item_empty(textItem))
                self.increase_zvalue(textItem)
                undoRedo.undoableAddItem(self.cScene.undoStack, self.tr("_paste"), self.cScene, textItem)
                textItem.setTextInteractionFlags(Qt.NoTextInteraction)
                cursor = textItem.textCursor()
                cursor.clearSelection()
                textItem.setTextCursor(cursor)
                self.cScene.unite_with_scene_rect(textItem.sceneBoundingRect())

                # return
            elif mimeData.hasText():

                textItem = Text(self.get_mouse_scene_pos(), 
                                self.cScene.YaziAraci.yaziRengi, 
                                self.cScene.YaziAraci.arkaPlanRengi, 
                                self.cScene.YaziAraci.kalem,
                                self.cScene.YaziAraci.yaziTipi,
                                text=mimeData.text())
                textItem.set_document_url(self.cScene.tempDirPath)
                textItem.textItemFocusedOut.connect(lambda: self.cScene.is_text_item_empty(textItem))
                self.increase_zvalue(textItem)
                undoRedo.undoableAddItem(self.cScene.undoStack, self.tr("_paste"), self.cScene, textItem)
                textItem.setTextInteractionFlags(Qt.NoTextInteraction)
                cursor = textItem.textCursor()
                cursor.clearSelection()
                textItem.setTextCursor(cursor)
                self.cScene.unite_with_scene_rect(textItem.sceneBoundingRect())
                # return

            else:
                self.lutfen_bekleyin_gizle()
                return

        stream = QDataStream(itemData, QIODevice.ReadOnly)

        self.cScene.clearSelection()

        paste_group = Group()
        paste_group.setFlags(paste_group.ItemIsSelectable
                             | paste_group.ItemIsMovable
                             # | group.ItemIsFocusable
                             )
        self.cScene.addItem(paste_group)
        # TODO: try icine mi alsak, cursor olurda bir hata olursa WaitCursor halde kalmasin.
        self.cScene.undoStack.beginMacro(self.tr("paste"))
        while not stream.atEnd():
            itemDict = stream.readQVariant()
            # item = stream.readQVariant()
            # print(item)

            if itemDict["type"] == shared.GROUP_ITEM_TYPE:
                group = self.add_item_to_scene_from_dict(itemDict, isPaste=True)
                # parentItem() == None her zaman.
                # self.increase_zvalue(group)
                self.dict_to_scene_recursive_group(itemDict["group_children"], group)
                # group.setScale(itemDict["scale"])
                if "children" in itemDict:
                    self.dict_to_scene_recursive_parent(itemDict["children"], group)

                group.updateBoundingRect()
                group.setScale(itemDict["scale"])
                group.setParentItem(paste_group)
                paste_group.allFirstLevelGroupChildren.append(group)

            else:
                # ------------------------------------------------------------------------------------
                # ## START ##  Copying related textItem's html images                      ## START ##
                # ## START ##  from one doc's temp folder to newly pasted's temp folder    ## START ##
                # ## START ##   before object creation                                     ## START ##
                # ------------------------------------------------------------------------------------
                # for ex, if you paste from one document to another, images don't show if we dont update this.

                if itemDict["type"] == Text.Type and not itemDict["isPlainText"] and eskiTempDir:
                    imgSrcParser = ImgSrcParser()
                    imgSrcParser.feed(itemDict["html"])
                    for srcURL in imgSrcParser.urls:
                        if srcURL.startswith("defter"):

                            yeniImgFolderPath = os.path.join(self.cScene.tempDirPath, "images")

                            # try:
                            if not os.path.exists(yeniImgFolderPath):
                                os.makedirs(yeniImgFolderPath)

                            imgPath = os.path.join(eskiTempDir, "images", srcURL)
                            yeniImgPath = os.path.join(yeniImgFolderPath, srcURL)

                            # print(imgPath)
                            # print(yeniImgPath)
                            # If shallow is true, files with identical os.stat() signatures are taken to be equal.
                            # Otherwise, the contents of the files are compared.
                            if os.path.exists(yeniImgPath):
                                if not filecmp.cmp(imgPath, yeniImgPath, shallow=True):
                                    # print("ayni isimde dosya var, icerik farkli")
                                    try:
                                        shutil.copy2(imgPath, yeniImgPath)
                                        # print(imgPath)
                                        # print(yeniImgPath)
                                    except Exception as e:
                                        self.log(str(e), level=3)
                                # else:
                                #     print("ayni isimde ve ayni icerikte dosya var")
                            else:
                                # print("ayni isimde dosya yok")
                                # farkli isimdeki halizirdaki diger dosyalar ile bu kopyalanan
                                # yeni dosya ayni icerige sahip mi diye kontrol etmek de
                                # false pozitif bir optimizasyon olur, anlamsiz yuk bindirir
                                try:
                                    shutil.copy2(imgPath, yeniImgPath)
                                except Exception as e:
                                    self.log(str(e), level=3)
                # ------------------------------------------------------------------------------------
                # ##  END  ##  Copying related textItem's html images                      ##  END  ##
                # ##  END  ##  from one doc's temp folder to newly pasted's temp folder    ##  END  ##
                # ##  END  ##   before object creation                                     ##  END  ##
                # ------------------------------------------------------------------------------------
                # --------------------------------------------------------------------------------------
                # ##  BASLA  ##  gomlu resim ,video,dosya nesnlerini bir belgeden digerine ##  BASLA  ##
                # ##  BASLA  ## kopyalamadan once ilgili dosyalari kopyaliyoruz            ##  BASLA  ##
                # --------------------------------------------------------------------------------------

                kopyalamak_lazim_mi = False
                if itemDict["type"] == Image.Type and itemDict["isEmbeded"] and eskiTempDir:
                    cesit_klasor_adi = "images"
                    cakismayan_isim_al_fonksiyonu = self.cScene.get_unique_path_for_embeded_image
                    kopyalamak_lazim_mi = True

                if itemDict["type"] == VideoItem.Type and itemDict["isEmbeded"] and eskiTempDir:
                    cesit_klasor_adi = "videos"
                    cakismayan_isim_al_fonksiyonu = self.cScene.get_unique_path_for_embeded_video
                    kopyalamak_lazim_mi = True

                if itemDict["type"] == DosyaNesnesi.Type and itemDict["isEmbeded"] and eskiTempDir:
                    cesit_klasor_adi = "files"
                    cakismayan_isim_al_fonksiyonu = self.cScene.get_unique_path_for_embeded_file
                    kopyalamak_lazim_mi = True

                if kopyalamak_lazim_mi:
                    yeniKlasorAdresi = os.path.join(self.cScene.tempDirPath, cesit_klasor_adi)
                    # try:
                    if not os.path.exists(yeniKlasorAdresi):
                        os.makedirs(yeniKlasorAdresi)

                    dosya_adi = os.path.basename(itemDict["filePath"])

                    eskiDosyaAdresi = os.path.join(eskiTempDir, cesit_klasor_adi, dosya_adi)
                    yeniDosyaAdresi = os.path.join(yeniKlasorAdresi, dosya_adi)

                    # If shallow is true, files with identical os.stat() signatures are taken to be equal.
                    # Otherwise, the contents of the files are compared.
                    if os.path.exists(yeniDosyaAdresi):
                        if not filecmp.cmp(eskiDosyaAdresi, yeniDosyaAdresi, shallow=True):
                            # print("ayni isimde dosya var, ama icerik farkli")
                            try:
                                yeniDosyaAdresi = cakismayan_isim_al_fonksiyonu(dosya_adi)
                                shutil.copy2(eskiDosyaAdresi, yeniDosyaAdresi)
                                # nesnenin resim dosya adresi degisti
                                itemDict["filePath"] = yeniDosyaAdresi
                                # print(eskiDosyaAdresi)
                                # print(yeniDosyaAdresi)
                            except Exception as e:
                                self.log(str(e), level=3)
                        # else:
                        #     # dolayisi ile bir sey yapmaya gerek yok, o dosya kullanilacak
                        #     print("ayni isimde ve ayni icerikte dosya var")
                    else:
                        # print("ayni isimde dosya yok")
                        # farkli isimdeki halizirdaki diger dosyalar ile bu kopyalanan
                        # yeni dosya ayni icerige sahip mi diye kontrol etmemek tercih edildi.
                        try:
                            shutil.copy2(eskiDosyaAdresi, yeniDosyaAdresi)
                        except Exception as e:
                            self.log(str(e), level=3)

                # --------------------------------------------------------------------------------------
                # ##  SON  ##  gomlu resim ,video,dosya nesnlerini bir belgeden digerine ##  SON  ##
                # ##  SON  ## kopyalamadan once ilgili dosyalari kopyaliyoruz            ##  SON  ##
                # --------------------------------------------------------------------------------------

                item = self.add_item_to_scene_from_dict(itemDict, isPaste=True)
                # parentItem() == None her zaman.
                # self.increase_zvalue(item)
                if "children" in itemDict:
                    self.dict_to_scene_recursive_parent(itemDict["children"], item)
                item.setParentItem(paste_group)
                paste_group.allFirstLevelGroupChildren.append(item)

        if len(paste_group.allFirstLevelGroupChildren) == 1:
            self.increase_zvalue(paste_group.allFirstLevelGroupChildren[0])

        paste_group.updateBoundingRect()  # gerek yok normalde de zaten, ekrana cizdirilmedigi icin paste_group.
        paste_group.moveCenterToPosition(self.get_mouse_scene_pos())
        self.cScene.unite_with_scene_rect(paste_group.sceneBoundingRect())
        # undoRedo.undoablePaste(self.cScene.undoStack, "paste", paste_group.allFirstLevelGroupChildren)
        paste_group.destroyGroupForPaste()
        self.cScene.undoStack.endMacro()
        self.cScene.removeItem(paste_group)
        del paste_group
        self.lutfen_bekleyin_gizle()

        # if mimeData.hasImage():
        #     setPixmap(mimeData.imageData())
        # elif mimeData.hasHtml():
        #     setText(mimeData.html())
        #     setTextFormat(Qt.RichText)
        # elif (mimeData.hasText():
        #     setText(mimeData.text())
        #     setTextFormat(Qt.PlainText)
        # else:
        #     setText(tr("Cannot display data"))

        # print(self.cScene.items())

    # ---------------------------------------------------------------------
    @Slot()
    def act_pre_mirror_y(self):
        if hasattr(self.cScene.activeItem, "tempTextItem"):
            if self.cScene.activeItem.tempTextItem:  # 2. kontrolu yapiyoruz cunku ilk olusturulurken none veriyoruz.
                self.cScene.activeItem.tempTextItem.clearFocus()
        if not self.cScene.selectionQueue:
            self.log(self.tr("Please select at least 1 item! "
                             "And click anywhere in the scene to set the mirror axis."), 5000, toStatusBarOnly=True)
            return
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.AynalaYAraci, pos=self.get_mouse_scene_pos())

    # ---------------------------------------------------------------------
    @Slot()
    def act_pre_mirror_x(self):
        if hasattr(self.cScene.activeItem, "tempTextItem"):
            if self.cScene.activeItem.tempTextItem:  # 2. kontrolu yapiyoruz cunku ilk olusturulurken none veriyoruz.
                self.cScene.activeItem.tempTextItem.clearFocus()
        if not self.cScene.selectionQueue:
            self.log(self.tr("Please select at least 1 item! "
                             "And click anywhere in the scene to set the mirror axis."), 5000, toStatusBarOnly=True)
            return
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.AynalaXAraci, pos=self.get_mouse_scene_pos())

    # ---------------------------------------------------------------------
    @Slot()
    def act_mirror_x(self, mPos):
        # bu sahneden cagriliyor
        self.lutfen_bekleyin_goster()
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.SecimAraci)  # bu finish_interactive_toolsu da cagiriyor.

        mposx = mPos.x()

        self.act_copy(isMirroring=True)
        mimeData = self.clipboard.mimeData()

        itemData = mimeData.data('scene/items')
        stream = QDataStream(itemData, QIODevice.ReadOnly)

        self.cScene.clearSelection()

        # TODO: try icine mi alsak, cursor olurda bir hata olursa WaitCursor halde kalmasin.
        self.cScene.undoStack.beginMacro(self.tr("mirror x"))
        mirroredItemsBoundingRect = QRectF()  # sceneRect adaptation
        while not stream.atEnd():
            itemDict = stream.readQVariant()
            # item = stream.readQVariant()
            # print(item)

            if itemDict["type"] == shared.GROUP_ITEM_TYPE:
                item = self.add_item_to_scene_from_dict(itemDict, isPaste=True)
                # self.increase_zvalue(item)
                self.dict_to_scene_recursive_group(itemDict["group_children"], item)
                if "children" in itemDict:
                    self.dict_to_scene_recursive_parent(itemDict["children"], item)
                item.setScale(itemDict["scale"])
                item.updateBoundingRect()
                # irect = item.boundingRect()

            else:
                item = self.add_item_to_scene_from_dict(itemDict, isPaste=True)
                # self.increase_zvalue(item)
                if "children" in itemDict:
                    self.dict_to_scene_recursive_parent(itemDict["children"], item)

            item.flipHorizontal(mposx)

            # v - sceneRect adaptation - v
            mirroredItemsBoundingRect = mirroredItemsBoundingRect.united(item.sceneBoundingRectWithChildren())
        self.cScene.unite_with_scene_rect(mirroredItemsBoundingRect)

        self.cScene.undoStack.endMacro()
        # restore old copy mimedata
        self.clipboard.setMimeData(self.beforeMirrorCopyMimeData)
        self.beforeMirrorCopyMimeData = None
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_mirror_y(self, mPos):
        # bu sahneden cagriliyor
        self.lutfen_bekleyin_goster()
        self.cScene.aktif_arac_degistir(aktifArac=self.cScene.SecimAraci)  # bu finish_interactive_toolsu da cagiriyor.

        mposy = mPos.y()

        self.act_copy(isMirroring=True)
        mimeData = self.clipboard.mimeData()

        itemData = mimeData.data('scene/items')
        stream = QDataStream(itemData, QIODevice.ReadOnly)

        self.cScene.clearSelection()

        # TODO: try icine mi alsak, cursor olurda bir hata olursa WaitCursor halde kalmasin.
        self.cScene.undoStack.beginMacro(self.tr("mirror y"))
        mirroredItemsBoundingRect = QRectF()  # sceneRect adaptation
        while not stream.atEnd():
            itemDict = stream.readQVariant()
            # item = stream.readQVariant()
            # print(item)

            if itemDict["type"] == shared.GROUP_ITEM_TYPE:
                item = self.add_item_to_scene_from_dict(itemDict, isPaste=True)
                # self.increase_zvalue(item)
                self.dict_to_scene_recursive_group(itemDict["group_children"], item)
                if "children" in itemDict:
                    self.dict_to_scene_recursive_parent(itemDict["children"], item)
                item.setScale(itemDict["scale"])
                item.updateBoundingRect()
                # irect = item.boundingRect()

            else:
                item = self.add_item_to_scene_from_dict(itemDict, isPaste=True)
                # self.increase_zvalue(item)
                if "children" in itemDict:
                    self.dict_to_scene_recursive_parent(itemDict["children"], item)

            item.flipVertical(mposy)
            # v - sceneRect adaptation - v
            mirroredItemsBoundingRect = mirroredItemsBoundingRect.united(item.sceneBoundingRectWithChildren())
        self.cScene.unite_with_scene_rect(mirroredItemsBoundingRect)

        self.cScene.undoStack.endMacro()
        # restore old copy mimedata
        self.clipboard.setMimeData(self.beforeMirrorCopyMimeData)
        self.beforeMirrorCopyMimeData = None
        self.lutfen_bekleyin_gizle()

    @Slot()
    # ---------------------------------------------------------------------
    def act_align_left(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()
        if not len(items) > 1:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 1:
                self.log(self.tr("Please select at least 2 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 2 items!"), 5000, toStatusBarOnly=True)
            return

        yeniLeft = self.cScene.activeItem.sceneLeft()
        self.cScene.undoStack.beginMacro(self.tr("align left edges"))
        for item in items:
            eskiPos = item.scenePos()
            item.setSceneLeft(yeniLeft)
            self.cScene.when_item_moved(item, eskiPos)
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    @Slot()
    # ---------------------------------------------------------------------
    def act_align_right(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 1:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 1:
                self.log(self.tr("Please select at least 2 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 2 items!"), 5000, toStatusBarOnly=True)
            return

        yeniRight = self.cScene.activeItem.sceneRight()
        self.cScene.undoStack.beginMacro(self.tr("align right edges"))
        for item in items:
            eskiPos = item.scenePos()
            item.setSceneRight(yeniRight)
            self.cScene.when_item_moved(item, eskiPos)
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    @Slot()
    # ---------------------------------------------------------------------
    def act_align_top(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 1:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 1:
                self.log(self.tr("Please select at least 2 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 2 items!"), 5000, toStatusBarOnly=True)
            return

        yeniTop = self.cScene.activeItem.sceneTop()
        self.cScene.undoStack.beginMacro(self.tr("align top edges"))
        for item in items:
            eskiPos = item.scenePos()
            item.setSceneTop(yeniTop)
            self.cScene.when_item_moved(item, eskiPos)
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    @Slot()
    # ---------------------------------------------------------------------
    def act_align_bottom(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 1:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 1:
                self.log(self.tr("Please select at least 2 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 2 items!"), 5000, toStatusBarOnly=True)
            return

        yeniBottom = self.cScene.activeItem.sceneBottom()
        self.cScene.undoStack.beginMacro(self.tr("align bottom edges"))
        for item in items:
            eskiPos = item.scenePos()
            item.setSceneBottom(yeniBottom)
            self.cScene.when_item_moved(item, eskiPos)
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    @Slot()
    # ---------------------------------------------------------------------
    def act_align_horizontal_center(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 1:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 1:
                self.log(self.tr("Please select at least 2 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 2 items!"), 5000, toStatusBarOnly=True)
            return

        hcenter = self.cScene.activeItem.sceneCenter().y()
        self.cScene.undoStack.beginMacro(self.tr("align centers horizontally"))
        for item in items:
            eskiPos = item.scenePos()
            item.setHorizontalCenter(hcenter)
            self.cScene.when_item_moved(item, eskiPos)
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    @Slot()
    # ---------------------------------------------------------------------
    def act_align_vertical_center(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 1:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 1:
                self.log(self.tr("Please select at least 2 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 2 items!"), 5000, toStatusBarOnly=True)
            return

        vcenter = self.cScene.activeItem.sceneCenter().x()
        self.cScene.undoStack.beginMacro(self.tr("align centers vertically"))
        for item in items:
            eskiPos = item.pos()
            item.setVerticalCenter(vcenter)
            self.cScene.when_item_moved(item, eskiPos)
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    @Slot()
    # ---------------------------------------------------------------------
    def act_equalize_horizontal_gaps(self):

        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 2:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 2:
                self.log(self.tr("Please select at least 3 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 3 items!"), 5000, toStatusBarOnly=True)
            return

        # t1 = time.time()
        # def getKey(item):
        #     return item.sceneLeft()
        # items.sort(key=getKey)

        # items.sort(key=lambda x: x.sceneLeft())
        items.sort(key=operator.methodcaller('sceneLeft'))
        # t2 = time.time()
        # print(t2-t1)

        left = items[0].sceneLeft()
        right = items[-1].sceneRight()

        # sumOfWidths = sum([item.rect().width() for item in items])
        sumOfWidths = 0
        for item in items:
            sumOfWidths += item.sceneWidth()

        sumOfGaps = right - left - sumOfWidths
        equalizedGap = sumOfGaps / (len(items) - 1)

        self.cScene.undoStack.beginMacro(self.tr("equalize horizontal gaps"))
        prevItemRightX = items[0].sceneRight()
        for item in (items[1:-1]):
            eskiPos = item.pos()
            item.setSceneLeft(prevItemRightX + equalizedGap)
            prevItemRightX = item.sceneRight()
            self.cScene.when_item_moved(item, eskiPos)
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    @Slot()
    # ---------------------------------------------------------------------
    def act_equalize_vertical_gaps(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 2:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 2:
                self.log(self.tr("Please select at least 3 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 3 items!"), 5000, toStatusBarOnly=True)
            return

        items.sort(key=operator.methodcaller('sceneTop'))
        top = items[0].sceneTop()
        bottom = items[-1].sceneBottom()

        sumOfHeights = 0
        for item in items:
            sumOfHeights += item.sceneHeight()

        sumOfGaps = bottom - top - sumOfHeights
        equalizedGap = sumOfGaps / (len(items) - 1)

        self.cScene.undoStack.beginMacro(self.tr("equalize vertical gaps"))
        prevItemBottomY = items[0].sceneBottom()
        for item in (items[1:-1]):
            eskiPos = item.pos()
            item.setSceneTop(prevItemBottomY + equalizedGap)
            prevItemBottomY = item.sceneBottom()
            self.cScene.when_item_moved(item, eskiPos)
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    def act_distribute_items_vertically(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 1:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 1:
                self.log(self.tr("Please select at least 2 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 2 items!"), 5000, toStatusBarOnly=True)
            return

        items.sort(key=operator.methodcaller('sceneTop'))

        self.cScene.undoStack.beginMacro(self.tr("distribute vertically"))
        prevItemBottomY = items[0].sceneBottom()
        for item in items[1:]:
            eskiPos = item.pos()
            item.setSceneTop(prevItemBottomY + 5)
            prevItemBottomY = item.sceneBottom()
            self.cScene.when_item_moved(item, eskiPos)
            self.cScene.unite_with_scene_rect(item.sceneBoundingRect())
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    def act_distribute_items_horizontally(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.get_selected_top_level_items()

        if not len(items) > 1:
            self.lutfen_bekleyin_gizle()
            if len(self.cScene.selectionQueue) > 1:
                self.log(self.tr("Please select at least 2 (non-parented) items!"), 5000, toStatusBarOnly=True)
            else:
                self.log(self.tr("Please select at least 2 items!"), 5000, toStatusBarOnly=True)
            return

        items.sort(key=operator.methodcaller('sceneLeft'))

        self.cScene.undoStack.beginMacro(self.tr("distribute horizontally"))
        prevItemRightX = items[0].sceneRight()
        for item in items[1:]:
            eskiPos = item.pos()
            item.setSceneLeft(prevItemRightX + 5)
            prevItemRightX = item.sceneRight()
            self.cScene.when_item_moved(item, eskiPos)
            self.cScene.unite_with_scene_rect(item.sceneBoundingRect())
        self.cScene.undoStack.endMacro()
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    def get_all_childitems_in_hierarchy(self, tempList, i):
        for c in i.childItems():
            if c.childItems():
                self.get_all_childitems_in_hierarchy(tempList, c)
            tempList.append(c)
        return tempList

    # ---------------------------------------------------------------------
    @Slot()
    def act_parent_items(self):
        self.lutfen_bekleyin_goster()
        items = self.cScene.selectedItems()
        yeniParent = self.cScene.activeItem
        items.remove(yeniParent)
        self.cScene.undoStack.beginMacro(self.tr("parent"))
        for i in items:

            # secili olanlardan biri halihzazirda ayni active itema zaten parent edilmis ise.
            if i.parentItem() == yeniParent:
                continue

            # parent swap
            tempList = []
            i_all_childitems_in_hierarchy = self.get_all_childitems_in_hierarchy(tempList, i)
            # if parent in i.childItems():
            if yeniParent in i_all_childitems_in_hierarchy:
                grandParent = i.parentItem()
                if not grandParent:
                    self.cScene.unGroupedRootItems.add(yeniParent)
                    yeniPos = yeniParent.scenePos()
                else:
                    yeniPos = grandParent.mapFromScene(yeniParent.scenePos())
                # unparent line added to reset rotation.
                undoRedo.undoableUnParent(self.cScene.undoStack, self.tr("_unparent"), yeniParent, None, yeniPos)
                # undoRedo.undoableParent(self.cScene.undoStack, "_parent", yeniParent, grandParent, yeniPos)

            yeniPos = yeniParent.mapFromScene(i.scenePos())
            if i.parentItem():
                # unparent line added to reset rotation.
                undoRedo.undoableUnParent(self.cScene.undoStack, self.tr("_unparent"), i, None, i.scenePos())
            undoRedo.undoableParent(self.cScene.undoStack, self.tr("_parent"), i, yeniParent, QPointF(yeniPos))
            i.setSelected(False)
        self.cScene.undoStack.endMacro()

        yeniParent.setSelected(True)
        self.log(self.tr("Parented"), 5000, toStatusBarOnly=True)
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_unparent_items(self, item=None):
        self.lutfen_bekleyin_goster()
        items = set()
        if item:
            items.add(item)
        else:

            for item in self.cScene.selectionQueue:
                if item.parentItem() in self.cScene.selectionQueue:
                    items.add(self.cScene.get_items_selected_top_level_parentitem(item))
                else:
                    # filtering possible nonparent and nonparented items
                    if item.type() == shared.GROUP_ITEM_TYPE:
                        if not (item.parentItem() or item.parentedWithParentOperation):
                            continue
                    else:
                        if not (item.parentItem() or item.childItems()):
                            continue
                    items.add(item)

        self.cScene.undoStack.beginMacro(self.tr("unparent"))

        for item in items:
            if item.parentItem():  # parented item olarak sadece bunu unparent ediyoruz icerigi kaliyor.
                undoRedo.undoableUnParent(self.cScene.undoStack, self.tr("_unparent"), item, None, item.scenePos())

            else:
                if item.type() == shared.GROUP_ITEM_TYPE:
                    # group.itemChange de ItemChildRemovedChange var. dolayısıyla kopyada iter ediyoruz
                    for c in item.parentedWithParentOperation[:]:
                        undoRedo.undoableUnParent(self.cScene.undoStack, self.tr("_unparent"), c, None, c.scenePos())
                else:
                    for c in item.childItems():
                        undoRedo.undoableUnParent(self.cScene.undoStack, self.tr("_unparent"), c, None, c.scenePos())
        self.cScene.undoStack.endMacro()
        self.log(self.tr("Unparented"), 5000, toStatusBarOnly=True)
        self.lutfen_bekleyin_gizle()

        # for i in self.cScene.selectedItems():
        #     i.setSelected(False)
        # item.setSelected(True)

    # ---------------------------------------------------------------------
    @Slot()
    def act_group_items(self):
        self.lutfen_bekleyin_goster()
        self.cScene.undoStack.beginMacro(self.tr("group"))
        items = self.cScene.selectedItems()
        undoRedo.undoableGroup(self.cScene.undoStack, self.tr("add single item to group"), items, self.cScene)
        self.cScene.undoStack.endMacro()
        self.radioCizgi.setChecked(True)
        self.act_radio_secim_degisti(self.radioCizgi)
        self.log(self.tr("Grouped"), 5000, toStatusBarOnly=True)
        self.lutfen_bekleyin_gizle()

    # # ---------------------------------------------------------------------
    # @Slot()
    # def act_group_items_ilk(self):
    # 
    #     group = Group()
    #     # group = QGraphicsItemGroup(None)
    #     group.setFlags(group.ItemIsSelectable
    #                    | group.ItemIsMovable
    #                    # | group.ItemIsFocusable
    #                    )
    # 
    #     self.cScene.undoStack.beginMacro(self.tr("group"))
    # 
    #     undoRedo.undoableAddItem(self.cScene.undoStack, 
    #                              description=self.tr("add group"), 
    #                              scene=self.cScene, item=group)
    #     self.increase_zvalue(group)
    #     items = self.cScene.selectedItems()
    # 
    #     # TODO: muhtemelen duzeldi, ama İnşaAllah yine bi bakalim sonra : 
    #     #  self.unGroupedRootItems a ekleniyor ve silinmiyordu itemlar. 
    #     #  ama bu tabi eski sistemde. child ve parent secili ise şimdi sadece parentlar ekleniyor gruba.

    #     for item in items:
    #         if item.parentItem():
    #             if item.parentItem() in items:  # o zaman bunu gruplamaya gerek yok cunku parenti gruplanacak zaten.
    #                 item.setFlag(item.ItemIsSelectable, False)
    #                 item.setFlag(item.ItemIsMovable, False)
    #                 item.setFlag(item.ItemIsFocusable, False)
    #                 # muhtemelen parentta da sorun var
    #                 # continue
    #             else:
    #                 self.act_unparent_items(item)
    #                 # group.addSingleItemToGroup(item)
    #                 undoRedo.undoableGroup(self.cScene.undoStack, self.tr("add single item to group"), item, group)
    #                 # TODO: if ile kontrol etsek once daha mi hizli olur, time complexity ye bakmak lazim.
    #                 # gruplandigi icin referansi parentta olacak ayrica tutmaya gerek yok
    #                 # burda da ihtiyac var discarda cunku yukarda unparent edilince ekleniyor unGroupedRootItems a.
    #                 self.cScene.unGroupedRootItems.discard(item)
    #         else:
    #             if item.childItems():  # sadece parent secilmis iken alt nesneleri secilemez hale getiriyoruz.
    #                 for c in item.childItems():
    #                     c.setFlag(item.ItemIsSelectable, False)
    #                     c.setFlag(item.ItemIsMovable, False)
    #                     c.setFlag(item.ItemIsFocusable, False)
    #             # group.addSingleItemToGroup(item)
    #             undoRedo.undoableGroup(self.cScene.undoStack, self.tr("add single item to group"), item, group)
    #             # TODO: if ile kontrol etsek once daha mi hizli olur, time complexity ye bakmak lazim.
    #             # gruplandigi icin referansi parentta olacak ayrica tutmaya gerek yok
    #             self.cScene.unGroupedRootItems.discard(item)
    #     group.updateBoundingRect()
    #     group.setSelected(True)
    #
    #     self.cScene.undoStack.endMacro()
    #     self.log(self.tr("Grouped"), 5000, toStatusBarOnly=True)

    # ---------------------------------------------------------------------
    @Slot()
    def act_ungroup_items(self):
        self.lutfen_bekleyin_goster()
        grup = self.cScene.activeItem
        if grup.type() == shared.GROUP_ITEM_TYPE:
            # gRot = group.rotation()
            # group.destroyGroup()
            self.cScene.undoStack.beginMacro(self.tr("ungroup"))
            undoRedo.undoableUnGroup(self.cScene.undoStack, self.tr("ungroup"), grup)
            # if gRot:
            #     for item in self.cScene.selectionQueue:
            #         if item.parentItem() in self.cScene.selectionQueue:
            #             continue
            #         if item.type() == PathItem.Type:
            #             undoRedo.undoableRotate(self.cScene.undoStack, "rotate", item, gRot)
            #         else:
            #             undoRedo.undoableRotateWithOffset(self.cScene.undoStack, "rotate", item, gRot)

            self.cScene.undoStack.endMacro()

            self.log(self.tr("Ungrouped"), 5000, toStatusBarOnly=True)
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_about(self):
        QMessageBox.about(self, self.tr('About Defter {}'.format(VERSION)),
                          self.tr('"Defter" is developed by Erdinc Yilmaz. Copyright (C) 2022 '))

    # ---------------------------------------------------------------------
    @Slot()
    def act_import_background_image(self):

        fn = QFileDialog.getOpenFileName(self,
                                         self.tr("Select Background Image ..."),
                                         self.sonKlasorResimler,
                                         self.supportedImageFormats)

        if fn[0]:
            filePath = fn[0]
            undoRedo.undoableSetSceneBackgroundImage(self.cScene.undoStack,
                                                     self.tr("change scene's background image"),
                                                     view=self.cView, imagePath=filePath)
            self.sonKlasorResimler = os.path.dirname(filePath)

    # ---------------------------------------------------------------------
    @Slot()
    def act_clear_background_image(self):
        # self.cView.set_background_image(None)
        undoRedo.undoableSetSceneBackgroundImage(self.cScene.undoStack,
                                                 self.tr("clear scene's background image"),
                                                 view=self.cView, imagePath=None)

    # ---------------------------------------------------------------------
    @Slot()
    def act_embed_background_image(self):
        # self.cView.set_background_image(None)
        undoRedo.undoableEmbedSceneBackgroundImage(self.cScene.undoStack,
                                                   self.tr("embed scene's background image"),
                                                   view=self.cView)

        self.log(self.tr("Scene's background image is embeded."), 5000, 1)

    # ---------------------------------------------------------------------
    def renk_sec(self, eskiRenk, baslik, anlikRenkGonderilecekFonksiyon=None):
        renkDialog = QColorDialog(self)
        renkDialog.setWindowTitle(baslik)
        renkDialog.setOptions(
            QColorDialog.DontUseNativeDialog
            | QColorDialog.ShowAlphaChannel
        )
        if anlikRenkGonderilecekFonksiyon:
            renkDialog.currentColorChanged.connect(anlikRenkGonderilecekFonksiyon)

        renkDialog.setCurrentColor(eskiRenk)
        if renkDialog.exec() == QColorDialog.Accepted:
            return renkDialog.currentColor()
        return QColor()

    # ---------------------------------------------------------------------
    def onizle_change_background_color(self, col):
        self.cView.setBackgroundBrush(col)

    # ---------------------------------------------------------------------
    @Slot()
    def act_change_background_color(self):

        eskiRenk = self.cView.backgroundBrush().color()
        col = self.renk_sec(eskiRenk=eskiRenk,
                            baslik=self.tr("Background Color"),
                            anlikRenkGonderilecekFonksiyon=self.onizle_change_background_color)
        self.onizle_change_background_color(eskiRenk)

        if not col.isValid():
            return
        # self.cScene.setBackgroundBrush(col)
        undoRedo.undoableSetSceneBackgroundBrush(self.cScene.undoStack, self.tr("change scene's background color"),
                                                 view=self.cView, color=col)

    # ---------------------------------------------------------------------
    def _make_callback_sol_tiklanan_butonla_renk_degistir(self, button, tip):
        return lambda: self.act_sol_tiklanan_butonla_renk_degistir(button, tip)

    # ---------------------------------------------------------------------
    def _make_callback_sag_tiklanan_butona_renk_secip_ata(self, button, tip):
        return lambda: self.act_sag_tiklanan_butona_renk_secip_ata(button, tip)

    # ---------------------------------------------------------------------
    def ver_renk_palet_buton(self, tip, gen, yuk, renk, parent):
        btn = PushButtonRenk("", gen, yuk, renk, parent)
        btn.setStatusTip(self.tr("Left click to set line color, Right click to modify color."))
        btn.setToolTip(self.tr("Left click to set line color, Right click to modify color."))

        btn.clicked.connect(self._make_callback_sol_tiklanan_butonla_renk_degistir(btn, tip))
        btn.sagTiklandi.connect(self._make_callback_sag_tiklanan_butona_renk_secip_ata(btn, tip))

        return btn

    # ---------------------------------------------------------------------
    @Slot()
    def act_sag_tiklanan_butona_renk_secip_ata(self, btn, tip):

        # bir de belki sag tiklayinca bg colora transparent secengi olsun.

        if tip == "y":
            yeni_renk = self.act_set_item_text_color(col=None, eskiRenk=btn.renk)
        elif tip == "a":
            yeni_renk = self.act_set_item_background_color(col=None, eskiRenk=btn.renk)
        elif tip == "c":
            yeni_renk = self.act_set_item_line_color(col=None, eskiRenk=btn.renk)

        if not yeni_renk.isValid():
            return

        btn.renkGuncelle(yeni_renk)

    # ---------------------------------------------------------------------
    @Slot()
    def act_sol_tiklanan_butonla_renk_degistir(self, btn, tip):
        if btn.renk:
            if tip == "a":
                self.act_set_item_background_color(col=btn.renk, eskiRenk=self.nesneArkaplanRengiBtn.renk)
            if tip == "y":
                self.act_set_item_text_color(col=btn.renk, eskiRenk=self.yaziRengiBtn.renk)
            elif tip == "c":
                self.act_set_item_line_color(col=btn.renk, eskiRenk=self.cizgiRengiBtn.renk)
        else:
            self.act_sag_tiklanan_butona_renk_secip_ata(btn, tip)

    # ---------------------------------------------------------------------
    def onizle_set_item_text_color(self, col, ilkHaleDondur=False):

        if self.cScene.selectionQueue:
            if ilkHaleDondur:
                for item in self.cScene.selectionQueue:
                    # if item.type() == shared.GROUP_ITEM_TYPE:
                    #     continue
                    item.setYaziRengi(item.gecici_degisken_eski_col)
                    del item.gecici_degisken_eski_col
            else:
                for item in self.cScene.selectionQueue:
                    # if item.type() == shared.GROUP_ITEM_TYPE:
                    #     continue
                    if not hasattr(item, "gecici_degisken_eski_col"):
                        item.gecici_degisken_eski_col = item.yaziRengi
                    item.setYaziRengi(col)

    # ---------------------------------------------------------------------
    @Slot()
    def act_set_item_text_color(self, col=None, eskiRenk=None, renkSecicidenMi=False):

        if not eskiRenk:
            eskiRenk = self.yaziRengiBtn.renk

        if not col:
            #  # eskiRenk=self.yaziRengi, olamiyor cunku dokuman yazi rengi o an secili nesneden farkli olabilir.
            col = self.renk_sec(eskiRenk=eskiRenk,
                                baslik=self.tr("Text Color"),
                                anlikRenkGonderilecekFonksiyon=self.onizle_set_item_text_color)
            if not col.isValid():
                self.onizle_set_item_text_color(col=None, ilkHaleDondur=True)
                return QColor()

        # nesne(ler) icin degistir
        if self.cScene.selectionQueue:
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.beginMacro(self.tr("change items' text color"))
            for item in self.cScene.selectionQueue:
                # if item.type() == shared.GROUP_ITEM_TYPE:
                #     continue
                undoRedo.undoableSetTextColor(self.cScene.undoStack,
                                              self.tr("change item's text color"),
                                              item, col, renkSecicidenMi)
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.endMacro()
        else:  # sahne icin degistir
            self.cScene.aktifArac.yaziRengi = col
            self.degistir_yazi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=True,
                                           renkSecicidenMi=renkSecicidenMi)

        return col

    # ---------------------------------------------------------------------
    def onizle_set_item_line_color(self, col, ilkHaleDondur=False):
        if self.cScene.selectionQueue:
            if ilkHaleDondur:
                for item in self.cScene.selectionQueue:
                    # if item.type() == shared.GROUP_ITEM_TYPE:
                    #     continue
                    item.setCizgiRengi(item.gecici_degisken_eski_col)
                    del item.gecici_degisken_eski_col
            else:
                for item in self.cScene.selectionQueue:
                    # if item.type() == shared.GROUP_ITEM_TYPE:
                    #     continue
                    if not hasattr(item, "gecici_degisken_eski_col"):
                        item.gecici_degisken_eski_col = item.cizgiRengi
                    item.setCizgiRengi(col)

    # ---------------------------------------------------------------------
    @Slot()
    def act_set_item_line_color(self, col=None, eskiRenk=None, renkSecicidenMi=False):

        if not eskiRenk:
            eskiRenk = self.cScene.aktifArac.cizgiRengi

        if not col:
            col = self.renk_sec(eskiRenk=eskiRenk,
                                baslik=self.tr("Line Color"),
                                anlikRenkGonderilecekFonksiyon=self.onizle_set_item_line_color)
            if not col.isValid():
                self.onizle_set_item_line_color(col=None, ilkHaleDondur=True)
                return QColor()

        # nesne(ler) icin degistir
        if self.cScene.selectionQueue:
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.beginMacro(self.tr("change items' line color"))
            for item in self.cScene.selectionQueue:
                # if item.type() == shared.GROUP_ITEM_TYPE:
                #     continue
                undoRedo.undoableSetLineColor(self.cScene.undoStack,
                                              self.tr("change item's line color"),
                                              item, col, renkSecicidenMi)
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.endMacro()
        else:  # sahne icin degistir
            self.cScene.aktifArac.cizgiRengi = col
            self.degistir_cizgi_rengi_ikonu(col, nesne_arkaplan_ikonu_guncelle=True,
                                            renkSecicidenMi=renkSecicidenMi)

        return col

    # ---------------------------------------------------------------------
    def onizle_set_item_background_color(self, col, ilkHaleDondur=False):
        if ilkHaleDondur:
            for item in self.cScene.selectionQueue:
                # if item.type() == shared.GROUP_ITEM_TYPE or item.type() == shared.LINE_ITEM_TYPE:
                #     continue
                item.setArkaPlanRengi(item.gecici_degisken_eski_col)
                del item.gecici_degisken_eski_col

        else:
            for item in self.cScene.selectionQueue:
                # if item.type() == shared.GROUP_ITEM_TYPE or item.type() == shared.LINE_ITEM_TYPE:
                #     continue
                if not hasattr(item, "gecici_degisken_eski_col"):
                    item.gecici_degisken_eski_col = item.arkaPlanRengi
                item.setArkaPlanRengi(col)

    # ---------------------------------------------------------------------
    @Slot()
    def act_set_item_background_color(self, col=None, eskiRenk=None, renkSecicidenMi=False):

        if not eskiRenk:
            eskiRenk = self.cScene.aktifArac.arkaPlanRengi

        if not col:
            col = self.renk_sec(eskiRenk=eskiRenk,
                                baslik=self.tr("Background Color"),
                                anlikRenkGonderilecekFonksiyon=self.onizle_set_item_background_color)

            if not col.isValid():
                # eger diyalog acildiysa itemin son rengi dialog acilmadan onceki renkten farkli olacak
                # unduRedo lu bir sekilde secilen rengi gondermeden once, dilagotan onceki haline donduruyoruz
                self.onizle_set_item_background_color(col=None, ilkHaleDondur=True)
                return QColor()

        # nesne(ler) icin degistir
        if self.cScene.selectionQueue:
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.beginMacro(self.tr("change items' background color"))
            for item in self.cScene.selectionQueue:
                # if item.type() == shared.GROUP_ITEM_TYPE or item.type() == shared.LINE_ITEM_TYPE:
                #     continue
                #     # for c in item.childItems():
                #     #     c.undoableSetItemBackgroundColor(self.cScene.undoStack,
                #     #                                             self.tr("change item's background color"), c, col)
                # if not item.type() == shared.LINE_ITEM_TYPE:
                undoRedo.undoableSetItemBackgroundColor(self.cScene.undoStack,
                                                        self.tr("change item's background color"),
                                                        item, col, renkSecicidenMi)
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.endMacro()
        else:  # sahne icin degistir
            self.cScene.aktifArac.arkaPlanRengi = col
            self.degistir_nesne_arkaplan_rengi_ikonu(renkSecicidenMi=renkSecicidenMi)

        return col

    # ---------------------------------------------------------------------
    def degistir_yazi_rengi_ikonu(self, yaziRengi=None, nesne_arkaplan_ikonu_guncelle=True,
                                  renkSecicidenMi=False):
        if not yaziRengi:
            yaziRengi = self.cScene.aktifArac.yaziRengi

        pix = QPixmap(16, 16)
        # pix.fill(color)

        font = QFont("serif", 13, QFont.Bold)

        pix.fill(Qt.transparent)
        # ~ pixFont = QPixmap(16, 16)
        painterTC = QPainter(pix)
        painterTC.setFont(font)
        painterTC.setPen(yaziRengi)
        painterTC.drawText(pix.rect(), Qt.AlignCenter, "A")
        # painterTC.drawRect(0, 0, 15, 15)
        painterTC.end()
        painterTC = None
        del painterTC

        # self.actionItemLineColor.setIcon(QIcon(pix))
        self.actionItemTextColor.setIcon(QIcon(pix))
        try:
            self.yaziRengiBtn.renkGuncelle(yaziRengi)
            if self.renk_tipi == "y" and not renkSecicidenMi:
                self.renkSecici.disardan_renk_gir(yaziRengi)

        except Exception as e:
            pass

        if nesne_arkaplan_ikonu_guncelle:
            self.degistir_nesne_arkaplan_rengi_ikonu()

    # ---------------------------------------------------------------------
    def degistir_cizgi_rengi_ikonu(self, cizgiRengi=None, nesne_arkaplan_ikonu_guncelle=True,
                                   renkSecicidenMi=False):

        if not cizgiRengi:
            cizgiRengi = self.cScene.aktifArac.cizgiRengi

        pix = QPixmap(16, 16)
        # pix.fill(color)

        # font = QFont("serif", 13, QFont.Bold)

        pix.fill(Qt.transparent)
        # pixFont = QPixmap(16, 16)
        # pix.fill(Qt.black)
        painterTC = QPainter(pix)
        # painterTC.setFont(font)
        pen = QPen(cizgiRengi)
        pen.setWidth(3)
        painterTC.setPen(pen)
        # painterTC.drawText(pixFont.rect(), Qt.AlignCenter, "A")
        # painterTC.drawRect(2, 2, 12, 12)
        painterTC.drawLine(0, 16, 16, 0)
        painterTC.end()
        painterTC = None
        del painterTC

        self.actionItemLineColor.setIcon(QIcon(pix))
        try:
            self.cizgiRengiBtn.renkGuncelle(cizgiRengi)
            if self.renk_tipi == "c" and not renkSecicidenMi:
                self.renkSecici.disardan_renk_gir(cizgiRengi)
        except Exception as e:
            pass

        if nesne_arkaplan_ikonu_guncelle:
            self.degistir_nesne_arkaplan_rengi_ikonu()

    # ---------------------------------------------------------------------
    def degistir_nesne_arkaplan_rengi_ikonu(self, arkaplanRengi=None, yaziRengi=None, cizgiRengi=None,
                                            renkSecicidenMi=False):

        if not arkaplanRengi:
            arkaplanRengi = self.cScene.aktifArac.arkaPlanRengi

        # if not yaziRengi:
        #     yaziRengi = self.cScene.aktifArac.yaziRengi
        #
        # if not cizgiRengi:
        #     cizgiRengi = self.cScene.aktifArac.cizgiRengi

        pix = QPixmap(16, 16)
        # pix.fill(color)

        # pixTextBackgroundColor = QPixmap(16, 16)
        pix.fill(arkaplanRengi)

        painter = QPainter(pix)
        # pix2 = QPixmap(8, 8)
        # pix2.fill(Qt.red)
        # painterTextBgColor.drawPixmap(pix2.rect(), pix2)

        # font = QFont("serif", 14, QFont.Bold)
        # font = QFont("serif")
        # font.setBold(True)
        # font.setPointSize(14)

        # font = QFont("serif", 8)
        # painter.setFont(font)
        # painter.setPen(QColor(Qt.red))
        # painter.setPen(cizgiRengi)
        # painter.drawRect(0, 0, 15, 15)
        # painter.setPen(yaziRengi)
        # pixFont = QPixmap(16, 16)
        # painter.drawText(pixFont.rect(), Qt.AlignCenter, "A")
        painter.end()
        painter = None
        del painter

        self.actionItemBackgroundColor.setIcon(QIcon(pix))

        try:
            self.nesneArkaplanRengiBtn.renkGuncelle(arkaplanRengi)
            if self.renk_tipi == "a" and not renkSecicidenMi:
                self.renkSecici.disardan_renk_gir(arkaplanRengi)

        except Exception as e:
            pass

    # ---------------------------------------------------------------------
    def kur_sahne_arac_degerleri(self):
        self.change_text_size_spinbox_value(self.currentFont.pointSize())
        self.change_font_combobox_value(self.currentFont)
        # self.itemRotationSBox_tbar.setValue(item.rotation())
        # self.itemRotationSBox_nesnedw.setValue(item.rotation())
        self.yazi_hizalama_degisti(self.yazi_hizasi)
        self.karakter_bicimi_degisti(self.karakter_bicimi_sozluk)

        self.degistir_yazi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=False)
        self.degistir_cizgi_rengi_ikonu(nesne_arkaplan_ikonu_guncelle=False)
        self.degistir_nesne_arkaplan_rengi_ikonu()

    # ---------------------------------------------------------------------
    # @Slot(Qt.PenStyle)
    def act_cizgi_tipi_degistir(self, penStyle_int):

        # activated kullanirsak
        # lineStyle = Qt.PenStyle(self.cizgiTipiCBox.itemData(self.cizgiTipiCBox.currentIndex(), Qt.UserRole))
        lineStyle = Qt.PenStyle(penStyle_int)

        if self.cScene.selectionQueue:
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.beginMacro(self.tr("change items' line style"))
            for item in self.cScene.selectionQueue:
                undoRedo.undoableSetLineStyle(self.cScene.undoStack, self.tr("change item's line style"), item,
                                              lineStyle)
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.endMacro()

        else:
            self.cScene.aktifArac.cizgiTipi = lineStyle

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_cizgi_birlesim_tipi_degistir(self, joinStyle_int):
        joinStyle = Qt.PenJoinStyle(joinStyle_int)

        if self.cScene.selectionQueue:
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.beginMacro(self.tr("change items' line join style"))
            for item in self.cScene.selectionQueue:
                undoRedo.undoableSetLineJoinStyle(self.cScene.undoStack, self.tr("change item's line join style"), item,
                                                  joinStyle)
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.endMacro()
        else:
            self.cScene.aktifArac.cizgiBirlesimTipi = joinStyle

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_cizgi_ucu_tipi_degistir(self, capStyle_int):
        capStyle = Qt.PenCapStyle(capStyle_int)

        if self.cScene.selectionQueue:
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.beginMacro(self.tr("change items' line cap style"))
            for item in self.cScene.selectionQueue:
                undoRedo.undoableSetLineCapStyle(self.cScene.undoStack, self.tr("change item's line cap style"), item,
                                                 capStyle)
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.endMacro()

        else:
            self.cScene.aktifArac.cizgiUcuTipi = capStyle

    # ---------------------------------------------------------------------
    def fircaBuyult(self):
        self.cScene.aktifArac.cizgiKalinligi += 0.5
        self.change_line_widthF(self.cScene.aktifArac.cizgiKalinligi)
        return self.cScene.aktifArac.cizgiKalinligi

    # ---------------------------------------------------------------------
    def fircaKucult(self):
        if self.cScene.aktifArac.cizgiKalinligi > 1:
            self.cScene.aktifArac.cizgiKalinligi -= 0.5
            self.change_line_widthF(self.cScene.aktifArac.kalem.widthF())
        return self.cScene.aktifArac.cizgiKalinligi

    # ---------------------------------------------------------------------
    def fircaDirektDegerGir(self, direktDeger):
        self.cScene.aktifArac.cizgiKalinligi = direktDeger
        self.change_line_widthF(direktDeger)

    # ---------------------------------------------------------------------
    @Slot(int)
    @Slot(float)
    def act_cizgi_kalinligi_degistir(self, widthF):

        if self.cScene.selectionQueue:
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.beginMacro(self.tr("change items' line width"))
            for item in self.cScene.selectionQueue:
                undoRedo.undoableSetLineWidthF(self.cScene.undoStack, self.tr("change item's line width"), item, widthF)
            if len(self.cScene.selectionQueue) > 1:
                self.cScene.undoStack.endMacro()

        else:
            self.cScene.aktifArac.cizgiKalinligi = widthF

    # ---------------------------------------------------------------------
    @Slot()
    def act_cizgi_ozelliklerini_sifirla(self):

        if self.cScene.selectionQueue:
            self.cScene.undoStack.beginMacro(self.tr("reset items' line properties"))
            for item in self.cScene.selectionQueue:
                undoRedo.undoableSetLineStyle(self.cScene.undoStack, self.tr("change item's line style"), item,
                                              Qt.SolidLine)
                undoRedo.undoableSetLineJoinStyle(self.cScene.undoStack, self.tr("change item's line join style"), item,
                                                  Qt.RoundJoin)
                undoRedo.undoableSetLineCapStyle(self.cScene.undoStack, self.tr("change item's line cap style"), item,
                                                 Qt.FlatCap)
                undoRedo.undoableSetLineWidthF(self.cScene.undoStack, self.tr("change item's line width"), item, 0)
            self.cScene.undoStack.endMacro()

        else:
            self.cizgiTipiCBox.setCurrentIndex(1)
            self.cizgiBirlesimTipiCBox.setCurrentIndex(0)
            self.cizgiUcuTipiCBox.setCurrentIndex(0)
            self.change_line_widthF(0)

            self.cScene.aktifArac.kalem = QPen(self.cScene.aktifArac.cizgiRengi,
                                               0,
                                               Qt.SolidLine,
                                               Qt.FlatCap,
                                               Qt.RoundJoin)

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_change_item_width(self, width):

        self.itemSize = QSizeF(width, self.itemHeightSBox_tbar.value())

        if self.cScene.selectionQueue:
            startedMacro = False
            for item in self.cScene.selectionQueue:
                if isinstance(item, BaseItem) or item.type() == shared.TEXT_ITEM_TYPE:
                    if not startedMacro:
                        self.cScene.undoStack.beginMacro(self.tr("change width"))
                        startedMacro = True
                    undoRedo.undoableResizeBaseItem(self.cScene.undoStack,
                                                    self.tr("change width"),
                                                    item,
                                                    QRectF(item.rect().topLeft(), self.itemSize / item.scale()),
                                                    item.rect(),
                                                    item.pos())

                elif item.type() == shared.LINE_ITEM_TYPE:
                    if not startedMacro:
                        self.cScene.undoStack.beginMacro(self.tr("change length"))
                        startedMacro = True

                        eskiLine = item._line
                        yeniLine = QLineF(eskiLine)
                        if not width:
                            width = 0.1
                        yeniLine.setLength(width)
                        undoRedo.undoableResizeLineItem(self.cScene.undoStack,
                                                        "change length",
                                                        item,
                                                        # yeniRect=self.rect(),
                                                        yeniLine=yeniLine,
                                                        eskiLine=eskiLine,
                                                        eskiPos=item.pos())

            if startedMacro:
                self.cScene.undoStack.endMacro()

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_change_item_height(self, height):

        self.itemSize = QSizeF(self.itemWidthSBox_tbar.value(), height)

        if self.cScene.selectionQueue:
            startedMacro = False
            for item in self.cScene.selectionQueue:
                if isinstance(item, BaseItem) or item.type() == shared.TEXT_ITEM_TYPE:
                    if not startedMacro:
                        self.cScene.undoStack.beginMacro(self.tr("change height"))
                        startedMacro = True
                    undoRedo.undoableResizeBaseItem(self.cScene.undoStack,
                                                    self.tr("change height"),
                                                    item,
                                                    QRectF(item.rect().topLeft(), self.itemSize / item.scale()),
                                                    item.rect(),
                                                    item.pos())
            if startedMacro:
                self.cScene.undoStack.endMacro()

    # ---------------------------------------------------------------------
    @Slot(QFont)
    def act_set_current_font(self, font):
        font = QFont(font)
        font.setPointSize(self.textSize)
        if self.cScene.selectionQueue:
            startedMacro = False
            for item in self.cScene.selectionQueue:
                if item.type() is not shared.GROUP_ITEM_TYPE:
                    if not startedMacro:
                        self.cScene.undoStack.beginMacro(self.tr("change font"))
                        startedMacro = True
                    undoRedo.undoableSetFont(self.cScene.undoStack,
                                             self.tr("change font"), item, QFont(font))
            if startedMacro:
                self.cScene.undoStack.endMacro()
        else:
            self.currentFont = font
            self.cScene.setFont(QFont(font))

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_change_text_size(self, value):
        self.textSize = value

        if self.cScene.selectionQueue:
            startedMacro = False
            for item in self.cScene.selectionQueue:
                if item.type() is not shared.GROUP_ITEM_TYPE:
                    if not startedMacro:
                        self.cScene.undoStack.beginMacro(self.tr("change text size"))
                        startedMacro = True
                    undoRedo.undoableSetFontSize(self.cScene.undoStack, self.tr("change text size"), item, value)
            if startedMacro:
                self.cScene.undoStack.endMacro()
        else:
            self.currentFont.setPointSize(value)
            self.cScene.setFont(QFont(self.currentFont))

    # ---------------------------------------------------------------------
    @Slot(int)
    def act_change_item_rotation(self, rotation):

        if not self.cScene.selectionQueue:
            return

        self.cScene.undoStack.beginMacro(self.tr("rotate"))
        for item in self.cScene.selectionQueue:
            if item.parentItem() in self.cScene.selectionQueue:
                continue
            if item.type() == shared.PATH_ITEM_TYPE:
                undoRedo.undoableRotate(self.cScene.undoStack, self.tr("rotate"), item, rotation)
            else:
                undoRedo.undoableRotateWithOffset(self.cScene.undoStack, self.tr("rotate"), item, rotation)

        self.cScene.undoStack.endMacro()

    # ---------------------------------------------------------------------
    def change_transform_box_values(self, item):
        if item.type() == shared.LINE_ITEM_TYPE:
            self.itemWidthSBox_tbar.setValue(item._line.length() * item.scale())
            self.itemWidthSBox_nesnedw.setValue(item._line.length() * item.scale())

            self.itemRotationSBox_tbar.setValue(item.rotation())
            self.itemRotationSBox_nesnedw.setValue(item.rotation())
        else:
            self.itemWidthSBox_tbar.setValue(item.rect().width() * item.scale())
            self.itemWidthSBox_nesnedw.setValue(item.rect().width() * item.scale())

            self.itemHeightSBox_tbar.setValue(item.rect().height() * item.scale())
            self.itemHeightSBox_nesnedw.setValue(item.rect().height() * item.scale())

            self.itemRotationSBox_tbar.setValue(item.rotation())
            self.itemRotationSBox_nesnedw.setValue(item.rotation())

            self.itemSize = QSizeF(self.itemWidthSBox_tbar.value(), self.itemHeightSBox_tbar.value())

    # ---------------------------------------------------------------------
    def change_text_size_spinbox_value(self, sizeVal):

        self.textSizeSBox_tbar.setValue(sizeVal)
        self.textSizeSBox_yazidw.setValue(sizeVal)
        # self.textSize = sizeVal
        # self.currentFont.setPointSize(sizeVal)
        # self.cScene.setFont(self.currentFont)

    # ---------------------------------------------------------------------
    def change_font_combobox_value(self, font):

        self.fontCBox_tbar.setCurrentFont(font)
        self.fontCBox_yazidw.setCurrentFont(font)

        # burda qfont kullaniyoruz cunku onceki itemdan geliyor font, dolayisiyla, instance oluyor.
        # ister istemez etkiliyor onceki itemi ,degisiklikler, secili olmasa da item.
        # self.currentFont = QFont(font)
        # self.cScene.setFont(font)

    # ---------------------------------------------------------------------
    def change_line_style_options(self, pen):
        self.cizgiTipiCBox.setCurrentIndex(self.cizgiTipiCBox.findData(pen.style(), Qt.UserRole))
        self.cizgiBirlesimTipiCBox.setCurrentIndex(self.cizgiBirlesimTipiCBox.findData(pen.joinStyle(), Qt.UserRole))
        self.cizgiUcuTipiCBox.setCurrentIndex(self.cizgiUcuTipiCBox.findData(pen.capStyle(), Qt.UserRole))
        self.change_line_widthF(pen.widthF())
        # self.cizgiKalinligiSlider.setValue(pen.width())


    # ---------------------------------------------------------------------
    def change_line_widthF(self, widthF):
        widthFx10 = widthF * 10
        self.cizgiKalinligiDSliderWithDSBox.setValue(widthFx10)
        self.cizgiKalinligiDSliderWithDSBox_tbar.setValue(widthFx10)

    # ---------------------------------------------------------------------
    def _add_style_preset_to_list_widget(self, presetName=None, fg=None, bg=None, cizgiRengi=None, pen=None,
                                         font=None):

        preset = ListWidgetItem(presetName)

        preset.setForeground(fg)
        preset.setBackground(bg)
        preset.setCizgiRengi(cizgiRengi)
        preset.setPen(QPen(pen))
        preset.setPresetFont(font)
        font2 = QFont(font)
        font2.setPointSize(9)
        preset.setFont(font2)
        # preset.setText("{}: {}pt - {}px".format(presetName, self.textSize, self._pen.widthF()))

        self.stylePresetsListWidget.addItem(preset)

        preset2 = ListWidgetItem(presetName)
        preset2.setForeground(fg)
        preset2.setBackground(bg)
        preset2.setCizgiRengi(cizgiRengi)
        preset2.setPen(QPen(pen))
        preset2.setPresetFont(font)
        preset2.setFont(font2)
        self.yuzenStylePresetsListWidget.addItem(preset2)

        count = self.stylePresetsListWidget.count()

        # ! burayi for dongusune cevirmeyin...
        if count < 10:
            preset.setToolTip("Alt + {}".format(count))
            preset2.setToolTip("Alt + {}".format(count))
            # def make_callback(_dosya):
            #     return lambda: self.act_open_def_file(_dosya)
            #
            # action.triggered.connect(make_callback(dosya))

            preset_hotkey = QShortcut(QKeySequence("Alt+{}".format(count)),
                                      self,
                                      lambda throw_away=0: self.act_apply_selected_style(preset))
            preset_hotkey.setContext(Qt.ApplicationShortcut)

    # ---------------------------------------------------------------------
    @Slot()
    def act_add_style_preset(self):
        # stiller pencersi ,stil ekle butonu da,
        # secili nesne sag tik menusundeki secili nesnenin stilini ekle de buraya geliyor.
        text, ok = QInputDialog.getText(self,
                                        self.tr('Create a new style preset'),
                                        self.tr('Preset name:'),
                                        text=self.tr("style"))
        if ok:
            if text == "":
                text = self.tr("style")

            if self.cScene.activeItem:
                fg = self.cScene.activeItem.yaziRengi
                bg = self.cScene.activeItem.arkaPlanRengi
                cizgiRengi = self.cScene.activeItem.cizgiRengi
                pen = self.cScene.activeItem._pen
                font = QFont(self.cScene.activeItem.font())

            else:
                fg = self.cScene.aktifArac.yaziRengi
                bg = self.cScene.aktifArac.arkaPlanRengi
                cizgiRengi = self.cScene.aktifArac.cizgiRengi
                pen = self.cScene.aktifArac.kalem
                font = QFont(self.cScene.aktifArac.yaziTipi)

            presetName = "  {}:  {}pt  {:.1f}px".format(text, font.pointSize(), pen.widthF())

            self._add_style_preset_to_list_widget(presetName, fg, bg, cizgiRengi, pen, font)

    # ---------------------------------------------------------------------
    def act_stylePresetsListWidget_secim_degisti(self):
        if self.stylePresetsListWidget.selectedItems():
            self.removeStylePresetBtn.setEnabled(True)
        else:
            self.removeStylePresetBtn.setEnabled(False)

    # ---------------------------------------------------------------------
    @Slot()
    def act_remove_style_preset(self):

        # if self.stylePresetsListWidget.selectedItems():

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(self.tr("Defter: Delete style preset?"))
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(self.tr("Do you want to delete selected file preset(s)?"))
        msgBox.setInformativeText(self.tr("This is undoable!"))

        deleteButton = msgBox.addButton(self.tr("&Delete"), QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton(self.tr("&Cancel"), QMessageBox.RejectRole)
        # msgBox.addButton(QMessageBox.Cancel)
        msgBox.setDefaultButton(deleteButton)
        msgBox.setEscapeButton(cancelButton)

        msgBox.exec()
        if msgBox.clickedButton() == deleteButton:

            for item in self.stylePresetsListWidget.selectedItems():
                row = self.stylePresetsListWidget.row(item)
                itemToDelete = self.stylePresetsListWidget.takeItem(row)
                # itemToDelete = None
                del itemToDelete

                itemToDelete2 = self.yuzenStylePresetsListWidget.takeItem(row)
                # itemToDelete = None
                del itemToDelete2

    # ---------------------------------------------------------------------
    @Slot(QListWidgetItem)
    def act_apply_selected_style(self, style):
        if self.cScene.selectionQueue:
            self.lutfen_bekleyin_goster()
            self.cScene.undoStack.beginMacro(self.tr("apply style preset to the selected item(s)"))
            for item in self.cScene.selectionQueue:
                # undoableApplyStylePreset(self, description, item, pen, brush, font):
                # pen = QPen(style.foreground().color())

                if item.type() == shared.GROUP_ITEM_TYPE:
                    self.cScene.undoStack.beginMacro(self.tr("apply style preset to the selected group"))
                    for cItem in item.childItems():
                        undoRedo.undoableApplyStylePresetToItem(self.cScene.undoStack,
                                                                self.tr('_apply style preset to the group'),
                                                                item=cItem,
                                                                pen=style.pen(),
                                                                brush=style.background(),
                                                                font=style.presetFont(),
                                                                yaziRengi=style.foreground().color(),
                                                                cizgiRengi=style.cizgiRengi()
                                                                )
                    self.cScene.undoStack.endMacro()
                else:
                    undoRedo.undoableApplyStylePresetToItem(self.cScene.undoStack,
                                                            self.tr('_apply style preset to the selected item'),
                                                            item=item,
                                                            pen=style.pen(),
                                                            brush=style.background(),
                                                            font=style.presetFont(),
                                                            yaziRengi=style.foreground().color(),
                                                            cizgiRengi=style.cizgiRengi()
                                                            )
            self.cScene.undoStack.endMacro()
            self.lutfen_bekleyin_gizle()

        else:

            undoRedo.undoableApplyStylePreset(self.cScene.undoStack, self.tr('apply style preset'),
                                              eskiPen=self.cScene.aktifArac.kalem,
                                              yeniPen=style.pen(),
                                              yaziRengi=style.foreground().color(),
                                              eskiYaziRengi=self.cScene.aktifArac.yaziRengi,
                                              cizgiRengi=style.cizgiRengi(),
                                              eskiCizgiRengi=self.cScene.aktifArac.cizgiRengi,
                                              eskiArkaPlanRengi=self.cScene.aktifArac.arkaPlanRengi,
                                              yeniArkaPlanRengi=style.background().color(),
                                              eskiFont=self.cScene.aktifArac.yaziTipi,
                                              yeniFont=style.presetFont(),
                                              scene=self.cScene)

    # ---------------------------------------------------------------------
    @Slot()
    def act_save_style_presets_to_file(self):
        filtre = self.tr('*.defstyles files (*.defstyles)')
        fn = QFileDialog.getSaveFileName(self,
                                         self.tr('Save style presets'),
                                         self.sonKlasor,  # hem sonklasor hem dosyaadi
                                         filtre
                                         )

        filePath = fn[0]
        if filePath:
            # TODO: uzanti kontrolu yap
            if not filePath.endswith(".defstyles"):
                filePath = '{}.defstyles'.format(filePath)
            self.sonKlasor = os.path.dirname(filePath)

            self.lutfen_bekleyin_goster()
            _file = QSaveFile(filePath)
            if not _file.open(QIODevice.WriteOnly):
                self.lutfen_bekleyin_gizle()
                QMessageBox.warning(self,
                                    'Defter',
                                    self.tr('Could not save file as '
                                            '"{0:s}" : "{1:s}"').format(os.path.basename(filePath),
                                                                        _file.errorString()))
                return False

            try:
                toFileStream = QDataStream(_file)
                toFileStream.setVersion(QDataStream.Qt_5_7)
                toFileStream.writeInt32(DEFSTYLES_MAGIC_NUMBER)
                toFileStream.writeInt16(DEFSTYLES_FILE_VERSION)
                toFileStream.writeQVariant(self.get_style_presets_list_for_saving_binary())
                _file.commit()

            except Exception as e:
                self.lutfen_bekleyin_gizle()
                QMessageBox.warning(self,
                                    'Defter',
                                    self.tr('Could not save file as '
                                            '"{0:s}" : "{1:s}" ').format(os.path.basename(filePath), str(e)))

                # buna ihtiyacımız yok aslında commit cagrilmaz ise zaten QSave in olusturdugu temp dosya siliniyor
                # eger bu noktadan sonra bir commit cagrilcak olsaydi ve cancelWriting deseydik
                #  o zaman o commit gecersiz olacakti, ama burdan sonra da commit cagrilmiyor zaten.
                # _file.cancelWriting()
                return False

    # ---------------------------------------------------------------------
    @Slot()
    def load_style_presets_file_and_return_a_list(self):
        filtre = self.tr('*.defstyles Files (*.defstyles)')
        fn = QFileDialog.getOpenFileName(self,
                                         self.tr('Load style presets...'),
                                         self.sonKlasor,
                                         filtre)
        if fn[0]:
            filePath = fn[0]
            self.lutfen_bekleyin_goster()
            _file = QFile(filePath)
            # if not _file.open(QIODevice.ReadOnly | QIODevice.Text): # QIODevice.Text - eger json load edersek diye.
            if not _file.open(QIODevice.ReadOnly):
                self.lutfen_bekleyin_gizle()
                QMessageBox.warning(self,
                                    'Defter',
                                    self.tr('Could not open file  --   "{0:s}"\n{1:s}').format(filePath,
                                                                                               _file.errorString()))
                return []

            # # read the serialized data from the file
            fromFileStream = QDataStream(_file)
            fromFileStream.setVersion(QDataStream.Qt_5_7)
            magic = fromFileStream.readInt32()
            if magic != DEFSTYLES_MAGIC_NUMBER:
                # raise IOError("unrecognized file type")
                self.log(self.tr('{0:s} : Unrecognized file type!').format(os.path.basename(filePath)), 6000, 3)
                self.lutfen_bekleyin_gizle()
                QMessageBox.warning(self,
                                    'Defter',
                                    self.tr('Could not open file  --   "{0:s}"\n '
                                            'Unrecognized file type!').format(os.path.basename(filePath)))
                return []
            version = fromFileStream.readInt16()
            if version > DEFSTYLES_FILE_VERSION:
                # print("old file")
                pass
            if version > DEFSTYLES_FILE_VERSION:
                # print("new file")
                pass

            presetList = fromFileStream.readQVariant()
            # _file.flush()
            _file.close()

            return presetList

    # ---------------------------------------------------------------------
    @Slot()
    def act_load_and_replace_style_presets(self):
        presetList = self.load_style_presets_file_and_return_a_list()
        if presetList:
            self.populate_style_presets_from_saved_file(presetList, clearAll=True)

    # ---------------------------------------------------------------------
    @Slot()
    def act_load_and_append_style_presets(self):
        presetList = self.load_style_presets_file_and_return_a_list()
        if presetList:
            self.populate_style_presets_from_saved_file(presetList, clearAll=False)

    # ---------------------------------------------------------------------
    @Slot()
    def act_clear_style_presets(self):
        self.stylePresetsListWidget.clear()
        self.yuzenStylePresetsListWidget.clear()

    # ---------------------------------------------------------------------
    def get_style_presets_list_for_saving_binary(self):
        presetList = []
        for i in range(self.stylePresetsListWidget.count()):
            preset = self.stylePresetsListWidget.item(i)
            presetList.append([
                preset.text(),
                preset.foreground(),
                preset.background(),
                preset.pen(),
                preset.presetFont(),
                preset.cizgiRengi()])
        return presetList

    # ---------------------------------------------------------------------
    def populate_style_presets_from_saved_file(self, presetList, clearAll=True):

        if clearAll:
            self.stylePresetsListWidget.clear()

        for savedPreset in presetList:
            self._add_style_preset_to_list_widget(presetName=savedPreset[0],
                                                  fg=savedPreset[1],
                                                  bg=savedPreset[2],
                                                  cizgiRengi=savedPreset[5],
                                                  pen=savedPreset[3],
                                                  font=savedPreset[4])

    # ---------------------------------------------------------------------
    def act_secili_nesne_stilini_secili_araca_uygula(self):

        self.cScene.aktifArac.font = self.cScene.activeItem.font()
        self.cScene.aktifArac.kalem = QPen(self.cScene.activeItem._pen)
        self.cScene.aktifArac.arkaPlanRengi = self.cScene.activeItem.arkaPlanRengi
        self.cScene.aktifArac.yaziRengi = self.cScene.activeItem.yaziRengi
        self.cScene.aktifArac.cizgiRengi = self.cScene.activeItem.cizgiRengi

    # ---------------------------------------------------------------------
    def act_secili_nesne_stilini_kendi_aracina_uygula(self):

        tip = self.cScene.activeItem.type()

        if tip == shared.TEXT_ITEM_TYPE:
            arac = self.cScene.YaziAraci
        elif tip == shared.RECT_ITEM_TYPE:
            arac = self.cScene.DortgenAraci
        elif tip == shared.PATH_ITEM_TYPE:
            arac = self.cScene.KalemAraci
        elif tip == shared.ELLIPSE_ITEM_TYPE:
            arac = self.cScene.YuvarlakAraci
        elif tip == shared.LINE_ITEM_TYPE:
            arac = self.cScene.OkAraci
        elif tip == shared.IMAGE_ITEM_TYPE:
            arac = self.cScene.ResimAraci
        elif tip == shared.VIDEO_ITEM_TYPE:
            arac = self.cScene.VideoAraci
        elif tip == shared.DOSYA_ITEM_TYPE:
            arac = self.cScene.DosyaAraci
        else:
            arac = self.cScene.SecimAraci

        arac.font = self.cScene.activeItem.font()
        arac.kalem = QPen(self.cScene.activeItem._pen)
        arac.arkaPlanRengi = self.cScene.activeItem.arkaPlanRengi
        arac.yaziRengi = self.cScene.activeItem.yaziRengi
        arac.cizgiRengi = self.cScene.activeItem.cizgiRengi

    # ---------------------------------------------------------------------
    @Slot()
    def act_bring_to_front(self):

        if not self.cScene.selectionQueue:
            return

        selectedItem = self.cScene.activeItem
        overlapItems = selectedItem.collidingItems()

        # zValue = 0
        # for item in overlapItems:
        #     if item.zValue() >= zValue:
        #         zValue = item.zValue() + 1

        liste = []
        for item in overlapItems:
            if item.zValue() >= selectedItem.zValue():
                liste.append(item.zValue())

        if liste:
            zValue = min(liste) + 0.1

            if not selectedItem.zValue() == zValue:  # gereksiz undo yigilmasi olmasin diye
                undoRedo.undoableSetZValue(self.cScene.undoStack, self.tr("bring to front"), selectedItem, zValue)

    # ---------------------------------------------------------------------
    @Slot()
    def act_send_to_back(self):

        if not self.cScene.selectionQueue:
            return

        selectedItem = self.cScene.activeItem
        overlapItems = selectedItem.collidingItems()

        # zValue = 0
        # for item in overlapItems:
        #     if item.zValue() <= zValue:
        #         zValue = item.zValue() - 1

        liste = []
        for item in overlapItems:
            if item.zValue() <= selectedItem.zValue():
                liste.append(item.zValue())

        if liste:
            zValue = max(liste) - 0.1

            if not selectedItem.zValue() == zValue:  # gereksiz undo yigilmasi olmasin diye
                undoRedo.undoableSetZValue(self.cScene.undoStack, self.tr("send to back"), selectedItem, zValue)

    # ---------------------------------------------------------------------
    @Slot(bool)
    def act_clean_mode(self, checked):
        if checked:
            self.state_before_clean_mode = self.saveState(version=1)
            self.toolsToolBar.hide()
            self.propertiesToolBar.hide()
            self.fontToolBar.hide()
            self.renkAracCubugu.hide()
            self.cizgiOzellikleriToolBar.hide()
            self.alignToolBar.hide()
            self.utilitiesToolBar.hide()
            self._statusBar.hide()
            self.mBar.hide()
            self.nesneOzellikleriDW.hide()
            self.stillerDW.hide()
            self.baskiSiniriCizimAyarlariDW.hide()
            self.sayfalarDW.hide()
            self.kutuphaneDW.hide()
        else:
            self.mBar.show()
            self._statusBar.show()
            self.restoreState(self.state_before_clean_mode, version=1)

    # ---------------------------------------------------------------------
    @Slot()
    def act_pin_item(self):

        if not self.cScene.selectionQueue:
            return

        self.cScene.undoStack.beginMacro(self.tr("pin"))
        for item in self.cScene.selectionQueue:
            undoRedo.undoableSetPinStatus(self.cScene.undoStack, self.tr("pin"), item, True)
        self.cScene.undoStack.endMacro()

    # ---------------------------------------------------------------------
    @Slot()
    def act_unpin_item(self):
        if not self.cScene.selectionQueue:
            return

        self.cScene.undoStack.beginMacro(self.tr("unpin"))
        for item in self.cScene.selectionQueue:
            undoRedo.undoableSetPinStatus(self.cScene.undoStack, self.tr("unpin"), item, False)
        self.cScene.undoStack.endMacro()

    # ---------------------------------------------------------------------
    @Slot()
    def act_edit_command(self, item):
        if item:  # hotkeyden item none gelirse diye
            # commandDialog = CommandDialog(item, self)
            commandDialog = CommandDialog(item)
            # commandDialog.logger.connect(lambda x: self.log(x, 5000, toStatusBarOnly=True))

            commandDialog.show()
            # if commandDialog.exec():
            #     print("tamam")
        else:
            self.log(self.tr("No active item!"), 5000, toStatusBarOnly=True)

    # ---------------------------------------------------------------------
    @Slot()
    def act_show_html_source(self):
        widget = QDialog(self)
        widget.setAttribute(Qt.WA_DeleteOnClose)
        widget.setWindowTitle(self.tr("Defter: HTML source"))
        layout = QVBoxLayout()
        widget.setLayout(layout)

        textEdit = QTextEdit(widget)
        # self.highlighter = HtmlHighlighter(textEdit.document())
        textEdit.setReadOnly(True)
        layout.addWidget(textEdit)
        textEdit.setPlainText(self.cScene.activeItem.toHtml())
        widget.show()

        # TODO: html kaydederken 2 defa kaydet belki de temizlesin ya da qwebkit ile bi bak

    # ---------------------------------------------------------------------
    def onizle_kut_change_background_color(self, col):
        self.ekranKutuphane.setBackgroundBrush(col)

    # ---------------------------------------------------------------------
    @Slot()
    def act_kut_change_background_color(self):

        eskiRenk = self.ekranKutuphane.backgroundBrush().color()
        col = self.renk_sec(eskiRenk=eskiRenk,
                            baslik=self.tr("Background Color"),
                            anlikRenkGonderilecekFonksiyon=self.onizle_kut_change_background_color)
        self.onizle_kut_change_background_color(eskiRenk)

        if not col.isValid():
            return
        # self.cScene.setBackgroundBrush(col)
        undoRedo.undoableSetSceneBackgroundBrush(self.cScene.undoStack, self.tr("change scene's background color"),
                                                 self.ekranKutuphane, col)

    # ---------------------------------------------------------------------
    @Slot()
    def act_kut_dosya_yoneticisinde_goster(self):

        # if self.cScene.activeItem.type() == Text.Type:
        #     url = self.cScene.activeItem.get_document_url()
        #     url = url.toLocalFile()
        # elif self.cScene.activeItem.type() == Image.Type or self.cScene.activeItem.type() == VideoItem.Type:
        #     url = self.cScene.activeItem.filePathForSave
        # else:
        #     return

        url = self.sahneKutuphane.selectedItems()[0].dosya_adresi
        norm = os.path.normpath(url)

        sistem = platform.system()
        if sistem == "Darwin":

            # norm = os.path.normpath(unicode(self.fsModel.rootPath()))
            # subprocess.Popen(('open %s' % norm))
            os.system(u'open -R "%s"' % norm)

        elif sistem == 'Windows':
            cmd = (r'explorer /select,"%s"' % norm)
            # subprocess.Popen(unicode (cmd ,"utf-8"))
            try:
                subprocess.Popen(cmd)
            except UnicodeEncodeError:
                language, output_encoding = locale.getdefaultlocale()
                subprocess.call(cmd.encode(output_encoding))
        elif sistem == "Linux":
            try:
                # subprocess.call(['xdg-open', os.path.dirname(norm)])
                subprocess.Popen(['xdg-open', os.path.dirname(norm)])
            except Exception as e:
                if subprocess.call(["which", "xdg-open"]) == 1:
                    self.log(self.tr('Please install "xdg-open" from your '
                                     'package manager.'), 500, toStatusBarOnly=True)

                    self.log(self.tr('---------------------------------------\nPlease install "xdg-open" from your '
                                     'package manager. \nMore info at :\nhttps://wiki.archlinux.org/index.php/Xdg-open'
                                     '\nor\nhttp://portland.freedesktop.org/xdg-utils-1.0/xdg-open.html\n'
                                     '---------------------------------------'), 0)

    # ---------------------------------------------------------------------
    @Slot()
    def act_show_in_file_manager(self):

        if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
            url = self.cScene.activeItem.get_document_url()
            url = url.toLocalFile()
        elif self.cScene.activeItem.type() in [shared.IMAGE_ITEM_TYPE, shared.VIDEO_ITEM_TYPE, shared.DOSYA_ITEM_TYPE]:
            url = self.cScene.activeItem.filePathForSave
        else:
            return

        norm = os.path.normpath(url)

        sistem = platform.system()
        if sistem == "Darwin":
            # norm = os.path.normpath(unicode(self.fsModel.rootPath()))
            # subprocess.Popen(('open %s' % norm))
            os.system(u'open -R "%s"' % norm)

        elif sistem == 'Windows':
            cmd = (r'explorer /select,"%s"' % norm)
            # subprocess.Popen(unicode (cmd ,"utf-8"))
            try:
                subprocess.Popen(cmd)
            except UnicodeEncodeError:
                language, output_encoding = locale.getdefaultlocale()
                subprocess.call(cmd.encode(output_encoding))

        elif sistem == "Linux":
            try:
                # subprocess.call(['xdg-open', os.path.dirname(norm)])
                subprocess.Popen(['xdg-open', os.path.dirname(norm)])
            except Exception as e:
                if subprocess.call(["which", "xdg-open"]) == 1:
                    self.log(self.tr('Please install "xdg-open" from your '
                                     'package manager.'), 500, toStatusBarOnly=True)

                    self.log(self.tr('---------------------------------------\nPlease install "xdg-open" from your '
                                     'package manager. \nMore info at :\nhttps://wiki.archlinux.org/index.php/Xdg-open'
                                     '\nor\nhttp://portland.freedesktop.org/xdg-utils-1.0/xdg-open.html\n'
                                     '---------------------------------------'), 0)

    # ---------------------------------------------------------------------
    def create_thread(self, imageURL):
        extension = os.path.splitext(imageURL)[1][1:].lower()
        if extension not in self.supportedImageFormatList:
            self.log(self.tr("Could not load image: Could not find the direct link to the image or "
                             "image type is unsupported.: {}").format(imageURL), 7000, 3)
            return

        imageSavePath = self.cScene.get_unique_path_for_downloaded_html_image(os.path.basename(imageURL))
        dThread = QThread()
        dWorker = DownloadWorker()
        self.workerThreadDict[dWorker] = dThread

        dWorker.moveToThread(dThread)

        dWorker.finished.connect(self.dThread_finished)
        dWorker.failed.connect(self.dthread_clean)
        dWorker.log.connect(self.log)

        dThread.start()
        dWorker.downloadWithThread.emit(imageURL, imageSavePath, QPointF())

    # ---------------------------------------------------------------------
    @Slot()
    def act_localize_html(self):

        imgSrcParser = ImgSrcParser()
        imgSrcParser.feed(self.cScene.activeItem.toHtml())

        # print(self.imgUrlList)
        # to prevent already localized urls to relocalize.
        self.imgUrlList = [x for x in imgSrcParser.urls if not x.startswith("defter")]
        # print(self.imgUrlList)
        self.workerThreadDict = {}

        self.is_fetching = True
        for imageURL in self.imgUrlList[:5]:
            self.create_thread(imageURL)
            self.imgUrlList.remove(imageURL)

            # try:
            #     from urllib.request import urlretrieve
            #     urlretrieve(imageURL, imageSavePath)
            # except HTTPError as e:
            #     print("hata")

    # ---------------------------------------------------------------------
    @Slot(str, str, QPointF, QObject)
    def dThread_finished(self, url, imagePath, scenePos, worker):
        # todo: COK ONEMLİ, İmajlari temp klasore kaydedip sonra actigimizda yok o klasor.
        # dosyayi kaydederken adresleri degistirmek ya da embed etmek mi lazim.
        # acaba ayri bir klasor mu yapsak web images gibisnden
        # her adres icin ayri klasor cok kalabalik olabilir.
        # hatta genel bi downloaded iages klasor.. hani web image diye isimlendirmistik ya.
        # text = self.cScene.activeItem.toHtml().replace(url, imagePath)
        # text = self.cScene.activeItem.toHtml().replace(url, "file:/images/{}".format(os.path.basename(imagePath)))

        # iptal edildi !! -> onemli: text nesnesindeki set_document_url'de de images-html klasoru ekleniyor.
        # img src= direkt adres yazabiliyoruz boylelikle
        text = self.cScene.activeItem.toHtml().replace(url, "{}".format(
            os.path.join("images-html", os.path.basename(imagePath))))
        self.cScene.activeItem.setHtml(text)
        self.cScene.activeItem.update()

        # self.sender().failed.emit()
        self.dthread_clean(worker)
        if self.imgUrlList:
            self.create_thread(self.imgUrlList.pop(0))
        else:
            self.is_fetching = False

    # ---------------------------------------------------------------------
    @Slot(QObject)
    def dthread_clean(self, worker):

        self.workerThreadDict[worker].quit()  # thread
        self.workerThreadDict[worker].deleteLater()  # thread
        worker.deleteLater()  # worker
        del self.workerThreadDict[worker]

        # print("{} active threads".format(len(self.workerThreadDict)))
        self.log(self.tr("{} active threads").format(len(self.workerThreadDict)), 0)

        if not len(self.workerThreadDict):
            self.log(self.tr("All images are succesfully downloaded!"), 1)

    # ---------------------------------------------------------------------
    def clean_download_threads(self):

        # TODO: burasi tam olmadi ..
        # logu if self.fetching icine mi tasisak ya da
        # close_selected_tab icinde is_fetching ifi oluturup oraya mi tasisak.

        if self.is_fetching:
            self.log(self.tr("Cleaning Threads Please Wait..."), 0)
            workers = self.workerThreadDict.keys()
            threads = self.workerThreadDict.values()

            for worker in workers:
                worker.failed.emit(worker)

            count = len(workers)
            while count > 0:
                for thread in threads:
                    if thread.isFinished():
                        count -= 1

    # ---------------------------------------------------------------------
    @Slot()
    def act_resize_text_item_to_fit_view(self):
        yari_ekran_genisligi = self.cView.get_visible_rect().width() / 2
        if self.cScene.activeItem.rect().width() > yari_ekran_genisligi:
            fitRect = QRectF(self.cScene.activeItem._rect)
            # fitRect.setWidth(self.cView.viewport().rect().width())
            fitRect.setWidth(yari_ekran_genisligi)
            self.cScene.activeItem.setRect(fitRect)

    # ---------------------------------------------------------------------
    @Slot()
    def act_web_browser_ac(self):
        """
        ayirdik cunku triggerden True geliyor ve de o da
        web_browser_ac url_as_string parametresine True olarak gidiyordu.
        """
        self.web_browser_ac()

    # ---------------------------------------------------------------------
    def web_browser_ac(self, url_as_string=None):
        """
        sahneden cagriliyor, mousedoubleclickevent icinden
        """

        self.webBrowserDW = DockWidget(self.tr("Web Browser"), self)
        self.webBrowserDW.setAttribute(Qt.WA_DeleteOnClose)
        self.webBrowserDW.setObjectName("webBrowserDockWidget")
        self.addDockWidget(Qt.RightDockWidgetArea, self.webBrowserDW)

        # -- her ada nın cevresine bir onu kaplayici ve margini ayarlanabilir bir cember veya kutu

        base = QWidget(self.webBrowserDW)
        base.setContentsMargins(0, 0, 0, 0)
        self.webBrowserDW.setWidget(base)
        layBase = QVBoxLayout(base)

        scroll = QScrollArea()
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        # scroll.setBackgroundRole(QPalette.Dark)
        self.webBrowserDW.setWidget(scroll)
        # scrollLayout = QVBoxLayout(scroll)

        widget = QDialog(scroll)
        # widget.resize(800, 600)
        # widget.setAttribute(Qt.WA_DeleteOnClose)
        # widget.setWindowTitle(self.tr("Defter: Web Browser"))
        layout = QVBoxLayout()
        layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        widget.setLayout(layout)

        scroll.setWidget(widget)

        webView = QWebEngineView(widget)
        webView.setObjectName("webview")
        webView.settings().setAttribute(QWebEngineSettings.PluginsEnabled, False)

        if not url_as_string:
            url = QUrl("https://google.com")
        else:
            print(url_as_string)
            url = QUrl.fromUserInput(url_as_string)
        if url.isValid():
            webView.load(url)

        adressLay = QHBoxLayout()
        backButton = QToolButton(widget)
        backButton.setText("Back")
        backButton.setIcon(QIcon(':icons/undo.png'))
        backButton.clicked.connect(webView.back)

        forwardButton = QToolButton(widget)
        forwardButton.setText("Forward")
        forwardButton.setIcon(QIcon(':icons/redo.png'))
        # forwardButton.clicked.connect(webView.page().triggerAction(QWebEnginePage.Forward))
        forwardButton.clicked.connect(webView.forward)

        refreshButton = QToolButton(widget)
        refreshButton.setText("Refresh")
        refreshButton.setIcon(QIcon(':icons/refresh.png'))
        refreshButton.clicked.connect(webView.reload)

        lineEdit = QLineEdit(widget)
        lineEdit.setClearButtonEnabled(True)
        # lineEdit.returnPressed.connect(lambda: webPage.load(QUrl(lineEdit.text())))
        lineEdit.returnPressed.connect(lambda: webView.load(QUrl.fromUserInput(lineEdit.text())))
        # webView.page().urlChanged.connect(lambda changed_url: lineEdit.setText(changed_url.toDisplayString()))
        webView.page().urlChanged.connect(lambda changed_url: lineEdit.setText(changed_url.toString()))
        webView.page().titleChanged.connect(widget.setWindowTitle)

        adressLay.addWidget(backButton)
        adressLay.addWidget(forwardButton)
        adressLay.addWidget(refreshButton)
        adressLay.addWidget(lineEdit)
        layout.addLayout(adressLay)
        layout.addWidget(webView)
        # widget.show()

    # ---------------------------------------------------------------------
    @Slot()
    def act_show_as_web_page(self):

        widget = QDialog(self)
        w1 = self.cScene.activeItem.rect().size().toSize().width()
        w2 = self.cView.size().width()
        h1 = self.cScene.activeItem.rect().size().toSize().height()
        h2 = self.cView.size().height()

        widget.setAttribute(Qt.WA_DeleteOnClose)
        widget.setWindowTitle(self.tr("Defter: Show As Web Page"))
        layout = QVBoxLayout()
        widget.setLayout(layout)

        webView = QWebEngineView(widget)
        webView.setObjectName("webview")
        webView.settings().setAttribute(QWebEngineSettings.PluginsEnabled, False)
        # if self.cScene.activeItem.type() == shared.DOSYA_ITEM_TYPE:
        #     webView.load(QUrl.fromLocalFile(self.cScene.activeItem.filePathForSave))
        #     widget.resize(self.cView.size())
        # else:
        #     webView.setHtml(self.cScene.activeItem.toHtml())
        #     widget.resize(min(w1, w2), min(h1, h2))
        webView.setHtml(self.cScene.activeItem.toHtml())
        widget.resize(min(w1, w2), min(h1, h2))
        layout.addWidget(webView)
        widget.show()

    # ---------------------------------------------------------------------
    @Slot()
    def act_convert_to_web_item(self):
        # for item in self.cScene.selectionQueue:
        #     if item.type() == Text.Type:
        #         if not item.isPlainText:
        #             html = item.toHtml()
        #             # pos, rect, arkaPlanRengi, pen, font
        #             webItem = Web(html, item.scenePos(), item.rect(), self.arkaPlanRengi, self._pen, self.currentFont)
        #             undoRedo.undoableAddItem(self.cScene.undoStack, "convert to web item", self.cScene, webItem)

        item = self.cScene.activeItem

        # if item.type() == DosyaNesnesi.Type:
        #     webItem = Web(None, item.filePathForSave, item.scenePos(), 
        #                   item.rect(), self.yaziRengi, self.arkaPlanRengi,
        #                   self._pen,
        #                   self.currentFont)
        # else:
        #     webItem = Web(item.toHtml(), None, item.scenePos(), item.rect(), self.yaziRengi, self.arkaPlanRengi,
        #                   self._pen,
        #                   self.currentFont)

        webItem = Web(item.toHtml(), None, item.scenePos(), item.rect(), 
                      self.cScene.aktifArac.yaziRengi,
                      self.cScene.aktifArac.arkaPlanRengi,
                      self.cScene.aktifArac.kalem,
                      self.cScene.aktifArac.yaziTip)

        undoRedo.undoableAddItem(self.cScene.undoStack, self.tr("convert to web item"), self.cScene, webItem)

    # ---------------------------------------------------------------------
    @Slot()
    def act_convert_to_plain_text(self):

        if self.cScene.selectionQueue:
            yaziNesneleri = []
            for item in self.cScene.selectionQueue:
                if item.type() == shared.TEXT_ITEM_TYPE:
                    yaziNesneleri.append(item)

            if len(yaziNesneleri) > 1:
                self.cScene.undoStack.beginMacro(self.tr("convert to plain text"))
            for item in yaziNesneleri:
                undoRedo.undoableConvertToPlainText(self.cScene.undoStack, self.tr("convert to plain text"), item)
            if len(yaziNesneleri) > 1:
                self.cScene.undoStack.endMacro()

    # ---------------------------------------------------------------------
    @Slot()
    def act_show_image_info(self):
        widget = QDialog(self)
        widget.setAttribute(Qt.WA_DeleteOnClose)
        widget.setWindowTitle(self.tr("Defter: Image info"))
        layout = QVBoxLayout()
        widget.setLayout(layout)

        textEdit = QTextEdit(widget)
        textEdit.setReadOnly(True)
        layout.addWidget(textEdit)
        if self.cScene.activeItem.originalSourceFilePath:
            org_path = self.cScene.activeItem.originalSourceFilePath
        else:
            org_path = self.tr("None: Cropped or pasted image")
        textEdit.append(self.tr(" Original Source Path: {}").format(org_path))
        textEdit.append(self.tr("\n Current Path: {}").format(self.cScene.activeItem.filePathForSave))
        textEdit.append(self.tr("\n isEmbeded: {}").format(self.cScene.activeItem.isEmbeded))

        originalImageSize = QPixmap(self.cScene.activeItem.filePathForDraw).size()

        textEdit.append(self.tr("\n Original Width: {}").format(originalImageSize.width()))
        textEdit.append(self.tr("\n Original Height: {}").format(originalImageSize.height()))

        textEdit.append(self.tr("\n Current Width: {}").format(self.cScene.activeItem._rect.width()))
        textEdit.append(self.tr("\n Current Height: {}").format(self.cScene.activeItem._rect.height()))
        widget.show()

    # ---------------------------------------------------------------------
    @Slot()
    def act_embed_images(self):
        # burda macro basa kondu, sanki asagidaki dongude embed islemi
        # gerceklesmeyebilir gibi dursa da, self.actionEmbedImage , embeded imaj secili degilse, gozukmediginden dolayi.
        # bu arada diyelim ki bir sekilde hic undoableEmbedImage cagrilmadi o zaman makro yine gozukuyor undo stackta!!

        self.lutfen_bekleyin_goster()
        if len(self.cScene.selectionQueue) > 1:
            itemsToEmbed = []

            for item in self.cScene.selectionQueue:
                if item.type() == shared.IMAGE_ITEM_TYPE:
                    if not item.isEmbeded:
                        if os.path.exists(item.filePathForSave):
                            itemsToEmbed.append(item)
                            # undoRedo.undoableEmbedImage(self.cScene.undoStack, self.tr("_embed image"), item)
                        else:
                            self.log(self.tr("Could not embeded! "
                                             "Image's original source path does not exist! : {}")
                                     .format(item.filePathForSave), level=3, toLogOnly=True)

            if itemsToEmbed:
                if len(itemsToEmbed) > 1:
                    self.cScene.undoStack.beginMacro(self.tr("Embed image(s)"))
                    for item in itemsToEmbed:
                        undoRedo.undoableEmbedImage(self.cScene.undoStack, self.tr("_embed image"), item)
                    self.cScene.undoStack.endMacro()

                else:  # tek eleman var demek
                    undoRedo.undoableEmbedImage(self.cScene.undoStack, self.tr("Embed image"), itemsToEmbed[0])
                    self.log(self.tr("Image embeded."), 5000, 1)

            self.log(self.tr("Image(s) embeded."), 5000, 1)

        else:  # 0 olamaz cunku sag clickten geliyor bu komut # kisayol iptal edildi
            item = self.cScene.activeItem
            if not item.isEmbeded:
                if os.path.exists(item.filePathForSave):
                    undoRedo.undoableEmbedImage(self.cScene.undoStack, self.tr("Embed image"), item)
                    self.log(self.tr("Image embeded."), 5000, 1)
                else:
                    self.log(self.tr("Could not embeded! Image's original source path does not exist! {}")
                             .format(item.filePathForSave), 7000, 3)

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_export_image(self):
        # direkt fileDialog cagiriyoruz cunku bu methodu cagiran action,
        # sadece image itema sag tiklaninca gozukuyor.
        succesfulExportCount = 0
        # seciliElemanSayisi = len(self.cScene.selectionQueue)

        if len(self.cScene.selectionQueue) > 1:
            filtre = self.tr("All Files (*)")
            fn = QFileDialog.getSaveFileName(self,
                                             self.tr("Save image(s) as"),
                                             self.sonKlasorDisaAktar,  # hem sonKlasor hem dosya adi
                                             filtre
                                             )

            userPath = fn[0]
            if userPath:
                self.lutfen_bekleyin_goster()
                fileName = os.path.basename(userPath)
                dirToCopy = os.path.dirname(userPath)

                i = 2
                filePathsForSaveSet = set()
                for item in self.cScene.selectionQueue:
                    if item.type() == shared.IMAGE_ITEM_TYPE:
                        if os.path.exists(item.filePathForSave):
                            filePathsForSaveSet.add(item.filePathForSave)

                for filePathForSave in filePathsForSaveSet:
                    # ext = os.path.splitext(item.originalSourceFilePath)[1].lower()
                    ext = os.path.splitext(filePathForSave)[1].lower()
                    path = os.path.join(dirToCopy, "{}-{}{}".format(fileName, i, ext))
                    # shutil.copy2(item.filePathForSave, path)
                    shutil.copy2(filePathForSave, path)
                    # path = os.path.join(dirToCopy, fileName)
                    i += 1
                    succesfulExportCount += 1
        else:
            # embeded olsa da, cesitli durumlar sebebi ile ? imaj bulunmayabilir?
            if not os.path.exists(self.cScene.activeItem.filePathForSave):
                return
            ext = os.path.splitext(self.cScene.activeItem.originalSourceFilePath)[1].lower()
            baseName = os.path.basename(self.cScene.activeItem.originalSourceFilePath)
            filtre = self.tr("*{} files (*{});;All Files (*)".format(ext, ext))
            fn = QFileDialog.getSaveFileName(self,
                                             self.tr("Save image(s) as"),
                                             os.path.join(self.sonKlasorDisaAktar, baseName),
                                             filtre
                                             )
            userPath = fn[0]
            if userPath:
                self.lutfen_bekleyin_goster()
                if not userPath.endswith(ext):
                    userPath = '{}{}'.format(userPath, ext)
                # if self.cScene.activeItem.type() == Image.Type:
                shutil.copy2(self.cScene.activeItem.filePathForSave, userPath)
                succesfulExportCount += 1
                # path = userPath

        self.sonKlasorDisaAktar = os.path.dirname(userPath)
        if succesfulExportCount:
            self.log(self.tr("{} image(s) exported.").format(succesfulExportCount), 5000, 1)
        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_show_video_info(self):
        widget = QDialog(self)
        widget.setAttribute(Qt.WA_DeleteOnClose)
        widget.setWindowTitle(self.tr("Defter: Video info"))
        layout = QVBoxLayout()
        widget.setLayout(layout)

        textEdit = QTextEdit(widget)
        textEdit.setReadOnly(True)
        layout.addWidget(textEdit)
        textEdit.append(self.tr(" Original Source Path: {}").format(self.cScene.activeItem.originalSourceFilePath))
        textEdit.append(self.tr("\n Current Path: {}").format(self.cScene.activeItem.filePathForSave))
        textEdit.append(self.tr("\n isEmbeded: {}").format(self.cScene.activeItem.isEmbeded))

        videoItemNativeSize = self.cScene.activeItem.videoItem.nativeSize()
        videoItemCurrentSize = self.cScene.activeItem.videoItem.size()
        # self.cScene.activeItem._rect.width()

        textEdit.append(self.tr("\n Original Width: {}").format(videoItemNativeSize.width()))
        textEdit.append(self.tr("\n Original Height: {}").format(videoItemNativeSize.height()))

        textEdit.append(self.tr("\n Current Width: {}").format(videoItemCurrentSize.width()))
        textEdit.append(self.tr("\n Current Height: {}").format(videoItemCurrentSize.height()))
        widget.show()

    # ---------------------------------------------------------------------
    @Slot()
    def act_embed_video(self):
        # burda macroyu basa koydum, sanki asagidaki dongude embed islemi
        # gerceklesmeyebilir gibi dursa da, self.actionEmbedImage , embeded imaj secili degilse, gozukmediginden dolayi.
        # bu arada diyelim ki bir sekilde hic undoableEmbedImage cagrilmadi o zaman makro yine gozukuyor undo stackta!!

        # bu embed image ile baya baya ayni, bir ara ortak noktalar ayri bir methodta toplanabilir.
        self.lutfen_bekleyin_goster()
        if len(self.cScene.selectionQueue) > 1:
            itemsToEmbed = []

            # self.cScene.undoStack.beginMacro(self.tr("Embed video(s)"))
            for item in self.cScene.selectionQueue:
                if item.type() == shared.VIDEO_ITEM_TYPE:
                    if not item.isEmbeded:
                        if os.path.exists(item.filePathForSave):
                            itemsToEmbed.append(item)
                            # undoRedo.undoableEmbedVideo(self.cScene.undoStack, self.tr("_embed video"), item)
                    else:
                        self.log(self.tr("Could not embeded! "
                                         "Video's original source path does not exist! : {}")
                                 .format(item.filePathForSave), level=3, toLogOnly=True)

            if itemsToEmbed:
                if len(itemsToEmbed) > 1:
                    self.cScene.undoStack.beginMacro(self.tr("Embed video(s)"))
                    for item in itemsToEmbed:
                        undoRedo.undoableEmbedVideo(self.cScene.undoStack, self.tr("_embed video"), item)
                    self.cScene.undoStack.endMacro()

                else:  # tek eleman var demek
                    undoRedo.undoableEmbedVideo(self.cScene.undoStack, self.tr("Embed video"), itemsToEmbed[0])
                    self.log("Video embeded.", 5000, 1)

            self.log(self.tr("Video(s) embeded."), 5000, 1)

        else:  # 0 olamaz cunku sag clickten geliyor bu komut
            item = self.cScene.activeItem
            if not item.isEmbeded:
                if os.path.exists(item.filePathForSave):
                    undoRedo.undoableEmbedVideo(self.cScene.undoStack, self.tr("_embed video"), item)
                    self.log(self.tr("Video embeded."), 5000, 1)
                else:
                    self.log(self.tr("Could not embeded! Video's original source path does not exist! {}")
                             .format(item.filePathForSave), 7000, 3)

            # self.cScene.undoStack.endMacro()
            # self.log("Video(s) embeded.", 5000, 1)

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_export_video(self):
        # direkt fileDialog cagiriyoruz cunku bu methodu cagiran action,
        succesfulExportCount = 0
        # sadece video itema sag tiklaninca gozukuyor.

        if len(self.cScene.selectionQueue) > 1:
            filtre = self.tr("All Files (*)")
            fn = QFileDialog.getSaveFileName(self,
                                             self.tr("Save video(s) as"),
                                             self.sonKlasorDisaAktar,  # hem sonklasor hem dosyaadi
                                             filtre
                                             )

            userPath = fn[0]
            if userPath:
                self.lutfen_bekleyin_goster()
                # fileName = os.path.splitext(os.path.basename(userPath))[0]
                fileName = os.path.basename(userPath)
                dirToCopy = os.path.dirname(userPath)

                i = 2
                filePathsForSaveSet = set()
                for item in self.cScene.selectionQueue:
                    if item.type() == shared.VIDEO_ITEM_TYPE:
                        if os.path.exists(item.filePathForSave):
                            filePathsForSaveSet.add(item.filePathForSave)

                for filePathForSave in filePathsForSaveSet:
                    # ext = os.path.splitext(item.originalSourceFilePath)[1].lower()
                    ext = os.path.splitext(filePathForSave)[1].lower()
                    path = os.path.join(dirToCopy, "{}-{}{}".format(fileName, i, ext))
                    # shutil.copy2(item.filePathForSave, path)
                    shutil.copy2(filePathForSave, path)
                    # path = os.path.join(dirToCopy, fileName)
                    i += 1
                    succesfulExportCount += 1

        else:
            # embeded olsa da, cesitli durumlar sebebi ile ? imaj bulunmayabilir?
            if not os.path.exists(self.cScene.activeItem.filePathForSave):
                return

            ext = os.path.splitext(self.cScene.activeItem.originalSourceFilePath)[1].lower()
            baseName = os.path.basename(self.cScene.activeItem.originalSourceFilePath)
            filtre = self.tr("*{} files (*{});;All Files (*)".format(ext, ext))
            fn = QFileDialog.getSaveFileName(self,
                                             self.tr("Save video(s) as"),
                                             os.path.join(self.sonKlasorDisaAktar, baseName),
                                             filtre
                                             )

            userPath = fn[0]
            if userPath:
                self.lutfen_bekleyin_goster()
                if not userPath.endswith(ext):
                    userPath = '{}{}'.format(userPath, ext)
                # if self.cScene.activeItem.type() == VideoItem.Type:
                shutil.copy2(self.cScene.activeItem.filePathForSave, userPath)
                succesfulExportCount += 1
                # path = userPath

        self.sonKlasorDisaAktar = os.path.dirname(userPath)
        if succesfulExportCount:
            self.log(self.tr("{} Video(s) exported.").format(succesfulExportCount), 5000, 1)

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_embed_dosya(self):
        # burda macroyu basa koydum, sanki asagidaki dongude embed islemi
        # gerceklesmeyebilir gibi dursa da, self.actionEmbedImage , embeded imaj secili degilse, gozukmediginden dolayi.
        # bu arada diyelim ki bir sekilde hic undoableEmbedImage cagrilmadi o zaman makro yine gozukuyor undo stackta!!

        # bu embed image ile baya baya ayni, bir ara ortak noktalar ayri bir methodta toplanabilir.
        self.lutfen_bekleyin_goster()
        if len(self.cScene.selectionQueue) > 1:
            itemsToEmbed = []

            # self.cScene.undoStack.beginMacro(self.tr("Embed file(s)"))
            for item in self.cScene.selectionQueue:
                if item.type() == shared.DOSYA_ITEM_TYPE:
                    if not item.isEmbeded:
                        if os.path.exists(item.filePathForSave):
                            itemsToEmbed.append(item)
                            # undoRedo.undoableEmbedFile(self.cScene.undoStack, self.tr("_embed file"), item)
                    else:
                        self.log(self.tr("Could not embeded! "
                                         "File's original source path does not exist! : {}")
                                 .format(item.filePathForSave), level=3, toLogOnly=True)

            if itemsToEmbed:
                if len(itemsToEmbed) > 1:
                    self.cScene.undoStack.beginMacro(self.tr("Embed file(s)"))
                    for item in itemsToEmbed:
                        undoRedo.undoableEmbedFile(self.cScene.undoStack, self.tr("_embed file"), item)
                    self.cScene.undoStack.endMacro()

                else:  # tek eleman var demek
                    undoRedo.undoableEmbedFile(self.cScene.undoStack, self.tr("Embed file"), itemsToEmbed[0])
                    self.log("File embeded.", 5000, 1)

            self.log(self.tr("File(s) embeded."), 5000, 1)

        else:  # 0 olamaz cunku sag clickten geliyor bu komut
            item = self.cScene.activeItem
            if not item.isEmbeded:
                if os.path.exists(item.filePathForSave):
                    undoRedo.undoableEmbedFile(self.cScene.undoStack, self.tr("_embed file"), item)
                    self.log(self.tr("File embeded."), 5000, 1)
                else:
                    self.log(self.tr("Could not embeded! File's original source path does not exist! {}")
                             .format(item.filePathForSave), 7000, 3)

            # self.cScene.undoStack.endMacro()
            # self.log("Video(s) embeded.", 5000, 1)

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_export_dosya(self):
        # direkt fileDialog cagiriyoruz cunku bu methodu cagiran action,
        succesfulExportCount = 0
        # sadece file itema sag tiklaninca gozukuyor.
        if len(self.cScene.selectionQueue) > 1:
            filtre = self.tr("All Files (*)")
            fn = QFileDialog.getSaveFileName(self,
                                             self.tr("Save file(s) as"),
                                             self.sonKlasorDisaAktar,  # hem sonklasor hem dosyaadi
                                             filtre
                                             )

            userPath = fn[0]
            if userPath:
                self.lutfen_bekleyin_goster()
                # fileName = os.path.splitext(os.path.basename(userPath))[0]
                fileName = os.path.basename(userPath)
                dirToCopy = os.path.dirname(userPath)

                i = 2
                filePathsForSaveSet = set()
                for item in self.cScene.selectionQueue:
                    if item.type() == shared.DOSYA_ITEM_TYPE:
                        if os.path.exists(item.filePathForSave):
                            filePathsForSaveSet.add(item.filePathForSave)

                for filePathForSave in filePathsForSaveSet:
                    # ext = os.path.splitext(item.originalSourceFilePath)[1].lower()
                    ext = os.path.splitext(filePathForSave)[1].lower()
                    path = os.path.join(dirToCopy, "{}-{}{}".format(fileName, i, ext))
                    # shutil.copy2(item.filePathForSave, path)
                    shutil.copy2(filePathForSave, path)
                    # path = os.path.join(dirToCopy, fileName)
                    i += 1
                    succesfulExportCount += 1

        else:
            # embeded olsa da, cesitli durumlar sebebi ile ? imaj bulunmayabilir?
            if not os.path.exists(self.cScene.activeItem.filePathForSave):
                return

            ext = os.path.splitext(self.cScene.activeItem.originalSourceFilePath)[1].lower()
            baseName = os.path.basename(self.cScene.activeItem.originalSourceFilePath)
            filtre = self.tr("*{} files (*{});;All Files (*)".format(ext, ext))
            fn = QFileDialog.getSaveFileName(self,
                                             self.tr("Save file(s) as"),
                                             os.path.join(self.sonKlasorDisaAktar, baseName),
                                             filtre
                                             )

            userPath = fn[0]
            if userPath:
                self.lutfen_bekleyin_goster()
                if not userPath.endswith(ext):
                    userPath = '{}{}'.format(userPath, ext)
                # if self.cScene.activeItem.type() == VideoItem.Type:
                shutil.copy2(self.cScene.activeItem.filePathForSave, userPath)
                succesfulExportCount += 1
                # path = userPath

        self.sonKlasorDisaAktar = os.path.dirname(userPath)
        if succesfulExportCount:
            self.log(self.tr("{} File(s) exported.").format(succesfulExportCount), 5000, 1)

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_show_dosya_info(self):
        widget = QDialog(self)
        widget.setAttribute(Qt.WA_DeleteOnClose)
        widget.setWindowTitle(self.tr("Defter: File info"))
        layout = QVBoxLayout()
        widget.setLayout(layout)

        textEdit = QTextEdit(widget)
        textEdit.setReadOnly(True)
        layout.addWidget(textEdit)
        textEdit.append(self.tr(" Original Source Path: {}").format(self.cScene.activeItem.originalSourceFilePath))
        textEdit.append(self.tr("\n Current Path: {}").format(self.cScene.activeItem.filePathForSave))
        textEdit.append(self.tr("\n isEmbeded: {}").format(self.cScene.activeItem.isEmbeded))

        st = os.stat(self.cScene.activeItem.filePathForSave)
        textEdit.append(self.tr("\n Size: {} Mb").format(st.st_size / 1024 / 1024))
        widget.show()

    # ---------------------------------------------------------------------
    def item_selected(self, item):

        self.cScene.selectionQueue.append(item)

        # if item.command():
        #     command = item.command()["command"]
        # else:
        #     pass

        self.degistir_yazi_rengi_ikonu(item.yaziRengi, nesne_arkaplan_ikonu_guncelle=False)
        self.degistir_cizgi_rengi_ikonu(item.pen().color(), nesne_arkaplan_ikonu_guncelle=False)
        self.degistir_nesne_arkaplan_rengi_ikonu(item.arkaPlanRengi, item.yaziRengi, item.pen().color())
        self.change_text_size_spinbox_value(item.font().pointSize())
        self.change_font_combobox_value(item.font())
        self.change_transform_box_values(item)
        self.yazi_hizalama_degisti()
        self.karakter_bicimi_degisti()
        if self.cizgiTipiCBox.isVisible():
            self.change_line_style_options(item._pen)
        item.update_resize_handles(force=True)

    # ---------------------------------------------------------------------
    def item_deselected(self, item):
        self.cScene.selectionQueue.remove(item)

    # ---------------------------------------------------------------------
    def line_item_selected(self, item):

        self.cScene.selectionQueue.append(item)

        # if item.command():
        #     command = item.command()["command"]
        # else:
        #     pass

        self.degistir_cizgi_rengi_ikonu(item._pen.color(), nesne_arkaplan_ikonu_guncelle=True)
        # self.itemRotationSBox_tbar.setValue(item.angle())
        # rotation change_transform_box_values icinde de var.
        self.change_transform_box_values(item)
        if self.cizgiTipiCBox.isVisible():
            self.change_line_style_options(item._pen)

    # ---------------------------------------------------------------------
    def path_item_selected(self, item):

        self.cScene.selectionQueue.append(item)

        # if item.command():
        #     command = item.command()["command"]
        # else:
        #     pass

        self.degistir_yazi_rengi_ikonu(item.yaziRengi, nesne_arkaplan_ikonu_guncelle=False)
        self.degistir_cizgi_rengi_ikonu(item._pen.color(), nesne_arkaplan_ikonu_guncelle=False)
        self.degistir_nesne_arkaplan_rengi_ikonu(item.arkaPlanRengi, item.yaziRengi, item._pen.color())
        self.change_text_size_spinbox_value(item.font().pointSize())
        self.change_font_combobox_value(item.font())
        self.itemRotationSBox_tbar.setValue(item.rotation())
        self.itemRotationSBox_nesnedw.setValue(item.rotation())
        self.yazi_hizalama_degisti()
        self.karakter_bicimi_degisti()
        if self.cizgiTipiCBox.isVisible():
            self.change_line_style_options(item._pen)

    # ---------------------------------------------------------------------
    # @Slot(QGraphicsTextItem)
    def text_item_selected(self, item):

        self.cScene.selectionQueue.append(item)

        # not ; cunku deselect edince de gonderiyor, eger kullanmazsak ters isliyor mekanizma
        # if not item.isSelected():

        # if item.command():
        #     command = item.command()["command"]
        # else:
        #     pass

        # color = item.defaultTextColor()
        self.degistir_yazi_rengi_ikonu(item.yaziRengi, nesne_arkaplan_ikonu_guncelle=False)
        self.degistir_cizgi_rengi_ikonu(item._pen.color(), nesne_arkaplan_ikonu_guncelle=False)
        self.degistir_nesne_arkaplan_rengi_ikonu(item.arkaPlanRengi, item.yaziRengi, item._pen.color())
        self.change_text_size_spinbox_value(item.font().pointSize())
        self.change_font_combobox_value(item.font())
        self.itemRotationSBox_tbar.setValue(item.rotation())
        self.itemRotationSBox_nesnedw.setValue(item.rotation())
        self.yazi_hizalama_degisti()
        self.karakter_bicimi_degisti()
        if self.cizgiTipiCBox.isVisible():
            self.change_line_style_options(item._pen)
        item.update_resize_handles(force=True)

    # ---------------------------------------------------------------------
    def group_item_selected(self, group):

        self.cScene.selectionQueue.append(group)
        # self.degistir_yazi_rengi_ikonu(group.cizgiRengi)
        # self.degistir_nesne_arkaplan_rengi_ikonu(group.arkaPlanRengi)

        self.itemRotationSBox_tbar.setValue(group.rotation())
        self.itemRotationSBox_nesnedw.setValue(group.rotation())
        if self.cizgiTipiCBox.isVisible():
            self.change_line_style_options(group._pen)

    # ---------------------------------------------------------------------
    def group_item_deselected(self, group):

        self.cScene.selectionQueue.remove(group)

    # ---------------------------------------------------------------------
    @Slot(bool)
    def act_toggle_always_on_top(self, isChecked):

        defaultFlags = self.windowFlags()

        if isChecked:
            # self.windowFlag = self.windowFlags()
            self.setWindowFlags(Qt.WindowStaysOnTopHint | defaultFlags)
            self.setVisible(True)
        else:
            # TODO: ^ bunu bi test et
            self.setWindowFlags(defaultFlags ^ Qt.WindowStaysOnTopHint)
            # self.windowFlag = None
            self.setVisible(True)

    # ---------------------------------------------------------------------
    def olustur_log_viewer_dialog(self):

        self.logViewerDialog = QDialog(self)
        # self.logViewerDialog.setAttribute(Qt.WA_DeleteOnClose)
        self.logViewerDialog.setWindowTitle(self.tr("Defter: Log"))
        layout = QVBoxLayout()
        self.logViewerDialog.setLayout(layout)

        self.logViewer = QTextEdit(self.logViewerDialog)
        self.logViewer.setReadOnly(True)
        # self.logViewer.setText("")
        layout.addWidget(self.logViewer)
        # self.logViewerDialog.show()

    # ---------------------------------------------------------------------
    @Slot()
    def act_toggle_log_viewer_dialog(self):
        # self.logCounter = 0
        # self.actionToggleLogViewer.setText(self.tr('Log'))
        if self.logViewerDialog.isVisible():
            self.logViewerDialog.hide()
        else:
            self.logViewerDialog.show()

    # ---------------------------------------------------------------------
    # def log(self, txt, msecs=5000, level=0, status=True):
    def log(self, txt, msecs=5000, level=0, toStatusBarOnly=False, toLogOnly=False, dialog=False):

        if not toLogOnly:
            self._statusBar.showMessage(txt, msecs)
            if toStatusBarOnly:
                return

        color = QColor(50, 50, 50)  # level:0  info = black
        lvl = ""

        if level == 1:  # success = green
            color = QColor(0, 120, 0)
        elif level == 2:  # warning = yellow
            color = QColor(150, 150, 0)
            lvl = self.tr("!! Warning : ")
        elif level == 3:  # error = red
            lvl = self.tr("!! Error : ")
            color = QColor(150, 0, 0)

        # PySide.QtGui.QTextEdit.insertHtml(text)
        # PySide.QtGui.QTextEdit.insertPlainText(text)
        cursor = self.logViewer.textCursor()
        # fmt = cursor.charFormat()
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        # cursor.mergeCharFormat(fmt)
        cursor.setCharFormat(fmt)
        self.logViewer.setTextCursor(cursor)

        t = time.strftime("%H:%M:%S")
        self.logViewer.append("%s :  %s%s" % (t, lvl, txt))
        self.logViewer.moveCursor(QTextCursor.End)
        # self.logCounter += 1
        # if self.splitterMain.sizes()[1] == 0:
        #     self.actionToggleLogViewer.setText(self.tr('Log (%s)' % self.logCounter))
        if dialog:
            QMessageBox.warning(self, 'Defter', txt)

    # ---------------------------------------------------------------------
    def html_kayit_klasor_adresi_sec(self, tekSayfaMi):

        fDialog = QFileDialog()
        # fDialog.setFileMode(QFileDialog.Directory)
        fDialog.setFileMode(QFileDialog.AnyFile)
        # fDialog.setOption(QFileDialog.ShowDirsOnly, True)
        fDialog.setOption(QFileDialog.DontUseNativeDialog, True)
        fDialog.setOption(QFileDialog.DontUseCustomDirectoryIcons, True)

        fDialog.setFilter(fDialog.filter() | QDir.Hidden)
        # fDialog.setAcceptMode(QFileDialog.AcceptOpen)
        fDialog.setAcceptMode(QFileDialog.AcceptSave)

        # uzanti eklendi mi kontrolune ihtiyac kalmiyor
        # fDialog.setDefaultSuffix('html')
        # filtre = ([self.tr("HTML Files (*.html)")])
        # fDialog.setNameFilters(filtre)
        # fDialog.selectNameFilter(filtre)

        fDialog.setDirectory(self.sonKlasorHTML)
        if tekSayfaMi:
            fDialog.setWindowTitle(self.tr("Export Page as HTML"))
        else:
            fDialog.setWindowTitle(self.tr("Export Document as HTML"))

        lay = fDialog.layout()

        aciklama = self.tr("Copy all the linked end embeded files with the HTML file")
        dosyalarKopyalansinMiCBox = QCheckBox(aciklama, fDialog)
        dosyalarKopyalansinMiCBox.setStyleSheet("QCheckBox{ background: #ee5;}")
        dosyalarKopyalansinMiCBox.setChecked(True)
        wAd0 = lay.itemAtPosition(2, 0).widget()
        wAd1 = lay.itemAtPosition(2, 1).widget()
        wAd2 = lay.itemAtPosition(2, 2).widget()

        wTip0 = lay.itemAtPosition(3, 0).widget()
        wTip1 = lay.itemAtPosition(3, 1).widget()
        wTip2 = lay.itemAtPosition(3, 2).widget()
        # wTip2.hide()
        lay.addWidget(dosyalarKopyalansinMiCBox, 2, 1)
        lay.replaceWidget(wAd1, dosyalarKopyalansinMiCBox)
        lay.addWidget(wAd0, 3, 0)
        lay.addWidget(wAd1, 3, 1)
        lay.addWidget(wAd2, 3, 2)
        lay.addWidget(wTip0, 4, 0)
        lay.addWidget(wTip1, 4, 1)
        lay.addWidget(wTip2, 3, 2, 2, 1)

        # fView = fDialog.findChild(QListView, 'listView')
        # # to make it possible to select multiple directories:
        # if fView:
        #     fView.setSelectionMode(QAbstractItemView.MultiSelection)
        # fTreeView = fDialog.findChild(QTreeView)
        # if fTreeView:
        #     fTreeView.setSelectionMode(QAbstractItemView.MultiSelection)

        if fDialog.exec() == QDialog.Accepted:
            # liste icinde tek adres, files desek de
            paths = fDialog.selectedFiles()
            return paths, dosyalarKopyalansinMiCBox.isChecked()
        else:
            return None, dosyalarKopyalansinMiCBox.isChecked()

    # ---------------------------------------------------------------------
    def _icerik_div_olustur(self, sayfa, def_dosyasi_icine_kaydet, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):
        sayfa_icerik_div = ""
        if def_dosyasi_icine_kaydet:
            # nesnelerde, if None kontrolu ile def dosyasi icine kaydettigimizi anliyoruz
            html_klasor_kayit_adres = None
        for item in sayfa.scene.items():
            div = item.html_dive_cevir(html_klasor_kayit_adres, dosya_kopyalaniyor_mu)
            if not div:
                # print(item)
                continue
            sayfa_icerik_div += div
        return sayfa_icerik_div

    # ---------------------------------------------------------------------
    def sayfa_html_olustur(self, sayfa, html_klasor_kayit_adres, tekSayfaMi, def_dosyasi_icine_kaydet,
                           dosya_kopyalaniyor_mu):

        if tekSayfaMi:
            nav_style = ""
            nav_html = ""
            margin_left = ""
        else:
            nav_style = f"""
            nav{{
              height: 100%;
              width: 100px;
              position: fixed;
              z-index: 1;
              top: 0;
              left: 0;
              background-color: #f5f5f5;
              overflow-x: hidden;
              padding-top: 16px;
              border-right: 1px solid rgba(82,82,82,0.5);
            }}
            nav a {{
                margin-bottom:0.7em;
                height:auto;
                background-color: #fff;
                padding: 4px 4px 4px 6px;
                text-decoration: none;
                font-size: 0.9em;
                color: #2e3a44;
                display: block;
            }}
            nav a:hover {{
              color: #2a6ea7;
              background-color: #e1ffdd;
            }}
            """
            nav_html = f"""
             <nav>
                {self._nav_sayfa_linkleri}
            </nav>
            """
            margin_left = "margin-left:100px;"

        sayfa.scene.setSceneRect(sayfa.scene.sceneRect().united(sayfa.scene.itemsBoundingRect()))
        if sayfa.view.backgroundImagePath:
            if def_dosyasi_icine_kaydet:
                arkaplan_resim_adres = os.path.join("images", os.path.basename(sayfa.view.backgroundImagePath))
            else:  # disari kayit
                if sayfa.view.backgroundImagePathIsEmbeded:
                    arkaplan_resim_adres = os.path.join("images", os.path.basename(sayfa.view.backgroundImagePath))
                else:
                    if dosya_kopyalaniyor_mu:
                        arkaplan_resim_adres = os.path.join(html_klasor_kayit_adres, "images",
                                                            os.path.basename(sayfa.view.backgroundImagePath))
                    else:
                        arkaplan_resim_adres = sayfa.view.backgroundImagePath

            arkaplan_resim = f"background-image:url({arkaplan_resim_adres});\n"
        else:
            arkaplan_resim = ""
        arkaplan_renk = f"rgba{sayfa.view.backgroundBrush().color().toTuple()}"

        icerik_div = self._icerik_div_olustur(sayfa, def_dosyasi_icine_kaydet,
                                              html_klasor_kayit_adres,
                                              dosya_kopyalaniyor_mu)

        if sayfa.adi[0] == "★":
            sayfa_adi = sayfa.adi[2:]
        else:
            sayfa_adi = sayfa.adi

        html = f"""
        <html>
        <head>\n
            <title>{self.cModel.fileName} - {sayfa_adi}</title>
            <style>
                body {{
                background: {arkaplan_renk};
                margin:0;
                padding:0;
                    }}
                div {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    align-items: center;}}
                    {nav_style}
                main{{
                position:absolute;
                    display:block;
                    background: {arkaplan_renk};
                    {arkaplan_resim}
                    background-repeat:no-repeat;
                    background-position: center center;
                    width:{sayfa.scene.sceneRect().width()};
                    height:{sayfa.scene.sceneRect().height()};
                    {margin_left}
                }}
            </style>
        </head>
        <body>
            {nav_html}
            <main>{icerik_div}</main>
        </body>
        </html>
        """

        return html

    # ---------------------------------------------------------------------
    def html_sayfa_kaydet(self, html, html_dosya_kayit_adres):

        with open(html_dosya_kayit_adres, mode="w", encoding="utf-8") as f:
            f.write(html)
            f.flush()

    # ---------------------------------------------------------------------
    def _ic_sayfalari_gezin(self, sayfa, kayit_klasor, def_dosyasi_icine_kaydet, oteleme):

        for ic_sayfa in sayfa.ic_sayfalar():
            if ic_sayfa.adi[0] == "★":
                sayfa_adi = f"{ic_sayfa.adi[2:]}.html"
            else:
                sayfa_adi = f"{ic_sayfa.adi}.html"
            html_dosya_kayit_adres = os.path.join(kayit_klasor, sayfa_adi)

            if def_dosyasi_icine_kaydet:
                self._nav_sayfa_linkleri += f'<a style="padding-left:{oteleme}px;"' \
                                            f' href="{sayfa_adi}"> {sayfa_adi}</a>\n'
            else:
                self._nav_sayfa_linkleri += f'<a style="padding-left:{oteleme}px;"' \
                                            f' href="{html_dosya_kayit_adres}"> {sayfa_adi}</a>\n'

            self._html_sayfa_listesi.append((ic_sayfa, html_dosya_kayit_adres))

            # sayfalarDict[sayfa.adi]["ic_sayfalar"] ={"{}".format(ic_sayfa.adi): ic_sayfa_sceneDict}
            if ic_sayfa.ic_sayfa_var_mi():
                self._ic_sayfalari_gezin(ic_sayfa, kayit_klasor, def_dosyasi_icine_kaydet, oteleme + 12)

    # ---------------------------------------------------------------------
    @Slot()
    def act_export_document_as_html(self, html_klasor_kayit_adres=None):
        def_dosyasi_icine_kaydet = True
        dosyalar_kopyalansin_mi = False
        if not html_klasor_kayit_adres:
            def_dosyasi_icine_kaydet = False
            fn, dosyalar_kopyalansin_mi = self.html_kayit_klasor_adresi_sec(tekSayfaMi=False)
            if not fn:
                return
            else:
                html_klasor_kayit_adres = fn[0]
                self.sonKlasorHTML = os.path.dirname(html_klasor_kayit_adres)
                os.makedirs(html_klasor_kayit_adres, exist_ok=True)
        self.lutfen_bekleyin_goster()
        if dosyalar_kopyalansin_mi:
            for sayfa in self.cModel.sayfalar():
                self.dosyalari_kopyala(sayfa, html_klasor_kayit_adres)

        oteleme = 0
        self._nav_sayfa_linkleri = ""
        self._html_sayfa_listesi = []

        self._ic_sayfalari_gezin(self.cModel.kokSayfa, html_klasor_kayit_adres, def_dosyasi_icine_kaydet, oteleme + 12)

        # TODO: eski ismi degismis sayfalardan veya silinmis sayfalardan kalan html dosyalarini temizle
        for sayfa, html_dosya_kayit_adres, in self._html_sayfa_listesi:
            html = self.sayfa_html_olustur(sayfa, html_klasor_kayit_adres, tekSayfaMi=False,
                                           def_dosyasi_icine_kaydet=def_dosyasi_icine_kaydet,
                                           dosya_kopyalaniyor_mu=dosyalar_kopyalansin_mi)

            self.html_sayfa_kaydet(html, html_dosya_kayit_adres)

        del self._nav_sayfa_linkleri
        del self._html_sayfa_listesi

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    @Slot()
    def act_export_page_as_html(self):
        fn, dosyalar_kopyalansin_mi = self.html_kayit_klasor_adresi_sec(tekSayfaMi=True)
        if fn:
            self.lutfen_bekleyin_goster()
            html_klasor_kayit_adres = fn[0]
            self.sonKlasorHTML = os.path.dirname(html_klasor_kayit_adres)
            os.makedirs(html_klasor_kayit_adres, exist_ok=True)
            if dosyalar_kopyalansin_mi:
                self.dosyalari_kopyala(self.cModel.enSonAktifSayfa, html_klasor_kayit_adres)
            sayfa = self.cModel.enSonAktifSayfa
            html = self.sayfa_html_olustur(sayfa, html_klasor_kayit_adres,
                                           tekSayfaMi=True, def_dosyasi_icine_kaydet=False,
                                           dosya_kopyalaniyor_mu=dosyalar_kopyalansin_mi)
            if sayfa.adi[0] == "★":
                sayfa_adi = f"{sayfa.adi[2:]}.html"
            else:
                sayfa_adi = f"{sayfa.adi}.html"
            self.html_sayfa_kaydet(html, os.path.join(html_klasor_kayit_adres, sayfa_adi))
            self.lutfen_bekleyin_gizle()

        else:
            return

    # ---------------------------------------------------------------------
    def dosyalari_kopyala(self, sayfa, hedef_klasor):

        try:
            # !! deprecated distutils.dir_util.copy_tree - python3.10
            # !! distutils.dir_util.copy_tree(self.cModel.tempDirPath, tempDirPath)
            # once acik sahne temp klasorunu tamamen kopyaliyoruz yeni bir temp klasore
            # TODO: dirs_exist_ok python 3.8 gerektiriyor.
            # shutil.copytree(self.cModel.tempDirPath, hedef_klasor, dirs_exist_ok=True)
            images_klasoru = os.path.join(self.cModel.tempDirPath, "images")
            if os.path.exists(images_klasoru):
                shutil.copytree(images_klasoru, os.path.join(hedef_klasor, "images"), dirs_exist_ok=True)

            images_klasoru = os.path.join(self.cModel.tempDirPath, "images-html")
            if os.path.exists(images_klasoru):
                shutil.copytree(images_klasoru, os.path.join(hedef_klasor, "images-html"), dirs_exist_ok=True)

            files_klasoru = os.path.join(self.cModel.tempDirPath, "files")
            if os.path.exists(files_klasoru):
                shutil.copytree(files_klasoru, os.path.join(hedef_klasor, "files"), dirs_exist_ok=True)

            videos_klasoru = os.path.join(self.cModel.tempDirPath, "videos")
            if os.path.exists(videos_klasoru):
                shutil.copytree(videos_klasoru, os.path.join(hedef_klasor, "videos"), dirs_exist_ok=True)

        except Exception as e:
            print(e)

        try:
            if sayfa.view.backgroundImagePath and not sayfa.view.backgroundImagePathIsEmbeded:
                kopyalanacak_adres = os.path.join(hedef_klasor, "images",
                                                  os.path.basename(sayfa.view.backgroundImagePath))

                hedef_nesne_tipi_klasoru = os.path.join(hedef_klasor, "images")
                if not os.path.exists(hedef_nesne_tipi_klasoru):
                    os.makedirs(hedef_nesne_tipi_klasoru, exist_ok=True)

                shutil.copy2(sayfa.view.backgroundImagePath, kopyalanacak_adres)

            for nesne in sayfa.scene.items():
                if nesne.type() == shared.IMAGE_ITEM_TYPE:
                    ic_klasor = "images"
                elif nesne.type() == shared.DOSYA_ITEM_TYPE:
                    ic_klasor = "files"
                elif nesne.type() == shared.VIDEO_ITEM_TYPE:
                    ic_klasor = "videos"
                else:
                    continue

                if not nesne.isEmbeded:  # gomulu ise zaten yukarda kopyalanıyor
                    if os.path.exists(nesne.filePathForSave):
                        # self.yeniImagePath = nesne.scene().get_unique_path_for_embeded_image(
                        #     os.path.basename(nesne.filePathForSave))
                        # klasor yoksa hata veriyor copy2
                        hedef_nesne_tipi_klasoru = os.path.join(hedef_klasor, ic_klasor)
                        if not os.path.exists(hedef_nesne_tipi_klasoru):
                            os.makedirs(hedef_nesne_tipi_klasoru, exist_ok=True)
                        kopyalanacak_adres = os.path.join(hedef_nesne_tipi_klasoru,
                                                          os.path.basename(nesne.filePathForSave))
                        shutil.copy2(nesne.filePathForSave, kopyalanacak_adres)
                    else:
                        # if not filecmp.cmp(imgPath, yeniImgPath, shallow=True):
                        print("nesne yok", nesne.filePathForSave)
                        pass
        except Exception as e:
            print(e)

        # if os.path.exists(yeniImgPath):
        #     if not filecmp.cmp(imgPath, yeniImgPath, shallow=True):
        #         # print("ayni isimde dosya var, icerik farkli")
        #         try:
        #             shutil.copy2(imgPath, yeniImgPath)
        #             # print(imgPath)
        #             # print(yeniImgPath)
        #         except Exception as e:
        #             self.log(str(e), level=3)

    # ---------------------------------------------------------------------
    def _get_printer(self):
        if not self.printer:
            # printer = QPrinter(QPrinter.HighResolution)
            # printer = QPrinter(QPrinter.PrinterResolution)
            # printer = QPrinter(QPrinter.ScreenResolution)
            self.printer = QPrinter()
            self.printer.setPageSize(QPageSize(QPageSize.A4))
            pLayout = self.printer.pageLayout()
            pLayout.setUnits(pLayout.Millimeter)
            pLayout.setPageSize(QPageSize(QPageSize.A4))
            # self.printer.setPageLayout(QPageSize(QPageSize.A4))
            self.printer.setPageLayout(pLayout)
            self.printer.setPageOrientation(QPageLayout.Portrait)
            # printer.setOutputFormat(QPrinter.PdfFormat)
            # printer.setOutputFileName("deneme.pdf")
            # return printer

    # ---------------------------------------------------------------------
    def act_yazici_sayfa_kenar_cizdir(self):
        self.cView.baskiRectler = []

        if self.baskiSinirGBox.isChecked():
            if self.radioSayfaSigdir.isChecked():

                basilacakRect = self.cScene.itemsBoundingRect()
                self.cView.baskiRectler.append(basilacakRect)

            else:  # genislik
                kagitPozisyonBoyutRect = self.printer.pageLayout().paintRectPixels(self.printer.resolution())
                basilacakRect = self.cScene.itemsBoundingRect()
                toplamBaskiYuksekligi = basilacakRect.height()
                baski_kagit_genislik_orani = basilacakRect.width() / kagitPozisyonBoyutRect.width()
                oranlanmis_basilacakRect_yukseklik = kagitPozisyonBoyutRect.height() * baski_kagit_genislik_orani
                basilacakRect.setHeight(oranlanmis_basilacakRect_yukseklik)
                # print(kagitPozisyonBoyutRect)

                self.cView.baskiRectler.append(basilacakRect)
                while toplamBaskiYuksekligi > 0:
                    toplamBaskiYuksekligi -= oranlanmis_basilacakRect_yukseklik
                    if toplamBaskiYuksekligi > 0:
                        sonrakiRect = QRectF(basilacakRect)
                        sonrakiRect.moveTop(basilacakRect.top() + oranlanmis_basilacakRect_yukseklik)
                        self.cView.baskiRectler.append(sonrakiRect)
        self.cView.update()

    # ---------------------------------------------------------------------
    def _paint_fit_page(self, painter, printer, sahne, basilacakRect):
        eskiRect = sahne.sceneRect()
        # sinyal slotlarla bu bool degerini tasimak yerine bu sekilde tercih edildi.
        if self.pDialog.cboxAsViewed.isChecked():
            sahne.setSceneRect(self.cView.mapToScene(basilacakRect.toRect()).boundingRect())
            kagitPozisyonBoyutRect = printer.pageLayout().paintRectPixels(printer.resolution())
            self.cView.render(painter, QRectF(kagitPozisyonBoyutRect),
                              self.cView.mapFromScene(basilacakRect.toRect()).boundingRect())
        else:
            sahne.setSceneRect(basilacakRect)
            sahne.render(painter)
        sahne.setSceneRect(eskiRect)

    # ---------------------------------------------------------------------
    def _paint_fit_width(self, painter, printer, sahne, basilacakRect):
        """
        // print the upper half of the viewport into the lower.
        // half of the page.
        QRect viewport = view.viewport()->rect();
        view.render(&painter,
                    QRectF(0, printer.height() / 2,
                           printer.width(), printer.height() / 2),
                    viewport.adjusted(0, 0, 0, -viewport.height() / 2));
        """
        eskiRect = sahne.sceneRect()
        sahne.setSceneRect(basilacakRect)
        # sayfa.view.centerOn(basilacakRect.center())
        # sayfa.view.ensureVisible(basilacakRect, xMargin=50, yMargin=50)
        # DeprecationWarning: QPrinter.pageRect() const is deprecated
        # kagitPozisyonBoyutRect = printer.pageRect()
        kagitPozisyonBoyutRect = printer.pageLayout().paintRectPixels(printer.resolution())
        # pageRect = printer.pageLayout().fullRect()
        # pageRect = printer.pageLayout().paintRect()
        # pageRect.moveTopLeft(basilacakRect.topLeft().toPoint())
        # basilacakRect.moveTopLeft(pageRect.topLeft())
        toplamBaskiYuksekligi = basilacakRect.height()
        # sigdirma algoritmasi 
        # basilacak karenin genisliginin kagit genisligine oranina gore
        # basilacak karenin yuksekligi tekrar ayarlaniyor
        baski_kagit_genislik_orani = basilacakRect.width() / kagitPozisyonBoyutRect.width()
        oranlanmis_basilacakRect_yukseklik = kagitPozisyonBoyutRect.height() * baski_kagit_genislik_orani
        basilacakRect.setHeight(oranlanmis_basilacakRect_yukseklik)

        while toplamBaskiYuksekligi > 0:

            # sinyal slotlarla bu bool degerini tasimak yerine bu sekilde tercih edildi.
            if self.pDialog.cboxAsViewed.isChecked():
                sahne.setSceneRect(self.cView.mapToScene(basilacakRect.toRect()).boundingRect())
                self.cView.render(painter, QRectF(kagitPozisyonBoyutRect),
                                  self.cView.mapFromScene(basilacakRect.toRect()).boundingRect())
            else:
                sahne.setSceneRect(basilacakRect)
                sahne.render(painter, kagitPozisyonBoyutRect, basilacakRect)
            toplamBaskiYuksekligi -= oranlanmis_basilacakRect_yukseklik
            basilacakRect.moveTop(basilacakRect.top() + oranlanmis_basilacakRect_yukseklik)
            if toplamBaskiYuksekligi > 0:
                printer.newPage()

        sahne.setSceneRect(eskiRect)

    # ---------------------------------------------------------------------
    def _paint_document(self, printer):
        # self.textEdit.print_(printer)
        p = QPainter()

        if not p.begin(printer):
            print("hata")
        p.setRenderHint(QPainter.Antialiasing)
        # TODO: bu baya yavaş olabiliyor,
        self.lutfen_bekleyin_goster()

        if self.pDialog.subOptionsRadioBtnGroup.checkedButton() == self.pDialog.radioFitPage:
            for sayfa in self.cModel.sayfalar():
                self._paint_fit_page(p, printer, sayfa.scene, sayfa.scene.itemsBoundingRect())
                printer.newPage()
        elif self.pDialog.subOptionsRadioBtnGroup.checkedButton() == self.pDialog.radioFitWidth:
            for sayfa in self.cModel.sayfalar():
                self._paint_fit_width(p, printer, sayfa.scene, sayfa.scene.itemsBoundingRect())
                printer.newPage()

        p.end()

        self.lutfen_bekleyin_gizle()

    # ---------------------------------------------------------------------
    def _paint_page(self, printer):
        # self.textEdit.print_(printer)
        p = QPainter()

        if not p.begin(printer):
            print("hata")
        p.setRenderHint(QPainter.Antialiasing)
        # itemsBRect = self.cScene.itemsBoundingRect().translated(0,0)
        # itemsBRect = self.cScene.itemsBoundingRect()
        # self.cScene.render(p, itemsBRect)

        if self.pDialog.subOptionsRadioBtnGroup.checkedButton() == self.pDialog.radioFitPage:
            self._paint_fit_page(p, printer, self.cScene, self.cScene.itemsBoundingRect())
        elif self.pDialog.subOptionsRadioBtnGroup.checkedButton() == self.pDialog.radioFitWidth:
            self._paint_fit_width(p, printer, self.cScene, self.cScene.itemsBoundingRect())

        p.end()

    # ---------------------------------------------------------------------
    def _paint_view(self, printer):
        # self.textEdit.print_(printer)
        p = QPainter()

        if not p.begin(printer):
            print("hata")
        p.setRenderHint(QPainter.Antialiasing)
        # p.scale(.3, .3)

        """
        // print the upper half of the viewport into the lower.
        // half of the page.
        QRect viewport = view.viewport()->rect();
        view.render(&painter,
                    QRectF(0, printer.height() / 2,
                           printer.width(), printer.height() / 2),
                    viewport.adjusted(0, 0, 0, -viewport.height() / 2));
        """

        # bunda 1 pixel adjust var, get_visible_rect ile alakasi
        # oldugunu hatirlatmasi icin yorum olarak eklendi
        # basilacakRect = self.cView.get_visible_rect()
        basilacakRect = self.cView.mapToScene(self.cView.viewport().rect()).boundingRect()

        if self.pDialog.subOptionsRadioBtnGroup.checkedButton() == self.pDialog.radioFitPage:
            self._paint_fit_page(p, printer, self.cScene, basilacakRect)

        elif self.pDialog.subOptionsRadioBtnGroup.checkedButton() == self.pDialog.radioFitWidth:
            self._paint_fit_width(p, printer, self.cScene, basilacakRect)

        p.end()

    # ---------------------------------------------------------------------
    def _paint_text_item_content(self, printer):

        # self.textEdit.print_(printer)

        if len(self.cScene.selectionQueue) == 1:
            if self.cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                p = QPainter()
                if not p.begin(printer):
                    print("hata")
                p.setRenderHint(QPainter.Antialiasing)
                # self.cScene.activeItem.doc.print_(printer)
                # rect = printer.pageRect()
                # self.cScene.activeItem.doc.setTextWidth(rect.width())
                self.cScene.activeItem.doc.drawContents(p)
                # printer.newPage()
                # self.cScene.activeItem.doc.drawContents( p)
                p.end()

    # ---------------------------------------------------------------------
    def _paint_selection(self, printer):

        # self.textEdit.print_(printer)
        p = QPainter()

        if not p.begin(printer):
            print("hata")
        p.setRenderHint(QPainter.Antialiasing)
        # itemsBRect = self.cScene.itemsBoundingRect().translated(0,0)
        # itemsBRect = self.cScene.itemsBoundingRect()
        # self.cScene.render(p, itemsBRect)

        basilacakRect = QRectF()
        for item in self.cScene.selectionQueue:
            # if item.isVisible():
            basilacakRect = basilacakRect.united(item.boundingRect().translated(item.pos()))
            # yeniRect = yeniRect.united(item.boundingRect())

        if self.pDialog.subOptionsRadioBtnGroup.checkedButton() == self.pDialog.radioFitPage:
            self._paint_fit_page(p, printer, self.cScene, basilacakRect)

        elif self.pDialog.subOptionsRadioBtnGroup.checkedButton() == self.pDialog.radioFitWidth:
            self._paint_fit_width(p, printer, self.cScene, basilacakRect)

    # # ---------------------------------------------------------------------
    # def _paint_selection___(self, printer):
    #     eskiSceneRect = self.cScene.sceneRect()
    #
    #     yeniRect = QRectF()
    #     for item in self.cScene.selectionQueue:
    #         # if item.isVisible():
    #         # yeniRect = yeniRect.united(item.boundingRect().translated(item.pos()))
    #         yeniRect = yeniRect.united(item.boundingRect())
    #
    #     self.cScene.setSceneRect(yeniRect)
    #     image = QImage(yeniRect.size().toSize(), QImage.Format_ARGB32)
    #     image.fill(Qt.transparent)
    #
    #     painter = QPainter()
    #     if not painter.begin(image):
    #         print("hata")
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     self.cScene.render(painter)
    #
    #     painter.end()
    #
    #     painter = QPainter()
    #     if not painter.begin(printer):
    #         print("hata")
    #     painter.setRenderHint(QPainter.Antialiasing)
    #
    #     size = yeniRect.size()
    #     viewport = painter.viewport()
    #
    #     # size.scale(QSizeF(viewport.size()), Qt.KeepAspectRatio)
    #     # painter.setViewport(viewport.x(), viewport.y(), size.width(), size.height())
    #     # painter.setWindow(yeniRect.toRect())
    #     painter.drawPixmap(0, 0, QPixmap(image))
    #     painter.end()

    # # ---------------------------------------------------------------------
    # def _paint_selection__(self, printer):
    #
    #     yeniRect = QRectF()
    #     for item in self.cScene.selectionQueue:
    #         # if item.isVisible():
    #         # yeniRect = yeniRect.united(item.boundingRect().translated(item.pos()))
    #         yeniRect = yeniRect.united(item.boundingRect())
    #
    #     painter = QPainter()
    #     if not painter.begin(printer):
    #         print("hata")
    #     painter.setRenderHint(QPainter.Antialiasing)
    #
    #     size = yeniRect.size()
    #     viewport = painter.viewport()
    #
    #     size.scale(QSizeF(viewport.size()), Qt.KeepAspectRatio)
    #     painter.setViewport(viewport.x(), viewport.y(), size.width(), size.height())
    #     painter.setWindow(yeniRect.toRect())
    #     # painter.drawPixmap(0,0,pixPrint)
    #     self.cScene.render(painter, self.cScene.activeItem._rect)
    #     painter.end()

    # # ---------------------------------------------------------------------
    # def _paint_selection____(self, printer):
    #
    #     # TODO: sayfalar cok olunca RAM yetmiyor !! DİKKAT !!!
    #
    #     yeniRect = QRectF()
    #     for item in self.cScene.selectionQueue:
    #         # if item.isVisible():
    #         # yeniRect = yeniRect.united(item.boundingRect().translated(item.pos()))
    #         yeniRect = yeniRect.united(item.boundingRect())
    #
    #     painter = QPainter()
    #
    #     if not painter.begin(printer):
    #         print("hata")
    #         painter.setRenderHint(QPainter.Antialiasing)
    #     # self.cView.render(p)
    #
    #     # yeniRect.adjust(0,0,yeniRect.width(),yeniRect.height())
    #
    #     # pRect = printer.paperRect()
    #
    #     pageRect = printer.pageRect()
    #     xscale = pageRect.width() / yeniRect.width()
    #     yscale = pageRect.height() / yeniRect.height()
    #     scale = min(xscale, yscale)
    #
    #     painter.translate(printer.paperRect().x() + printer.pageRect().width() / 2,
    #                       printer.paperRect().y() + printer.pageRect().height() / 2)
    #
    #     painter.scale(scale, scale)
    #     painter.translate(-self.cScene.sceneRect().width() / 2, -self.cScene.sceneRect().height() / 2)
    #     self.cScene.render(painter)
    #     # nh = yeniRect.height()
    #     # ph = pageRect.height()
    #     # print(self.cScene.sceneRect())
    #     # print(yeniRect)
    #     # print(nh, ph, nh > ph)
    #     # if nh <= ph:
    #     #     # printRect = QRectF(pRect.x(), pRect.y(), pRect.width(), pRect.height())
    #     #     printRect = QRectF(yeniRect.x(), yeniRect.y(), yeniRect.width(), yeniRect.height())
    #     #     # printRect = printRect.translated(0,0)
    #     #     self.cScene.render(painter, printRect)
    #     #     # self.cScene.render(p, yeniRect)
    #     # else:
    #     #     while nh > ph:
    #     #         self.cScene.render(painter, QRectF(yeniRect.x(), yeniRect.y(), yeniRect.width(), nh))
    #     #         printer.yeniPage()
    #     #         nh = nh - ph
    #     #         print(nh , ph , nh <= ph)
    #     #
    #     painter.end()
    #
    #     """
    #     QRect viewport = view.viewport()->rect();
    #         view.render(&painter,
    #         QRectF(0, printer.height() / 2,
    #                printer.width(), printer.height() / 2),
    #         viewport.adjusted(0, 0, 0, -viewport.height() / 2));
    #
    #         """

    # document

    # ---------------------------------------------------------------------
    def _change_preview_mode(self, mode):
        # TODO:

        if mode == "document":
            self.pDialog.preview.paintRequested.connect(self._paint_document)

        elif mode == "page":
            self.pDialog.preview.paintRequested.connect(self._paint_page)

        elif mode == "view":
            self.pDialog.preview.paintRequested.connect(self._paint_view)

        elif mode == "selection":
            self.pDialog.preview.paintRequested.connect(self._paint_selection)

        elif mode == "content":
            self.pDialog.preview.paintRequested.connect(self._paint_text_item_content)

        self.pDialog.preview.updatePreview()

    # ---------------------------------------------------------------------
    def act_print_document(self):
        # printer = self._get_printer()

        # printer.setResolution(QPrinter.ScreenResolution)
        self.printer.setOutputFormat(QPrinter.NativeFormat)
        # "document" "page" "view" "selection" "content"
        self.pDialog = PrintPreviewDialog(self.printer, "document", self)
        self.pDialog.paintRequested.connect(self._paint_document)
        self.pDialog.paintRequestTypeChanged.connect(self._change_preview_mode)
        if self.radioSayfaSigdir.isChecked():
            self.pDialog.radioFitPage.setChecked(True)
        else:
            self.pDialog.radioFitWidth.setChecked(True)
        # pDialog.exec()
        self.pDialog.show()

        # TODO bi sekilde self.pDialog none yapmak lazim.. sinyal falan mi gondersek close veya
        # print edince.. sonra da burdan =None desek, bi cesit dialog implementation

        # preview = QPrintPreviewDialog(printer, self)
        # preview.paintRequested.connect(self._paint_document)
        # # preview.exec()
        # preview.exec()

    # ---------------------------------------------------------------------
    def act_export_selected_text_item_content_as_pdf(self):

        # printer = self._get_printer()
        self.printer.setOutputFormat(QPrinter.PdfFormat)
        self.pDialog = PrintPreviewDialog(self.printer, "content", self)
        self.pDialog.paintRequested.connect(self._paint_text_item_content)
        self.pDialog.paintRequestTypeChanged.connect(self._change_preview_mode)
        if self.radioSayfaSigdir.isChecked():
            self.pDialog.radioFitPage.setChecked(True)
        else:
            self.pDialog.radioFitWidth.setChecked(True)
        # pDialog.exec()
        self.pDialog.show()

    # ---------------------------------------------------------------------
    def act_print_selected_text_item_content(self):
        # printer = self._get_printer()

        # printer.setResolution(QPrinter.ScreenResolution)
        self.printer.setOutputFormat(QPrinter.NativeFormat)
        # "document"  "page" "view" "selection" "content"
        self.pDialog = PrintPreviewDialog(self.printer, "content", self)
        self.pDialog.paintRequested.connect(self._paint_text_item_content)
        self.pDialog.paintRequestTypeChanged.connect(self._change_preview_mode)
        if self.radioSayfaSigdir.isChecked():
            self.pDialog.radioFitPage.setChecked(True)
        else:
            self.pDialog.radioFitWidth.setChecked(True)
        # pDialog.exec()
        self.pDialog.show()

    # ---------------------------------------------------------------------
    def act_export_page_as_image(self):
        # sayfa = self.sayfalarDWTreeView.get_current_sayfa()
        # baseName = sayfa.adi
        fn = QFileDialog.getSaveFileName(self,
                                         self.tr('Save Image as'),
                                         self.sonKlasorDisaAktar,  # hem sonklasor hem dosyaadi
                                         self.supportedImageFormats
                                         )
        path = fn[0]
        if path:
            if not path.endswith(".jpg"):
                path = '{}.{}'.format(path, "jpg")

            # image = QImage(self.cSecne.itemsBoundingRect().toRect(), QImage.Format_ARGB32_Premultiplied)
            image = QImage(self.cScene.itemsBoundingRect().size().toSize(), QImage.Format_ARGB32)
            image = QImage(self.cView.viewport().size(), QImage.Format_ARGB32)
            image.fill(Qt.transparent)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            self.cView.render(painter)
            painter.end()
            image.save(path)

            self.log(self.tr("Page succesfully exported as image. {}".format(path)), 7000)

            self.sonKlasorDisaAktar = os.path.dirname(path)

            # if self.printer.outputFileName():
            #     self.preview.print()

    # ---------------------------------------------------------------------
    @Slot()
    def act_ekran_goruntusu_tam_ekran(self):
        self.hide()
        QApplication.processEvents()
        QTimer.singleShot(10, lambda: self.ekran_goruntusu_cek(QApplication.primaryScreen().geometry()))
        # self.ekran_goruntusu_cek(QApplication.primaryScreen().geometry())
        self.show()

    # ---------------------------------------------------------------------
    @Slot()
    def act_ekran_goruntusu_secim_cm_on(self):
        self.hide()
        self.shot_selection = TamEkranWidget_CM_On()
        QApplication.setOverrideCursor(Qt.CrossCursor)
        self.shot_selection.rubberBandReleased.connect(self.bekle_ekran_goruntusu_cek)
        self.shot_selection.esc_key_pressed.connect(self.kapat_ekran_goruntusu)
        # self.shot_selection.activateWindow()
        # self.shot_selection.raise_()
        # self.shot_selection.showFullScreen()

    # ---------------------------------------------------------------------
    @Slot()
    def act_ekran_goruntusu_secim_cm_off(self):
        self.hide()
        self.shot_selection = TamEkranWidget_CM_Off()
        QApplication.setOverrideCursor(Qt.CrossCursor)
        self.shot_selection.rubberBandReleased.connect(self.bekle_ekran_goruntusu_cek)
        self.shot_selection.esc_key_pressed.connect(self.kapat_ekran_goruntusu)
        # self.shot_selection.activateWindow()
        # self.shot_selection.raise_()
        # self.shot_selection.showFullScreen()

    # ---------------------------------------------------------------------
    @Slot(QRect)
    def bekle_ekran_goruntusu_cek(self, geo):
        # time.sleep(0.2)
        # QTimer.singleShot(300, lambda: self.ekran_goruntusu_cek(geo))
        if not geo.isEmpty():
            self.ekran_goruntusu_cek(geo)

        # QTimer.singleShot(10, lambda geo=geo: self.ekran_goruntusu_cek(geo))
        self.kapat_ekran_goruntusu()

    # ---------------------------------------------------------------------
    @Slot()
    def kapat_ekran_goruntusu(self):
        self.shot_selection.close()
        self.shot_selection.deleteLater()
        self.shot_selection = None
        # del self.shot_selection
        QApplication.restoreOverrideCursor()
        self.show()

    # ---------------------------------------------------------------------
    def ekran_goruntusu_cek(self, geo):

        geo = geo.adjusted(2, 2, -2, -2)

        x, y, w, h = geo.x(), geo.y(), geo.width(), geo.height()

        # iki ekran varsa
        # QPixmap screenshot = QPixmap::grabWindow(desktop->winId(), 0, 0, desktop->width(), desktop->height());

        # self.originalPixmap = QPixmap.grabWindow(QApplication.desktop().winId(), *self.get_screenshot_frame())
        # self.originalPixmap = QPixmap.grabWindow(QApplication.desktop().winId(), x, y, w, h)

        # TODO: pixmap grabwindow deprecated
        # self.originalPixmap = QPixmap.grabWindow(QApplication.desktop().winId(), x, y, w, h)
        # self.originalPixmap = QScreen.grabWindow(QApplication.desktop().winId(), x, y, w, h)

        screen = QApplication.primaryScreen()
        if screen:
            originalPixmap = screen.grabWindow(0, x, y, w, h)

            # sahneye direk yerlestir
            if not originalPixmap.isNull():

                # sahneye direk yerlestir
                # imageSavePath = self.cScene.get_unique_path_for_embeded_image("screenshot.jpg")
                # fmt = "jpg"
                # originalPixmap.save(imageSavePath, fmt, quality=100)
                # 
                # self.log("Screenshot saved as: {}".format(imageSavePath))
                # 
                # rect = QRectF(originalPixmap.rect())
                # imageItem = Image(imageSavePath, self.get_mouse_scene_pos(), rect, 
                #                   self.cScene.ResimAraci.yaziRengi, 
                #                   self.cScene.ResimAraci.arkaPlanRengi,
                #                   self.cScene.ResimAraci.kalem, 
                #                   self.cScene.ResimAraci.yaziTipi)
                # 
                # imageItem.isEmbeded = True
                # 
                # self.increase_zvalue(imageItem)
                # undoRedo.undoableAddItem(self.cScene.undoStack, self.tr("_screenshot"), self.cScene, imageItem)
                # imageItem.reload_image_after_scale()
                # self.cScene.unite_with_scene_rect(imageItem.sceneBoundingRect())

                # panoya kopyala
                eskiMimeData = self.clipboard.mimeData()

                mimeData = QMimeData()
                if eskiMimeData.data('scene/items'):
                    mimeData.setData('scene/items', eskiMimeData.data('scene/items'))
                if eskiMimeData.hasText():
                    mimeData.setText(eskiMimeData.text())
                if eskiMimeData.hasHtml():
                    mimeData.setHtml(eskiMimeData.html())
                if eskiMimeData.hasUrls():
                    mimeData.setUrls(eskiMimeData.urls())
                if eskiMimeData.hasColor():
                    mimeData.setImageData(eskiMimeData.colorData())
                # if eskiMimeData.hasImage():
                #     mimeData.setImageData(eskiMimeData.imageData())

                mimeData.setImageData(originalPixmap.toImage())
                self.clipboard.setMimeData(mimeData)

    # ---------------------------------------------------------------------
    @Slot()
    def on_ekranGoruntusuMenu_about_to_show(self):
        pass

        # if platform.system() == "Linux":
        #     from PySide2.QtX11Extras import QX11Info
        # 
        #     try:
        #         if QX11Info.isCompositingManagerRunning():
        #             self.actionSecimEkranGoruntusuAlCmOn.setEnabled(True)
        #             self.actionSecimEkranGoruntusuAlCmOff.setEnabled(False)
        # 
        #         else:
        #             self.actionSecimEkranGoruntusuAlCmOn.setEnabled(False)
        #             self.actionSecimEkranGoruntusuAlCmOff.setEnabled(True)
        # 
        #             self.log(self.tr("You should install or enable a compositing manager "
        #                      "to be able to use disabled options in screenshot menu!"))
        #     except AttributeError:
        #         pass

    # ---------------------------------------------------------------------
    def arsivleme_programi_adres_belirle(self):

        self.arsivleme_programi_adres = "_python_zipfile"

        sistem = platform.system()
        if sistem in ["Linux", "Darwin"]:
            if shutil.which("7z"):
                self.arsivleme_programi_adres = "7z"
            elif shutil.which("zip"):
                self.arsivleme_programi_adres = "zip"
        elif sistem == "Windows":
            if shutil.which("7z.exe"):
                self.arsivleme_programi_adres = "7z.exe"
            elif shutil.which("7z.exe", path=os.path.join(os.environ["ProgramW6432"], "7-Zip")):
                self.arsivleme_programi_adres = os.path.join(os.environ["ProgramW6432"], "7-Zip", "7z.exe")
            elif shutil.which("7z.exe", path=os.path.join(os.environ["ProgramFiles(x86)"], "7-Zip")):
                self.arsivleme_programi_adres = os.path.join(os.environ["ProgramFiles(x86)"], "7-Zip", "7z.exe")
            elif shutil.which("zip.exe"):
                self.arsivleme_programi_adres = "zip.exe"
        # else:  # baska bir os ise
        #     # belki "zip" denenebilir.
        #     self.arsivleme_programi_adres = "_python_zipfile"
        #     return

    # ---------------------------------------------------------------------
    def ziple(self, program_adres, zip_dosya_tam_adres, kaynak_klasor_tam_adres):
        eski_dir = os.getcwd()
        try:
            if program_adres.startswith("7"):
                subprocess.call(
                    [program_adres, "u", zip_dosya_tam_adres, kaynak_klasor_tam_adres + os.sep + "*", "-mx0", "-tzip"],
                    stdout=subprocess.DEVNULL)  # stderr=subprocess.DEVNULL

            elif program_adres.startswith("z"):
                # subprocess.call([program_adres, "-FS0ryo", zip_dosya_tam_adres, "./*"])
                subprocess.call([program_adres, "-FS0ryoq", zip_dosya_tam_adres, "." + os.sep + "*"])
                os.chdir(eski_dir)

            elif program_adres.startswith("_"):
                self._python_zipfile_ile_ziple(zip_dosya_tam_adres, kaynak_klasor_tam_adres)

        except Exception as e:
            print(e)
            self._python_zipfile_ile_ziple(zip_dosya_tam_adres, kaynak_klasor_tam_adres)
            # if not os.getcwd() == eski_dir:
            os.chdir(eski_dir)

    # ---------------------------------------------------------------------
    def _python_zipfile_ile_ziple(self, zip_dosya_tam_adres, kaynak_klasor_tam_adres):
        # bunun yerine asagidaki zipfile tercih edildi.
        # cunku sıkıstırma oranı secebiliyoruz
        # shutil.make_archive(base_name=zippedFolderSavePath, format="zip", root_dir=tempDirPath)
        # shutil.make_archive ziplenmis dosya sonuna .zip ekliyor, ####.def.zip oluyor
        # os.rename("{}.zip".format(zippedFolderSavePath), zippedFolderSavePath)

        # kaynak_klasor kendisi haric sadece icini kaydediyoruz.
        len_kaynak_klasor = len(kaynak_klasor_tam_adres)
        with zipfile.ZipFile(zip_dosya_tam_adres, "w", zipfile.ZIP_STORED) as zipf:
            for root, dirs, files in os.walk(kaynak_klasor_tam_adres):
                # !! Olasi bos klasorleri eklememeyi tercih ettik !!
                #
                for dosya_adi in files:
                    kaynak_dosya_tam_adres = os.path.join(root, dosya_adi)
                    dosya_zip_icindeki_adres = kaynak_dosya_tam_adres[len_kaynak_klasor:]
                    zipf.write(kaynak_dosya_tam_adres, dosya_zip_icindeki_adres)


# ---------------------------------------------------------------------
def calistir():
    prog = QApplication(sys.argv)
    prog.setWindowIcon(QIcon(":icons/defter.png"))
    # if > win7 icin fusion, win 10 icin bakilabilir belki win kalabilir
    # "macintosh" var osx icin
    # linux icin "gtk"
    prog.setStyle("fusion")

    loc = QLocale.system().name()
    print(loc)
    loc = "tr_TR"
    from PySide6.QtCore import QTranslator

    qtTranslator = QTranslator(prog)
    # dosya_adi = "defter_" + loc+".qm"
    dosya_adi = "defter_" + loc
    # dosya_adresi = os.path.join(DEFTER_SCRIPT_PATH, dosya_adi)
    # print(dosya_adresi)
    # if qtTranslator.load(dosya_adresi):
    # if qtTranslator.load(dosya_adi,os.path.dirname(__file__)):

    # pencere = DefterAnaPencere()

    if qtTranslator.load(dosya_adi):
        prog.installTranslator(qtTranslator)
        print(qtTranslator.isEmpty())

    # pencere translatordan sonra olusturmak lazım
    # yoksa bir event meselesi var onunla ilgilenmke lazım
    # program açıkken dil degistirmek icin de aynısı..
    # Guncelleme: Şimdi pencereyi once de olusturabiliyoruz..
    # o yuzden iptal ettik alt satiri,
    # TODO: su anda yine bozuk :)
    pencere = DefterAnaPencere()

    # pencere.show()
    # burda pencere.show() demiyoruz, DefterAnaPencere().__init__ icinde show var.
    # initten cikmadan bazi islemlerden once show cagirmak gerekiyor.  (visible view rect sceneRect e atayabilmek icin)
    sys.exit(prog.exec())


# ---------------------------------------------------------------------
if __name__ == "__main__":
    calistir()
