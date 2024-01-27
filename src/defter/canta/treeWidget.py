# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '04/Sep/2017'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QTreeWidget, QSizePolicy


#######################################################################
class TreeWidget(QTreeWidget):
    # tabWidgetFocusedIn = Signal()
    itemIsAboutToEdited = Signal(str)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):

        super(TreeWidget, self).__init__(parent)

        self.setColumnCount(1)
        # self.setHeaderLabel("Sayfalar")
        # headerView = self.header()  # PyQt5.QtWidgets.QHeaderView
        self.header().hide()
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setIconSize(QSize(128, 128))
        self.setUniformRowHeights(True)
        # self.setAnimated(True)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(15)

        # self.setStyleSheet("")

        # self.setStyleSheet(
        #     "QTreeView {show-decoration-selected: 1;}"
        #     "QTreeView::item {border: 1px solid #d9d9d9;"
        #     "    margin:0;padding:0;"
        #     "    border-top-color: transparent;"
        #     "    border-bottom-color: transparent;"
        #     "    border-top-color: black;border-bottom-color: black;"
        #     "}"
        #     "QTreeView::item:hover { background: qlineargradient(x1: 0, y1: 0," "x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);"
        #     "    border: 1px solid #bfcde4;}"
        #     "QTreeView::item:selected {border: 1px solid #567dbc;}"
        #     "QTreeView::item:selected:active{background: qlineargradient(x1: 0," "y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);}"
        #     "QTreeView::item:selected:!active {background: qlineargradient(x1:" "0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);}"
        #
        #     "QTreeView::branch:has-siblings:!adjoins-item {"
        #     "    border-image: url(canta/icons/stylesheet/vline.png) 0; }"
        #     "QTreeView::branch:has-siblings:adjoins-item {"
        #     "    border-image: url(canta/icons/stylesheet/branch-more.png) 0;}"
        #     "QTreeView::branch:!has-children:!has-siblings:adjoins-item {"
        #     "    border-image: url(canta/icons/stylesheet/branch-end.svg) 0;}"
        #     "QTreeView::branch:has-children:!has-siblings:closed,"
        #     "QTreeView::branch:closed:has-children:has-siblings {"
        #     "        border-image: none;"
        #     "        image: url(canta/icons/stylesheet/branch-closed.png);}"
        #     "QTreeView::branch:open:has-children:!has-siblings,"
        #     "QTreeView::branch:open:has-children:has-siblings  {"
        #     "        border-image: none;"
        #     "        image: url(canta/icons/stylesheet/branch-open.png);}"
        #                                         )

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        # asagidaki varken yukardakilere gerek yok, diger widgetler ile olan iliskiler ile ilgili yukardakiler.
        # TODO: liste elemani disari tasinabiliyor.
        self.setDragDropMode(self.DragDropMode.InternalMove)
        # pal = QPalette()

        # pal.setColor(QPalette.Background, Qt.white)
        # self.setPalette(pal)
        # self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.sayfalarDW.setWidget(self.sayfalarDWBaseWidget)

    # ---------------------------------------------------------------------
    def dropEvent(self, e):
        # sayfadaki tek nesneyi drag drop edince secisisz kaliyor her sey.
        # ve secim degisince sayfa_degistirde current item none donuyor ve hata oluyor.
        # veya ctrl ile deselect edilebiliyor. selectionMode SingleItem olsa bile bu ctrl yi etkilemiyor.
        #
        # o yuzden burda agac da bir secisizlestirme olunca en bas nesne seciliyor. idi
        # onu yerine dragged itemi tekrar seciyoruz.
        # illa bir satir secili olmasi onemli,

        draggedItem = self.selectedItems()[0]

        sayfa = draggedItem.data(1, Qt.ItemDataRole.UserRole)[0]

        super(TreeWidget, self).dropEvent(e)

        if draggedItem.parent():
            yeniParent = draggedItem.parent().data(1, Qt.ItemDataRole.UserRole)[0]
        else:
            yeniParent = None
        # lol :)    [o.showMinimized() for o in QApplication.topLevelWidgets()]

        # print(QApplication.topLevelWidgets())
        self.parent().parent().parent().cDokuman.sayfa_tasi(sayfa,
                                                            yeniParent,
                                                            self.indexFromItem(draggedItem).row())

        if not self.selectedItems():
            draggedItem.setSelected(True)
            # self.setCurrentItem(self.topLevelItem(0), 0)

    # # ---------------------------------------------------------------------
    # def dragLeaveEvent(self, e):
    #     print("asd")
    #     e.ignore()
    #     # return
    #
    #     super(TreeWidget, self).dragLeaveEvent(e)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, e):
        # to disable ctrl deselect
        super(TreeWidget, self).mousePressEvent(e)
        item = self.itemAt(e.pos())
        if item:  # item yazisina cift tiklayip edit edince hata oluyor. item yok diyor. o yuzden if kontrolu.
            item.setSelected(True)
            self.parent().parent().parent().tw_sayfa_degistir(item)

            # if item and item != not self.currentItem():
            #     self.clearSelection()
            #     item.setSelected(True)
            #     e.accept()

    # ---------------------------------------------------------------------
    def wheelEvent(self, event):
        # factor = 1.41 ** (event.delta() / 240.0)
        # self.scale(factor, factor)

        iconSize = self.iconSize()

        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            # if event.delta() > 0:
            if event.angleDelta().x() > 0:

                if not iconSize.width() >= 120:
                    # iconSize = 120
                    iconSize *= 1.1

                self.setIconSize(iconSize)
            else:

                if not iconSize.width() <= 16:
                    # iconSize = 16
                    iconSize *= .9
                self.setIconSize(iconSize)
        else:
            super(TreeWidget, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, QMouseEvent):
        self.itemIsAboutToEdited.emit(self.currentItem().text(0))
        super(TreeWidget, self).mouseDoubleClickEvent(QMouseEvent)

    # ---------------------------------------------------------------------
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key.Key_F2:
            self.itemIsAboutToEdited.emit(self.currentItem().text(0))
        super(TreeWidget, self).keyPressEvent(QKeyEvent)

    # ---------------------------------------------------------------------
    def temizle(self):
        pass

    # ---------------------------------------------------------------------
    def sayfa_bul_ve_sec(self, sayfa):
        # https://doc.qt.io/qt-5/qt.html#MatchFlag-enum
        # self.findItems(textToMatch, Qt.MatchContains | Qt.MatchRecursive)
        self._sayfa_bul_ve_sec(self.invisibleRootItem(), sayfa)

    # ---------------------------------------------------------------------
    def _sayfa_bul_ve_sec(self, item, sayfa):

        for i in range(item.childCount()):
            child = item.child(i)
            if sayfa == child.data(1, Qt.ItemDataRole.UserRole)[0]:
                child.setSelected(True)
                self.setCurrentItem(child)
                break
            else:
                if child.childCount():
                    self._sayfa_bul_ve_sec(child, sayfa)
