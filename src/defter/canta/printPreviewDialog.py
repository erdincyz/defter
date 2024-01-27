# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '21/Oct/2017'
__author__ = 'Erdinç Yılmaz'

import os

from PySide6.QtCore import Qt, Slot, Signal, QSettings, QSize, QLocale
from PySide6.QtGui import QIcon, QKeySequence, QDoubleValidator, QIntValidator, QActionGroup, QAction, \
    QPageLayout
from PySide6.QtPrintSupport import QPrintPreviewWidget, QPrinter, QPrintDialog, QPageSetupDialog
from PySide6.QtWidgets import QVBoxLayout, QToolBar, QMainWindow, QLineEdit, QLabel, \
    QSizePolicy, QComboBox, QWidget, QFormLayout, QDockWidget, QPushButton, QHBoxLayout, QButtonGroup, \
    QRadioButton, QGroupBox, QCheckBox, QFileDialog, QApplication

from . import shared

from . import icons_rc


########################################################################
class ZoomValidator(QDoubleValidator):

    # ---------------------------------------------------------------------
    def __init__(self, bottom, top, decimals, parent=None):
        super(ZoomValidator, self).__init__(bottom, top, decimals, parent)

    # ---------------------------------------------------------------------
    def validate(self, text, pos):
        replacePercent = False
        if text.endswith('%'):
            text = text[:len(text) - 1]
            replacePercent = True

        state = QDoubleValidator.validate(self, text, pos)
        if replacePercent:
            text += '%'
        num_size = 4
        if state == QDoubleValidator.State.Intermediate:
            idx = text.find("{}".format(QLocale.system().decimalPoint()))
            if (idx == -1 and len(text) > num_size) or (idx != -1 and idx > num_size):
                return QDoubleValidator.State.Invalid

        # print(state)
        return state


# ########################################################################
# class LineEdit(QLineEdit):
#
#     # ---------------------------------------------------------------------
#     def __init__(self, parent=None):
#         super(LineEdit, self).__init__(parent)
#         self.setContextMenuPolicy(Qt.NoContextMenu)
#         self.returnPressed.connect(self.act_return_pressed)
#         self.originalText = ""
#
#     # ---------------------------------------------------------------------
#     def act_return_pressed(self):
#         self.originalText = self.text()
#
#     # ---------------------------------------------------------------------
#     def focusInEvent(self, QFocusEvent):
#         self.originalText = self.text()
#         QLineEdit.focusInEvent(self, QFocusEvent)
#
#     # ---------------------------------------------------------------------
#     def focusOutEvent(self, QFocusEvent):
#         if self.isModified() and not self.hasAcceptableInput():
#             self.setText(self.originalText)
#         QLineEdit.focusOutEvent(self, QFocusEvent)


########################################################################
class PrintPreviewDialog(QMainWindow):
    """
    custom print preivew dialog
    """

    paintRequested = Signal(QPrinter)
    previewChanged = Signal()
    paintRequestTypeChanged = Signal(str)

    # main window kullanip sonra setWindowModality

    # ---------------------------------------------------------------------
    def __init__(self, printer, yazdirmaAlaniTipi, parent=None):
        super(PrintPreviewDialog, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # self.setWindowModality(Qt.WindowModal)
        # self.setWindowModality(Qt.ApplicationModal)

        # self.accepted.connect(self.yaz_ayarlar)

        self.printer = printer
        self.printDialog = None

        self.setGeometry(600, 150, 700, 800)

        self.olustur_ayarlar()
        self.oku_arayuz_ayarlari()

        self.create_preview_widget(printer)
        self.create_tool_bar()
        self.create_options_dock_widget(yazdirmaAlaniTipi)

        title = self.tr("Defter: Print Preview")
        if printer.docName():
            title = "{}: {}".format(title, printer.docName())
        self.setWindowTitle(title)

        if not printer.isValid():
            pass

            """#if defined(Q_OS_WIN) || defined(Q_OS_MAC)
                || printer->outputFormat() != QPrinter::NativeFormat
                #endif
            )
                pageSetupAction->setEnabled(false);"""
        self.preview.setFocus()

    # ---------------------------------------------------------------------
    def closeEvent(self, QCloseEvent):
        self.yaz_ayarlar()
        super(PrintPreviewDialog, self).closeEvent(QCloseEvent)

    # ---------------------------------------------------------------------
    def create_preview_widget(self, printer):
        centralWidget = QWidget(self)
        centralWidget.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout(centralWidget)  # no need to set layout if we give it a parent

        self.preview = QPrintPreviewWidget(printer, centralWidget)
        # preview.fitToWidth()
        # self.preview.fitInView()

        # self.preview.setFont(QFont('Sans', 9, QFont.Bold))

        # self.preview.setSinglePageViewMode()
        # self.preview.setViewMode(QPrintPreviewWidget.SinglePageView)

        # self.preview.paintRequested.connect(lambda: self.paint_requested(printer))
        self.preview.paintRequested.connect(lambda prntr: self.paintRequested.emit(prntr))
        self.preview.previewChanged.connect(self.act_preview_changed)

        self.setCentralWidget(centralWidget)
        layout.addWidget(self.preview)

    # ---------------------------------------------------------------------
    def create_options_dock_widget(self, yazdirmaAlaniTipi):
        self.optionsDW = QDockWidget(self)

        self.optionsDW.setWindowTitle(self.tr("Print Options"))
        self.optionsDW.setObjectName("printOptionsDockWidget")
        self.optionsDW.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.optionsDW.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                                   QDockWidget.DockWidgetFeature.DockWidgetClosable |
                                   # QDockWidget.DockWidgetFeature.DockWidgetVerticalTitleBar|
                                   QDockWidget.DockWidgetFeature.DockWidgetFloatable
                                   )

        baseWidget = QWidget(self.optionsDW)
        baseLayout = QVBoxLayout(baseWidget)

        radioGBox = QGroupBox(baseWidget)
        radioGBox.setFlat(True)
        # radioGBox.setTitle("radio")
        radioGBoxLayout = QVBoxLayout(radioGBox)

        self.radioBtnGroup = QButtonGroup(radioGBox)
        self.radioDocument = QRadioButton(self.tr("Document"), radioGBox)
        self.radioPage = QRadioButton(self.tr("Page"), radioGBox)
        self.radioView = QRadioButton(self.tr("Current View"), radioGBox)
        self.radioSelection = QRadioButton(self.tr("Selection"), radioGBox)
        self.radioSelection.setEnabled(False)
        self.radioContent = QRadioButton(self.tr("Content"), radioGBox)
        self.radioContent.setEnabled(False)
        self.radioBtnGroup.addButton(self.radioDocument)
        self.radioBtnGroup.addButton(self.radioPage)
        self.radioBtnGroup.addButton(self.radioView)
        self.radioBtnGroup.addButton(self.radioSelection)
        self.radioBtnGroup.addButton(self.radioContent)

        radioGBoxLayout.addWidget(self.radioDocument)
        radioGBoxLayout.addWidget(self.radioPage)
        radioGBoxLayout.addWidget(self.radioView)
        radioGBoxLayout.addWidget(self.radioSelection)
        radioGBoxLayout.addWidget(self.radioContent)

        if yazdirmaAlaniTipi == "document":
            self.radioDocument.setChecked(True)
        elif yazdirmaAlaniTipi == "page":
            self.radioPage.setChecked(True)
        elif yazdirmaAlaniTipi == "view":
            self.radioView.setChecked(True)
        elif yazdirmaAlaniTipi == "selection":
            self.radioSelection.setChecked(True)
        elif yazdirmaAlaniTipi == "content":
            self.radioContent.setChecked(True)

        if self.parent().cScene.selectionQueue:
            self.radioSelection.setEnabled(True)
            if self.parent().cScene.activeItem.type() == shared.TEXT_ITEM_TYPE:
                self.radioContent.setEnabled(True)

        self.radioBtnGroup.buttonClicked.connect(self.act_radio_button_group_clicked)

        # ---------------------------------------------------------------------
        # options widgets

        self.cboxAsViewed = QCheckBox(self.tr("As viewed"), baseWidget)
        self.cboxAsViewed.toggled.connect(self.act_as_viewed_cbox_toggled)

        subOptionsGBox = QGroupBox(baseWidget)
        subOptionsGBox.setFlat(True)
        # optionsGBox.setTitle("options")
        subOptionsGBoxLayout = QVBoxLayout(subOptionsGBox)

        self.subOptionsRadioBtnGroup = QButtonGroup(subOptionsGBox)

        self.radioFitPage = QRadioButton(self.tr("Fit page"), subOptionsGBox)
        self.radioFitWidth = QRadioButton(self.tr("Fit width"), subOptionsGBox)
        self.radioFitPage.setChecked(True)

        self.subOptionsRadioBtnGroup.addButton(self.radioFitPage)
        self.subOptionsRadioBtnGroup.addButton(self.radioFitWidth)

        subOptionsGBoxLayout.addWidget(self.cboxAsViewed)
        subOptionsGBoxLayout.addWidget(self.radioFitPage)
        subOptionsGBoxLayout.addWidget(self.radioFitWidth)

        self.subOptionsRadioBtnGroup.buttonClicked.connect(self.act_sub_options_radio_button_toggled)

        # ---------------------------------------------------------------------
        # btns
        buttonLayout = QHBoxLayout()

        printBtn = QPushButton(self.tr("Print"), baseWidget)
        printBtn.clicked.connect(self.act_print)
        # if self.printer.outputFormat() != QPrinter.NativeFormat:
        #     printBtn.setEnabled(False)

        pdfBtn = QPushButton(self.tr("Export PDF"), baseWidget)
        pdfBtn.clicked.connect(self.act_export_pdf)

        # saveAsImageBtn = QPushButton(self.tr("Save as Image"), baseWidget)
        # saveAsImageBtn.clicked.connect(self.act_save_as_image)

        buttonLayout.addWidget(printBtn)
        buttonLayout.addWidget(pdfBtn)
        # buttonLayout.addWidget(saveAsImageBtn)

        closeBtn = QPushButton(self.tr("Close"), baseWidget)
        closeBtn.setShortcut(QKeySequence("Ctrl+Q"))
        closeBtn.clicked.connect(self.close)

        # ---------------------------------------------------------------------
        # genel
        baseLayout.addWidget(radioGBox)
        baseLayout.addWidget(subOptionsGBox)
        baseLayout.addSpacing(20)
        baseLayout.addLayout(buttonLayout)
        baseLayout.addStretch()
        baseLayout.addWidget(closeBtn)
        # baseLayout.addSpacing(10)

        self.optionsDW.setWidget(baseWidget)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.optionsDW)

    # ---------------------------------------------------------------------
    def act_as_viewed_cbox_toggled(self, secili_mi):
        # if secili_mi:
        #     pass

        # bu secili_mi sinyalini etrafta dolastirmaktansa, _paint methodlarında
        # self.cboxAsViewed secili durumu kontrol ediliyor,
        # burda tekrar paint methodunu cagiriyoruz
        self.act_radio_button_group_clicked(self.radioBtnGroup.checkedButton())

    # ---------------------------------------------------------------------
    def act_radio_button_group_clicked(self, btn):
        # TODO: buyuk dosyalar icin. end call edilsin hemen bitmemis ise.
        # QPrinter().paintingActive()
        # QPrinter().paintEngine().isActive()
        # painter active var bi de isactive de olabilir
        # print(self.printer.paintEngine().isActive())
        # print(self.printer.paintingActive())
        if self.printer.paintingActive():
            if self.printer.paintEngine().end():
                print("engine durduruldu")
        # TODO: buyuk dosyalar icin. end call edilsin hemen bitmemis ise.

        if btn == self.radioDocument:
            tip = "document"
        elif btn == self.radioPage:
            tip = "page"
        elif btn == self.radioView:
            tip = "view"
        elif btn == self.radioSelection:
            tip = "selection"
        elif btn == self.radioContent:
            tip = "content"

        self.paintRequestTypeChanged.emit(tip)
        self._update_options_group_box(tip)

    # ---------------------------------------------------------------------
    def act_sub_options_radio_button_toggled(self, btn):
        if btn == self.radioFitPage:
            tip = "fitPage"
        elif btn == self.radioFitWidth:
            tip = "fitWidth"

        # bu sinyali etrafta dolastirmaktansa, _paint methodlarında
        # hangi radyo buton secili kontrol ediyoruz
        # burda tekrar paint methodunu cagiriyoruz
        self.act_radio_button_group_clicked(self.radioBtnGroup.checkedButton())

    # ---------------------------------------------------------------------
    def _update_options_group_box(self, tip):

        if tip == "document":
            pass
        elif tip == "page":
            pass
        elif tip == "view":
            pass
        elif tip == "selection":
            pass
        elif tip == "content":
            pass

    # ---------------------------------------------------------------------
    def create_tool_bar(self):
        self.toolBar = QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setWindowTitle("Tools")
        self.toolBar.setIconSize(QSize(16, 16))

        self.pageNumberLineEdit = QLineEdit(self.toolBar)
        self.pageNumberLineEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.pageNumberLineEdit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.pageNumberLineEdit.editingFinished.connect(self.act_page_num_edited)

        self.pageNumberLabel = QLabel(self.toolBar)

        self.zoomCBox = QComboBox(self.toolBar)
        self.zoomCBox.setEditable(True)
        self.zoomCBox.setMinimumContentsLength(7)
        self.zoomCBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        zoomEditorLineEdit = QLineEdit(self.toolBar)
        zoomEditorLineEdit.setValidator(ZoomValidator(1, 1000, 1, zoomEditorLineEdit))
        self.zoomCBox.setLineEdit(zoomEditorLineEdit)

        factors = (25, 50, 100, 200, 250, 300, 400, 800, 1600)
        for factor in factors:
            self.zoomCBox.addItem("{}%".format(factor))

        zoomEditorLineEdit.editingFinished.connect(self.act_zoom_factor_changed)
        self.zoomCBox.currentIndexChanged.connect(self.act_zoom_factor_changed)

        # fit group ---------------------------------------------------------------------
        # an action is added to a group by creating it with the group as its parent, no need to add it.
        self.fitGroup = QActionGroup(self.toolBar)
        self.actionFitWidth = QAction(QIcon(':icons/genislik-sigdir.png'), self.tr("Fit Width"), self.fitGroup)
        # self.actionFitWidthAction.setShortcut(QKeySequence("Q"))
        self.actionFitWidth.setCheckable(True)

        self.actionFitPage = QAction(QIcon(':icons/sayfa-sigdir.png'), self.tr("Fit Page"), self.fitGroup)
        # self.actionFitWidthAction.setShortcut(QKeySequence("Q"))
        self.actionFitPage.setCheckable(True)

        self.fitGroup.triggered.connect(self.act_fit)

        # zoom group ---------------------------------------------------------------------
        zoomGroup = QActionGroup(self.toolBar)
        self.actionZoomOut = QAction(QIcon(':icons/zoom-out.png'), self.tr("Zoom Out"), zoomGroup)
        # self.actionZoomOut.setShortcut(QKeySequence("Q"))
        self.actionZoomIn = QAction(QIcon(':icons/zoom-in.png'), self.tr("Zoom In"), zoomGroup)
        # self.actionZoomIn.setShortcut(QKeySequence("Q"))

        # orientation Group ---------------------------------------------------------------------
        orientationGroup = QActionGroup(self.toolBar)
        self.actionPortrait = QAction(QIcon(':icons/dikey-sayfa.png'), self.tr("Portrait"), orientationGroup)
        # self.actionPortrait.setShortcut(QKeySequence("Q"))
        self.actionPortrait.triggered.connect(self.preview.setPortraitOrientation)
        self.actionPortrait.setCheckable(True)

        self.actionLandscape = QAction(QIcon(':icons/yatay-sayfa.png'), self.tr("Landscape"), orientationGroup)
        # self.actionLandscape.setShortcut(QKeySequence("Q"))
        self.actionLandscape.triggered.connect(self.preview.setLandscapeOrientation)
        self.actionLandscape.setCheckable(True)

        # nav group ---------------------------------------------------------------------
        self.navGroup = QActionGroup(self.toolBar)
        self.navGroup.setExclusive(False)
        self.navGroup.triggered.connect(self.act_navigate)
        self.actionFirstPage = QAction(QIcon(':icons/first-page.png'), self.tr("First Page"), self.navGroup)
        # self.actionFirstPage.setShortcut(QKeySequence("Q"))
        self.actionPrevPage = QAction(QIcon(':icons/prev-page.png'), self.tr("Previous Page"), self.navGroup)
        # self.actionPrevPage.setShortcut(QKeySequence("Q"))
        self.actionNextPage = QAction(QIcon(':icons/next-page.png'), self.tr("Next Page"), self.navGroup)
        # self.actionNextPage.setShortcut(QKeySequence("Q"))
        self.actionLastPage = QAction(QIcon(':icons/last-page.png'), self.tr("Last Page"), self.navGroup)
        # self.actionLastPage.setShortcut(QKeySequence("Q"))

        # mode group ---------------------------------------------------------------------
        modeGroup = QActionGroup(self.toolBar)
        self.actionSingleMode = QAction(QIcon(':icons/single-page.png'), self.tr("Show single page"), modeGroup)
        # self.actionSingleMode.setShortcut(QKeySequence("Q"))
        self.actionSingleMode.setCheckable(True)

        self.actionFacingMode = QAction(QIcon(':icons/facing-pages.png'), self.tr("Show facing pages"), modeGroup)
        # self.actionFacingMode.setShortcut(QKeySequence("Q"))
        self.actionFacingMode.setCheckable(True)

        self.actionOverviewMode = QAction(QIcon(':icons/all-pages.png'),
                                          self.tr("Show overview of all pages"), modeGroup)
        # self.actionOverviewMode.setShortcut(QKeySequence("Q"))
        self.actionOverviewMode.setCheckable(True)
        modeGroup.addAction(self.actionOverviewMode)
        modeGroup.triggered.connect(self.act_set_mode)

        # printer group ---------------------------------------------------------------------
        printerGroup = QActionGroup(self.toolBar)
        self.actionPageSetup = QAction(QIcon(':icons/settings.png'), self.tr("Page Setup"), printerGroup)
        # self.actionPageSetup.setShortcut(QKeySequence("Q"))
        self.actionPageSetup.triggered.connect(self.act_page_setup)

        self.actionPrint = QAction(QIcon(':icons/print.png'), self.tr("Print"), printerGroup)
        # self.actionPrint.setShortcut(QKeySequence("Q"))
        self.actionPrint.triggered.connect(self.act_print)

        # page number widget---------------------------------------------------------------------
        pageEdit = QWidget(self.toolBar)
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setContentsMargins(0, 0, 0, 0)

        # if mac

        pageNumberEditSize = self.pageNumberLineEdit.minimumSizeHint()
        pageNumberLabelSize = self.pageNumberLabel.minimumSizeHint()
        self.pageNumberLineEdit.resize(pageNumberEditSize)
        self.pageNumberLabel.resize(pageNumberLabelSize)
        # end if mac

        formLayout = QFormLayout()
        # if mac
        formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        # end if
        formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.pageNumberLineEdit)
        formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.pageNumberLabel)
        vBoxLayout.addLayout(formLayout)
        vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pageEdit.setLayout(vBoxLayout)

        # ---------------------------------------------------------------------
        self.toolBar.addAction(self.actionFitWidth)
        self.toolBar.addAction(self.actionFitPage)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.zoomCBox)
        self.toolBar.addAction(self.actionZoomOut)
        self.toolBar.addAction(self.actionZoomIn)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPortrait)
        self.toolBar.addAction(self.actionLandscape)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionFirstPage)
        self.toolBar.addAction(self.actionPrevPage)
        self.toolBar.addWidget(pageEdit)
        self.toolBar.addAction(self.actionNextPage)
        self.toolBar.addAction(self.actionLastPage)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSingleMode)
        self.toolBar.addAction(self.actionFacingMode)
        self.toolBar.addAction(self.actionOverviewMode)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPageSetup)
        self.toolBar.addAction(self.actionPrint)

        self.zoomInBtn = self.toolBar.widgetForAction(self.actionZoomIn)
        self.zoomInBtn.setAutoRepeat(True)
        self.zoomInBtn.setAutoRepeatInterval(200)
        self.zoomInBtn.setAutoRepeatDelay(200)
        self.zoomInBtn.clicked.connect(self.act_zoom_in)

        self.zoomOutBtn = self.toolBar.widgetForAction(self.actionZoomOut)
        self.zoomOutBtn.setAutoRepeat(True)
        self.zoomOutBtn.setAutoRepeatInterval(200)
        self.zoomOutBtn.setAutoRepeatDelay(200)
        self.zoomOutBtn.clicked.connect(self.act_zoom_out)

        # -- baslangic --
        self.addToolBar(self.toolBar)
        self.actionFitPage.setChecked(True)
        self.actionSingleMode.setChecked(True)
        if self.preview.orientation() == QPageLayout.Orientation.Portrait:
            self.actionPortrait.setChecked(True)
        else:
            self.actionLandscape.setChecked(True)

    # ---------------------------------------------------------------------
    def _is_fitting(self):
        return self.fitGroup.isExclusive() and (self.actionFitWidth.isChecked() or self.actionFitPage.isChecked())

    # ---------------------------------------------------------------------
    def set_fitting(self, on):
        if self._is_fitting():
            return

        self.fitGroup.setExclusive(on)

        if on:
            if self.actionFitWidth.isChecked():
                action = self.actionFitWidth
            else:
                action = self.actionFitPage
            action.setChecked(True)
            if self.fitGroup.checkedAction() != action:
                self.fitGroup.removeAction(action)
                self.fitGroup.addAction(action)
        else:
            self.actionFitWidth.setChecked(False)
            self.actionFitPage.setChecked(False)

    # ---------------------------------------------------------------------
    def olustur_ayarlar(self):
        QApplication.setOrganizationName(shared.DEFTER_ORG_NAME)
        QApplication.setOrganizationDomain(shared.DEFTER_ORG_DOMAIN)
        QApplication.setApplicationName(shared.DEFTER_APP_NAME)
        self.settings = QSettings(shared.DEFTER_AYARLAR_DOSYA_ADRES, QSettings.Format.IniFormat)
        # self.settings.clear()

    # ---------------------------------------------------------------------
    def oku_arayuz_ayarlari(self):
        self.settings.beginGroup("PrintDialogSettings")
        if self.settings.contains("printWinGeometry"):
            self.restoreGeometry(self.settings.value("printWinGeometry"))
            self.restoreState(self.settings.value("printWinState", 0))
            # self.actionAlwaysOnTopToggle.blockSignals(True)
            # self.actionAlwaysOnTopToggle.setChecked(int(self.settings.value("alwaysOnTop", False)))
            # self.actionAlwaysOnTopToggle.blockSignals(False)
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    def yaz_ayarlar(self):
        self.settings.beginGroup("PrintDialogSettings")
        self.settings.setValue("printWinGeometry", self.saveGeometry())
        self.settings.setValue("printWinState", self.saveState(0))  # version=0
        # self.settings.setValue("alwaysOnTop", _unicode_to_bool(self.actionAlwaysOnTopToggle.isChecked()))
        self.settings.endGroup()
        # self.settings.sync()

    # ---------------------------------------------------------------------
    @Slot(QPrinter)
    def paint_requested(self, painter):
        self.paintRequested.emit(painter)

    # ---------------------------------------------------------------------
    @Slot()
    def act_preview_changed(self):
        self.update_nav_actions()
        self.update_page_number_label()
        self.update_zoom_factor()

    # ---------------------------------------------------------------------
    def act_zoom_factor_changed(self):
        text = self.zoomCBox.lineEdit().text()
        # factor = float(text.translate(None, "%"))
        factor = float(text.replace("%", ""))
        factor = max(1.0, min(1000.0, factor))

        self.preview.setZoomFactor(factor / 100)
        self.zoomCBox.setEditText("{}%".format(factor))
        self.set_fitting(False)

    # ---------------------------------------------------------------------
    def update_nav_actions(self):
        cPage = self.preview.currentPage()
        pCount = self.preview.pageCount()

        self.actionNextPage.setEnabled(cPage < pCount)
        self.actionPrevPage.setEnabled(cPage > 1)
        self.actionFirstPage.setEnabled(cPage > 1)
        self.actionLastPage.setEnabled(cPage < pCount)
        self.pageNumberLineEdit.setText(str(cPage))

    # ---------------------------------------------------------------------
    def update_page_number_label(self):
        pCount = self.preview.pageCount()
        maxChars = len(str(pCount))
        self.pageNumberLabel.setText(" {}".format(pCount))
        # cyphersWidth = self.fontMetrics().width("8" * maxChars)
        cyphersWidth = self.fontMetrics().horizontalAdvance("8" * maxChars)
        maxWidth = self.pageNumberLineEdit.minimumSizeHint().width() + cyphersWidth
        self.pageNumberLineEdit.setMinimumWidth(maxWidth)
        self.pageNumberLineEdit.setMaximumWidth(maxWidth)
        self.pageNumberLineEdit.setValidator(QIntValidator(1, pCount, self.pageNumberLineEdit))

    # ---------------------------------------------------------------------
    def update_zoom_factor(self):
        self.zoomCBox.lineEdit().setText("{0:.2f}%".format(self.preview.zoomFactor() * 100))

    # ---------------------------------------------------------------------
    def act_fit(self, action):
        self.set_fitting(True)
        if action == self.actionFitPage:
            self.preview.fitInView()
        else:
            self.preview.fitToWidth()

    # ---------------------------------------------------------------------
    def act_zoom_in(self):
        self.set_fitting(True)
        self.preview.zoomIn()
        self.update_zoom_factor()

    # ---------------------------------------------------------------------
    def act_zoom_out(self):
        self.set_fitting(False)
        self.preview.zoomOut()
        self.update_zoom_factor()

    # ---------------------------------------------------------------------
    def act_page_num_edited(self):
        res = int(self.pageNumberLineEdit.text())
        self.preview.setCurrentPage(res)

    # ---------------------------------------------------------------------
    @Slot(QAction)
    def act_navigate(self, action):

        cPage = self.preview.currentPage()
        if action == self.actionPrevPage:
            self.preview.setCurrentPage(cPage - 1)
        elif action == self.actionNextPage:
            self.preview.setCurrentPage(cPage + 1)
        elif action == self.actionFirstPage:
            self.preview.setCurrentPage(1)
        elif action == self.actionLastPage:
            self.preview.setCurrentPage(self.preview.pageCount())
        self.update_nav_actions()

    # ---------------------------------------------------------------------
    def act_set_mode(self, action):
        if action == self.actionOverviewMode:
            self.preview.setViewMode(QPrintPreviewWidget.ViewMode.AllPagesView)
            self.set_fitting(False)
            self.fitGroup.setEnabled(False)
            self.navGroup.setEnabled(False)
            self.pageNumberLineEdit.setEnabled(False)
            self.pageNumberLabel.setEnabled(False)

        elif action == self.actionFacingMode:
            self.preview.setViewMode(QPrintPreviewWidget.ViewMode.FacingPagesView)

        elif action == self.actionSingleMode:
            self.preview.setViewMode(QPrintPreviewWidget.ViewMode.SinglePageView)

        if action == self.actionFacingMode or action == self.actionSingleMode:
            self.fitGroup.setEnabled(True)
            self.navGroup.setEnabled(True)
            self.pageNumberLineEdit.setEnabled(True)
            self.pageNumberLabel.setEnabled(True)
            self.set_fitting(True)

    # ---------------------------------------------------------------------
    def act_export_pdf(self):
        # if not self.printer.outputFormat()  == QPrinter.NativeFormat:

        fn = QFileDialog.getSaveFileName(self,
                                         self.tr('Export to PDF'),
                                         self.parent().sonKlasorDisaAktar,
                                         self.tr("*.pdf files (*.pdf);;All Files (*)"))

        path = fn[0]
        if path:
            if not path.endswith(".pdf"):
                path = '%s.pdf' % path
            self.printer.setOutputFileName(path)

            if self.printer.outputFileName():
                self.preview.print_()

            self.parent().log(self.tr("File succesfully saved! {}".format(path)), 7000)

            self.parent().sonKlasorDisaAktar = os.path.dirname(path)

            self.close()
            return

    # ---------------------------------------------------------------------
    def act_print(self):

        # if defined(Q_OS_WIN) || defined(Q_OS_MAC)
        # if not self.printer.outputFormat()  == QPrinter.NativeFormat:
        #     title = "Export to PDF"
        #     fn = QFileDialog.getSaveFileName(title,
        #                                            self.printer.outputFileName(),
        #                                            "*.pdf files (*.pdf);;All Files (*)")
        #
        #     path = fn[0]
        #     if path:
        #         if not path.endswith(".pdf"):
        #             path = '%s.pdf' % path
        #         self.printer.setOutputFileName(path)
        #
        #         if self.printer.outputFileName():
        #             self.preview.print()
        #         self.close()
        #         return

        # end if

        if not self.printDialog:
            self.printDialog = QPrintDialog(self.printer, self)
            # self.printDialog.set
        if self.printDialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.preview.print_()
            self.close()

    # ---------------------------------------------------------------------
    def act_page_setup(self):
        pageSetupDialog = QPageSetupDialog(self.printer, self)
        if pageSetupDialog.exec() == QPageSetupDialog.DialogCode.Accepted:
            if self.preview.orientation() == QPageLayout.Orientation.Portrait:
                self.actionPortrait.setChecked(True)
                self.preview.setPortraitOrientation()
            else:
                self.actionLandscape.setChecked(True)
                self.preview.setLandscapeOrientation()

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
