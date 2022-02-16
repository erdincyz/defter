# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '18/May/2018'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Signal, Qt, QSize, QItemSelectionModel, QMimeData
from PySide6.QtWidgets import QTreeView, QAbstractItemView, QHeaderView, QMenu, QProxyStyle
from PySide6.QtGui import QDrag, QPen
from canta.treeSayfa import Sayfa


########################################################################
########################################################################
class YeniStil(QProxyStyle):

    def drawPrimitive(self, element, option, painter, widget=None):
        """ """
        if element == self.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
            painter.setPen(QPen(Qt.blue, 3, Qt.DotLine))
            # option_new = QStyleOption(option)
            # option_new.rect.setLeft(0)
            # if widget:
            #     option_new.rect.setRight(widget.width())
            # option = option_new
        super().drawPrimitive(element, option, painter, widget)


#######################################################################
#######################################################################
class TreeView(QTreeView):
    f2Pressed = Signal()
    middleClick = Signal()
    # treewidgettaki, itemIsAboutToEdited
    # nesneAktiveEdildi = Signal(QTreeWidgetItem, int)  # itemActivated

    secimDegisti = Signal(Sayfa)

    boyut_degisti = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):

        super(TreeView, self).__init__(parent)
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        # self.setIndentation(20)
        # self.setSortingEnabled(False)
        # self.setColumnHidden(1, False)
        # self.setColumnHidden(2, False)
        # self.setColumnHidden(3, False)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        # self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragDropOverwriteMode(False)
        # self.setAutoExpandDelay()
        self.setItemsExpandable(True)

        # self.setRootIsDecorated(True)
        # self.setUniformRowHeights(True)
        self.setIconSize(QSize(128, 128))

        # self.header().setStretchLastSection(False)
        # self.header().setSectionResizeMode(QHeaderView.Interactive)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.header().setSectionResizeMode(QHeaderView.Stretch)

        # doubleclick editi yoketmek icin
        # self.setEditTriggers(QAbstractItemView.EditKeyPressed)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        # self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(self.SingleSelection)

        self.setSelectionBehavior(self.SelectRows)

        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(7)

        self.setAutoScroll(True)
        # self.resizeColumnToContents(0)
        # self.setAutoScrollMargin(20)

        # self.setContextMenuPolicy()

        # ---------------------------------------------------------------------
        # css_stil = """
        # QTreeView::branch {
        #         /* background: palette(base);*/
        #        /* background: #99bbdd;*/
        #        /* background: #deefff;*/
        # }
        # QTreeView::branch:has-siblings:!adjoins-item {
        #     /*background: cyan;*/
        #     background: lightgreen;
        #     border-image: url(:icons/stylesheet/vline.png) 0;
        #
        #
        # }
        # QTreeView::branch:has-siblings:adjoins-item {
        #     /*background: red;*/
        #    /* background: #99bbdd;*/
        #     background: #deefff;
        #     border-image: url(:icons/stylesheet/branch-more.png) 0;
        # }
        #
        # QTreeView::branch:!has-children:!has-siblings:adjoins-item {
        # /*background: blue;*/
        # background: #deefff;
        #     border-image: url(:icons/stylesheet/branch-end.png) 0;
        # }
        #
        #
        # /*kapali dal*/
        # QTreeView::branch:has-children:!has-siblings:closed,
        # QTreeView::branch:closed:has-children:has-siblings {
        #         /*border-image: none;*/
        #         border-image: url(:icons/stylesheet/vline.png) 0;
        #         /*background: pink;*/
        #         /*background: #777777;*/
        #         image: url(:icons/stylesheet/branch-closed.png);
        # }
        #
        # QTreeView::branch:open:has-children:!has-siblings,
        # QTreeView::branch:open:has-children:has-siblings  {
        #     background: #11dd11;
        #     background: lightgreen;
        #     /*border-image: none;*/
        #     border-image: url(:icons/stylesheet/vline.png) 0;
        #     image: url(:icons/stylesheet/branch-open.png);
        # }
        #
        # /*dal acik, ic sayfa var ama kendi seviyesinde baska yok*/
        # /*QTreeView::branch:open:has-children:!has-siblings {
        # background: green;}*/
        #
        # /*dal kapali, ic sayfa var ama kendi seviyesinde baska yok*/
        # /*QTreeView::branch:closed:has-children:!has-siblings {
        #
        #     background: gray;
        # }*/
        #
        # """
        # ---------------------------------------------------------------------

        css_stil = """
                QTreeView::branch {
                background: #eeffdf;
                }

                QTreeView::branch:has-siblings:!adjoins-item {
                    background: #eeffdf;
                }

                QTreeView::branch:has-siblings:adjoins-item {
                    background: #efeffe;
                }

                QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                    background: #efeffe;
                }

                /*kapali dal*/
                QTreeView::branch:has-children:!has-siblings:closed,
                QTreeView::branch:closed:has-children:has-siblings {
                        background: #efeffe;
                        image: url(:icons/stylesheet/branch-closed.png);
                }

                QTreeView::branch:open:has-children:!has-siblings,
                QTreeView::branch:open:has-children:has-siblings  {
                    background: #eeffdf;
                    image: url(:icons/stylesheet/branch-open.png);
                }

                /*dal acik, ic sayfa var ama kendi seviyesinde baska yok*/
                /*QTreeView::branch:open:has-children:!has-siblings {
                    background: #eeffdf;
                }*/

                /*dal kapali, ic sayfa var ama kendi seviyesinde baska yok*/
                /*QTreeView::branch:closed:has-children:!has-siblings {
                    background: #eeffdf;
                }*/

                """

        self.setStyle(YeniStil())
        self.setStyleSheet(css_stil)

    # def resizeEvent(self, event):
    #     self.boyut_degisti.emit()
    #     self.itemDelegate().satirYuksekligi = event.size().width() /2
    #     self.model().layoutChanged.emit()
    #     return super(TreeView, self).resizeEvent(event)

    # ---------------------------------------------------------------------
    def get_properties_for_save(self):
        properties = {"iconSize": self.iconSize(),
                      "satirYuksekligi": self.itemDelegate().satirYuksekligi,
                      }
        return properties

    # ---------------------------------------------------------------------
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addSection("Boyut")
        actionListe = menu.addAction("Liste")
        actionResimKucuk = menu.addAction("Küçük")
        actionResimOrta = menu.addAction("Orta")
        actionResimBuyuk = menu.addAction("Buyuk")
        # menu.addSeparator()
        # actionKopyala = menu.addAction("Çoğalt")
        # actionOzellikler = menu.addAction("Ozellikler")
        # menu.addSection("Resmet")
        # actionGozuken = menu.addAction("Gozuken")
        # actionGozuken = menu.addAction("Tum Sahne")
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == actionListe:
            size = QSize(20, 20)
            satirYuksekligi = 20
            self.setIconSize(size)
            self.itemDelegate().satirYuksekligi = satirYuksekligi
            self.model().treeViewIconSize = size
            self.model().treeViewSatirYuksekligi = satirYuksekligi
        elif action == actionResimKucuk:
            size = QSize(48, 48)
            satirYuksekligi = 48
            self.setIconSize(size)
            self.itemDelegate().satirYuksekligi = satirYuksekligi
            self.model().treeViewIconSize = size
            self.model().treeViewSatirYuksekligi = satirYuksekligi
        elif action == actionResimOrta:
            size = QSize(128, 128)
            satirYuksekligi = 128
            self.setIconSize(size)
            self.itemDelegate().satirYuksekligi = satirYuksekligi
            self.model().treeViewIconSize = size
            self.model().treeViewSatirYuksekligi = satirYuksekligi
        elif action == actionResimBuyuk:
            size = QSize(256, 256)
            satirYuksekligi = 256
            self.setIconSize(size)
            self.itemDelegate().satirYuksekligi = satirYuksekligi
            self.model().treeViewIconSize = size
            self.model().treeViewSatirYuksekligi = satirYuksekligi

    # # ---------------------------------------------------------------------
    # def mousePressEvent(self, e):
    #     """selection changed icinde hallediliyor.."""
    #     # to disable ctrl deselect
    #     idx = self.indexAt(e.pos())
    #     print(idx)
    #     if not idx.isValid():
    #         return
    #         # e.accept()
    #     super(TreeView, self).mousePressEvent(e)
    #
    #     if idx.isValid():  # eski bu aciklama, item yazisina cift tiklayip edit edince hata oluyor.
    #                        item yok diyor. o yuzden if kontrolu.
    #         self.selectionModel().select(idx, self.selectionModel().Select)
    #         self.parent().parent().parent().tv_sayfa_degistir(self.model().itemFromIndex(idx))

    # ---------------------------------------------------------------------
    def mousePressEvent(self, e):
        self.draggedItemIndex = self.indexAt(e.pos())
        super(TreeView, self).mousePressEvent(e)

    # ---------------------------------------------------------------------
    def currentChanged(self, yeniIdx, eskiIdx):

        self.secimDegisti.emit(self.model().sayfa_indexten(yeniIdx))

    # ---------------------------------------------------------------------
    def selectionChanged(self, selected, deselected):
        """This slot is called when the selection is changed.
        The previous selection (which may be empty),
        is specified by deselected , and the new selection by selected ."""
        #  to disable ctrl deselect, and empty click deselect
        # print(selected.isEmpty(), deselected.isEmpty())
        if selected.isEmpty():
            # selected.clear()
            # deselected.clear()
            return

        # if not deselected.isEmpty():
        #     # selected.clear()
        #     # deselected.clear()
        #     return
        super(TreeView, self).selectionChanged(selected, deselected)
        # print(QItemSelection.indexes())
        # self.secimDegisti.emit(self.model().itemFromIndex(QItemSelection),
        #                        self.model().itemFromIndex(QItemSelection_1))
        # TODO: burda niye yukardaki selected kullanamadık?
        item = self.getSelectedItem()
        if item:
            self.secimDegisti.emit(item)
            # TODO: performans optimize et, direkt inde mi kullanmak ,veya key pressed ile secilince scroll etmeceç
            # bi de gerek ok ztaen
            self.scrollTo(self.model().index_sayfadan(item),
                          self.EnsureVisible)  # PositionAtCenter

    # # ---------------------------------------------------------------------
    # def mouseDoubleClickEvent(self, QMouseEvent):
    #     self.itemIsAboutToEdited.emit(self.currentItem().text(0))
    #     super(TreeView, self).mouseDoubleClickEvent(QMouseEvent)
    #
    # # ---------------------------------------------------------------------
    # def keyPressEvent(self, QKeyEvent):
    #     if QKeyEvent.key() == Qt.Key_F2:
    #         self.itemIsAboutToEdited.emit(self.currentItem().text(0))
    #     super(TreeView, self).keyPressEvent(QKeyEvent)

    #
    # def startDrag(self, dropAction):
    #     print('tree start drag')
    #
    #     icon = QIcon('/home/image.png')
    #     pixmap = icon.pixmap(64, 64)
    #
    #     mime = QMimeData()
    #     mime.setData('application/x-item', '???')
    #
    #     drag = QDrag(self)
    #     drag.setMimeData(mime)
    #     drag.setHotSpot(QPoint(pixmap.width()/2, pixmap.height()/2))
    #     drag.setPixmap(pixmap)
    #     drag.start(Qt.CopyAction)

    ########################################################################
    def startDraag(self, Union, Qt_DropActions=None, Qt_DropAction=None):
        # create mime data object
        mime = QMimeData()
        mime.setData('text/sayfa', b'btreeviewdan')
        # start drag
        drag = QDrag(self)
        drag.setMimeData(mime)

        # modeldeki supportedDragActions lari parametre olarak kullanir
        if drag.exec(Qt.MoveAction) == Qt.MoveAction:
            print(drag.target(), "asdlşıafslkdfjiklsdjfilkasjdkfjailskdjf")

    # def dragMoveEvent(self, event):
    #     print(event.mimeData.formats())
    #     event.setDropAction(Qt.MoveAction)
    #     event.accept()
    # if event.mimeData().hasFormat("application/x-item"):
    #     event.setDropAction(Qt.MoveAction)
    #     event.accept()
    # else:
    #     event.ignore()

    # def dragEnterEvent(self, event):
    #     if (event.mimeData().hasFormat('application/x-item')):
    #         event.accept()
    #     else:
    #         event.ignore()
    #
    # def dropEvent(self, event):
    #     if (event.mimeData().hasFormat('application/x-item')):
    #         event.acceptProposedAction()
    #         data = QString(event.mimeData().data("application/x-item"))
    #         item = QTreeWidgetItem(self)
    #         item.setText(0, data)
    #         self.addTopLevelItem(item)
    #     else:
    #         event.ignore()
    ########################################################################

    def dragEnteerEvent(self, event):
        # event.setDropAction(Qt.MoveAction)
        # event.acceptProposedAction()
        # if event.mimeData().hasFormat('object/x-standart-item'):

        # print(event.mimeData().data("application/x-qabstractitemmodeldatalist").data())
        if True:
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    #
    def dragMooveEvent(self, event):
        # print(event.mimeData().formats())
        event.setDropAction(Qt.MoveAction)
        dropIndicatorPos = self.dropIndicatorPosition()
        # print(dropIndicatorPos)
        event.accept()

    def dropEvent(self, event):
        # if event.source():
        #     print(event.source())
        #     QTreeView.dropEvent(self, event)
        # else:

        hedefParentIndex = self.indexAt(event.pos())
        dropIndicatorPos = self.dropIndicatorPosition()
        # print(dropIndicatorPos)

        if not hedefParentIndex.isValid():
            hedefParentIndex = self.rootIndex()

        # if not hedefIndex.parent().isValid() and  hedefIndex.row() != -1:
        if dropIndicatorPos == self.OnItem:
            hedefRow = -11
        elif dropIndicatorPos == self.BelowItem:
            # bu ikisinde item hedef degil aslinda, (AboveItem, BelowItem)
            # hedefParentIndex demek anlam karmasasi yaratmasin, bu durumda parent bunun parenti
            # asagida var zaten.
            # kenarinda bulunmak suretiyle, uzerinde bulundugumuz item,
            # indexAt ile bu itemi bulu sirasini bulup alt veya ust cizgi olmasina gore
            # bir row index belirliyoruz. bu moverRowstada degisecek cunku item silinebilir
            # sira degisebilir. bu silinmeden onceki ham hal.
            hedefRow = hedefParentIndex.row()
            hedefParentIndex = hedefParentIndex.parent()
        elif dropIndicatorPos == self.AboveItem:
            hedefRow = hedefParentIndex.row() - 1
            hedefParentIndex = hedefParentIndex.parent()
        elif dropIndicatorPos == self.OnViewport:
            hedefRow = -22

        # m = event.mimeData()
        # if m.hasUrls():
        # print("dropped")
        # selectedIndex = self.selectedIndexes()[0]
        # print(self.draggedItemIndex)
        self.model().moveRows(self.draggedItemIndex.parent(), self.draggedItemIndex.row(), 1, hedefParentIndex,
                              hedefRow)
        # event.acceptProposedAction()
        # event.accept()
        event.ignore()

        # drPos = self.dropIndicatorPosition()
        # if drPos == QAbstractItemView.BelowItem and drPos== QAbstractItemView.AboveItem:
        #     event.ignore()
        # else:
        #     event.accept()
        #
        #
        # if event.mimeData().hasFormat('object/x-standart-item'):
        #     # event.setDropAction(Qt.CopyAction)
        #     event.setDropAction(Qt.MoveAction)
        #     # print(self.dropIndicatorPosition())
        #     event.accept()
        # else:
        #     event.ignore()

    #
    #     # # ---------------------------------------------------------------------
    #     # def dragLeaveEvent(self, e):
    #     #     print("asd")
    #     #     e.ignore()
    #     #     # return
    #     #
    #     #     super(TreeWidget, self).dragLeaveEvent(e)
    #
    #     # ---------------------------------------------------------------------
    #
    # def wheelEvent(self, event):
    #     # factor = 1.41 ** (event.delta() / 240.0)
    #     # self.scale(factor, factor)
    #
    #     iconSize = self.iconSize()
    #
    #     if event.modifiers() & Qt.AltModifier:
    #         # if event.delta() > 0:
    #         if event.angleDelta().x() > 0:
    #
    #             if not iconSize.width() >= 120:
    #                 # iconSize = 120
    #                 iconSize *= 1.1
    #
    #             self.setIconSize(iconSize)
    #         else:
    #
    #             if not iconSize.width() <= 16:
    #                 # iconSize = 16
    #                 iconSize *= .9
    #             self.setIconSize(iconSize)
    #     else:
    #         super(TreeWidget, self).wheelEvent(event)

    # ---------------------------------------------------------------------
    def sayfa_bul_ve_sec(self, sayfa):
        # https://doc.qt.io/qt-5/qt.html#MatchFlag-enum
        # self.findItems(textToMatch, Qt.MatchContains | Qt.MatchRecursive)
        self._sayfa_bul_ve_sec(ustSayfa=self.model().kokSayfa, sayfa=sayfa)

    # ---------------------------------------------------------------------
    def _sayfa_bul_ve_sec(self, ustSayfa, sayfa):

        for s in ustSayfa.ic_sayfalar():
            if s == sayfa:
                self.itemi_sec_ve_current_index_yap(sayfa)
                break
            else:
                if s.ic_sayfalar():
                    self._sayfa_bul_ve_sec(s, sayfa)

    # ---------------------------------------------------------------------
    def itemi_sec_ve_current_index_yap(self, item):

        # TODO: bu alttaki methodlarda cok biribiri arası zıplama var
        # optimize edemez miyiz acaba.. İnş. sonra tabi. ..

        # print("item", item)
        self.model().enSonAktifSayfa = item
        idx = self.model().index_sayfadan(item)
        # self.setCurrentIndex(idx) # bu ayni isi yapiyor alt iki satirin.
        self.selectionModel().select(idx, self.selectionModel().ClearAndSelect)
        self.selectionModel().setCurrentIndex(idx, QItemSelectionModel.ClearAndSelect)
        self.scrollTo(self.model().index_sayfadan(item), self.EnsureVisible)  # PositionAtCenter

        # print(self.model().enSonAktifSayfa.adi)

    # ---------------------------------------------------------------------
    def current_index_yap(self, item):
        # self.setCurrentIndex(self.model().indexFromItem(item))
        idx = self.model().index_sayfadan(item)
        self.selectionModel().setCurrentIndex(idx, QItemSelectionModel.ClearAndSelect)

    # ---------------------------------------------------------------------
    def itemi_secme(self, item):
        self.selectionModel().select(self.model().sayfada_index(item),
                                     self.selectionModel().Deselect)

    # ---------------------------------------------------------------------
    def itemi_expand_et(self, sayfa, ackapa=True):
        # print("expand")
        # idx = self.model().index_sayfadan(sayfa.parent())
        idx = self.model().index_sayfadan(sayfa)
        self.setExpanded(idx, ackapa)
        self.expand(idx)
        # self.update()

    # ------------------------------------------------------------------------------
    def getSelectedItem(self):
        # TODO: ana kodta selected index kontrollerini kaldir, gerci bu sefer if not none denecek..
        # bi standartlastiralim bunu.
        if self.selectedIndexes():
            sayfa = self.model().sayfa_indexten(self.selectedIndexes()[0])
            # print(item, "burda")
            return sayfa

        # else:
        #     return self.getCurrentItem()
        # return None
        return self.model().kokSayfa

    # ------------------------------------------------------------------------------
    def getCurrentItem(self):
        item = self.model().sayfa_indexten(self.currentIndex())
        return item

    # ------------------------------------------------------------------------------
    def getSelectedItemsParentItem(self):
        item = self.getSelectedItem()
        if item:
            if item.parent():
                return item.parent()

        return self.model().kokSayfa
        # return None

    # #----------------------------------------------------------------------
    # def dragMoveEvent(self, event):
    #
    #     print event.mimeData()
    #
    #     # self
    #     # if opened ise:
    #     #     event.ignore()
    #     # else:
    #     #     event.accept()
    #     # if event.mimeData().hasUrls:
    #     #     event.setDropAction(QtCore.Qt.CopyAction)
    #     #     event.accept()
    #     # else:
    #     #     event.ignore()

    # ------------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            # mayaTBox.myWindow.createScriptTabs(mayaTBox.myWindow.fsModel.fileInfo(mayaTBox.myWindow.treeViewScripts.selectedIndexes()[0]).filePath())
            self.middleClick.emit()
        return QTreeView.mouseReleaseEvent(self, event)

    # ------------------------------------------------------------------------------
    def keyPressEvent(self, event):

        if event.key() == Qt.Key_F2:
            self.f2Pressed.emit()
            self.edit(self.currentIndex())
        else:
            return QTreeView.keyPressEvent(self, event)

    # ----------------------------------------------------------------------
    def zoom(self, delta):
        # print(delta)
        font = self.font()
        iconSize = self.iconSize()
        if delta < 0:
            size = font.pointSize() - 1
            if size > 4:
                font.setPointSize(size)
                self.setFont(font)
                self.itemDelegate().fontSize = size
                iconSize -= QSize(1, 1)
                self.setIconSize(iconSize)
                self.itemDelegate().iconSizeWidth = iconSize.width() + 9
        elif delta > 0:
            size = font.pointSize() + 1
            font.setPointSize(size)
            self.setFont(font)
            self.itemDelegate().fontSize = size
            iconSize += QSize(1, 1)
            self.setIconSize(iconSize)
            self.itemDelegate().iconSizeWidth = iconSize.width() + 9

    # ----------------------------------------------------------------------
    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            self.zoom(event.angleDelta().y())  # pixelDelta
            # print(event.angleDelta().y())  # dikey delta = y
        else:
            QTreeView.wheelEvent(self, event)
