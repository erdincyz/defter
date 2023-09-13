# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '01/Jun/2018'
__author__ = 'Erdinç Yılmaz'

import tempfile
from typing import Any

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal, QSize, QMimeData, QByteArray

from canta.treeSayfa import Sayfa
from canta.shared import renk_degismis_nesne_yazi_rengi


# dataChanged : belirli row veya columnları gunceller , ekleme cıkarma yok
# layoutAboutToBeChanged , layoutChanged, bunlar viewa her şeyi gunclletir, tekrar çizdirir, row column ekleme için
# layoutAboutToBeChanged ve turevlerini mumkun oldugunca biz emit etmiyoruz,
# beginInsert, endInsert kullanaraktan bunlar emit ediyor gerektigi kadarı ile gerektigi yerde. tabi bu bir tavsiye

########################################################################
class DokumanAgacModel(QAbstractItemModel):
    dokuman_no = 1

    MimeType = "object/x-standart-item"

    nesneDegisti = Signal(Sayfa, str)

    # ---------------------------------------------------------------------
    def __init__(self, tempDirPath=None, parent=None):
        super(DokumanAgacModel, self).__init__(parent)

        # bunların fonksiyonları scene icinde
        # her sayfa scene , ayrı oldugu icin aynı dokuman icinde farklı sayfalarda uzerine yazma
        # durumu oluyordu.

        self.embededImageCounter = 0
        self.embededVideoCounter = 0
        self.embededFileCounter = 0

        self.treeViewIkonBoyutu = QSize(48, 48)
        self.yaziRengi = parent.palette().windowText().color()

        # self.sayfalar = []
        Sayfa.sayfa_no = 0  # her dokuman icin sayfa sayisini sifirliyoruz
        self.kokSayfa = Sayfa()  # omurga
        self.kokSayfa.adi = "kokSayfa"
        # self.sayfa_ekle(self.kokSayfa, ustSayfa=None)
        # self.

        if not tempDirPath:
            tempDirPath = tempfile.mkdtemp(prefix="defter-tmp")

        self.tempDirPath = tempDirPath
        self.saveFilePath = ""
        self.no = DokumanAgacModel.dokuman_no
        self.fileName = self.tr("Untitled Document - {}".format(self.no))

        self.enSonAktifSayfa = None

        DokumanAgacModel.dokuman_no += 1

        # self._roleNames = {}
        # for i in range(0, meta.propertyCount()):
        #     self._roleNames[i] = meta.property(i).name()

    # ---------------------------------------------------------------------
    def degismis_sayfa_var_mi(self):

        var_mi = False

        for sayfa in self.sayfalar():
            if not sayfa.scene.undoStack.isClean():
                var_mi = True
                break

        return var_mi

    # ---------------------------------------------------------------------
    def degismis_sayfalarin_listesi(self):
        liste = []
        for sayfa in self.sayfalar():
            if not sayfa.scene.undoStack.isClean():
                liste.append(sayfa)

        return liste

    # ---------------------------------------------------------------------
    def iterItems(self, root):
        if root is not None:
            stack = [root]
            while stack:
                parent = stack.pop(0)
                # for row in range(parent.satirSayisi()):
                #     for column in range(parent.sutunSayisi()):
                #         child = parent.child(row, column)
                #         yield child
                #         if child.hasChildren():
                #             stack.append(child)
                for row in range(parent.satirSayisi()):
                    ic_sayfa = parent.ic_sayfa(row)
                    yield ic_sayfa
                    if ic_sayfa.ic_sayfa_var_mi():
                        stack.append(ic_sayfa)

    # ---------------------------------------------------------------------
    def kaydedince_butun_yildizlari_sil(self):
        self._kaydedince_butun_yildizlari_sil(self.kokSayfa.ic_sayfalar())

    # ---------------------------------------------------------------------
    def _kaydedince_butun_yildizlari_sil(self, sayfalar):
        for sayfa in sayfalar:
            sayfa.scene.blockSignals(True)
            sayfa.scene.undoStack.setClean()

            itemText = sayfa.adi
            if itemText[0] == "★":
                sayfa.adi = itemText[2:]

            idx = self.index_sayfadan(sayfa)
            self.dataChanged.emit(idx, idx)

            sayfa.scene.blockSignals(False)

            if sayfa._ic_sayfalar:
                self._kaydedince_butun_yildizlari_sil(sayfa._ic_sayfalar)

    # ---------------------------------------------------------------------
    def sayfalar(self):
        # TODO: bu sıra gozetmiyor
        stack = [self.kokSayfa]
        while stack:
            parent = stack.pop(0)
            # for row in range(parent.satirSayisi()):
            #     for column in range(parent.sutunSayisi()):
            #         child = parent.child(row, column)
            #         yield child
            #         if child.hasChildren():
            #             stack.append(child)
            for row in range(parent.satirSayisi()):
                ic_sayfa = parent.ic_sayfa(row)
                yield ic_sayfa
                if ic_sayfa.ic_sayfa_var_mi():
                    stack.append(ic_sayfa)

    # ---------------------------------------------------------------------
    def get_properties_for_save(self):
        properties = {"saveFilePath": self.saveFilePath,
                      "fileName": self.fileName,
                      "embededImageCounter": self.embededImageCounter,
                      "embededVideoCounter": self.embededVideoCounter,
                      "embededFileCounter": self.embededFileCounter,
                      "enSonAktifSayfaKim": self.enSonAktifSayfa._kim,
                      "treeViewIkonBoyutu": self.treeViewIkonBoyutu
                      }
        return properties

    # ---------------------------------------------------------------------
    def kimlikten_sayfa(self, kim):
        for sayfa in self.sayfalar():
            if kim == sayfa._kim:
                # break
                return sayfa
        return None

    # ---------------------------------------------------------------------
    def sayfa_indexten(self, index):
        if index.isValid():
            return index.internalPointer()
            # if sayfa:
            #     return sayfa
            # return sayfa

        return self.kokSayfa

    # ---------------------------------------------------------------------
    def satirdaki_sayfa(self, satir):
        return self.kokSayfa.ic_sayfa(satir)

    # ---------------------------------------------------------------------
    def indexFromItem(self, item, column=0):
        if item == self.kokSayfa:
            return QModelIndex()

        parent = item.parent()
        if not parent:
            parent = self.kokSayfa

        if len(parent.children()) == 0:
            return None

        # print(item.title(), [i.title() for i in parent.children()])

        row = parent.children().index(item)
        col = column

        return self.createIndex(row, col, item)

    # ---------------------------------------------------------------------
    def index_sayfadan(self, sayfa, column=0):
        if not sayfa:
            return QModelIndex()

        if sayfa == self.kokSayfa:
            return QModelIndex()

        ustSayfa = sayfa.parent()
        if not ustSayfa:
            ustSayfa = self.kokSayfa

        if ustSayfa.satirSayisi() == 0:
            return None  # ?? hmm, bos index root olur tabi, none dondurmek lazım

        row = sayfa.satir()

        return self.createIndex(row, column, sayfa)

        # return self.index(row=sayfa.satir(), column=0, parent=sayfa.parent())

    """
    QModelIndex QStandardItemModel::indexFromItem(const QStandardItem *item) const
{
    if (item && item->d_func()->parent) {
        QPair<int, int> pos = item->d_func()->position();
        return createIndex(pos.first, pos.second, item->d_func()->parent);
    }
    return QModelIndex();
}
    """

    # ---------------------------------------------------------------------
    def parentt(self, index=None):
        node = self.sayfa_indexten(index)
        parentNode = node.parent()
        if parentNode == self.kokSayfa:
            return QModelIndex()
        return self.createIndex(parentNode.satir(), 0, parentNode)

    """
    QModelIndex QStandardItemModel::parent(const QModelIndex &child) const
{
    Q_D(const QStandardItemModel);
    if (!d->indexValid(child))
        return QModelIndex();
    QStandardItem *parentItem = static_cast<QStandardItem*>(child.internalPointer());
    return indexFromItem(parentItem);
}
    """

    # ---------------------------------------------------------------------
    def parent(self, index=None):
        """bu tamam olmasi lazım"""
        if not index.isValid():
            return QModelIndex()

        sayfa = index.internalPointer()
        ust_sayfa = sayfa.parent()

        # TODO: bu olmamıs olabilir.
        # yani tab sonra az saga kaydır yeni tab az saga kaydir yeni tab ve de burda ust_sayfa_none diyor
        # ama bundan sonra da problem var..
        if not ust_sayfa:
            return QModelIndex()

        if ust_sayfa == self.kokSayfa:
            return QModelIndex()

        return self.createIndex(ust_sayfa.satir(), 0, ust_sayfa)  # row, column, parent

    # ---------------------------------------------------------------------
    def index(self, row: int, column: int, parentIndex: QModelIndex = QModelIndex()):

        """İnş Tamam"""

        # allttaki de aktif edilebilir standatitem e edilmiş

        # if row < 0 or column < 0 or row >= parent.satirSayisi() or column >= parent.sutunSayisi():
        #     return QModelIndex()

        # parentNode = self.index_sayfadan(parent)

        # if parentIndex.isValid() and parentIndex.column() != 0:
        #     return QModelIndex()

        if not self.hasIndex(row, column, parentIndex):
            return QModelIndex()

        # parentItem = self.sayfa_indexten(parentIndex)
        # altakinin aynisi zaten func cagirmasin bosuna diye burda acik ekledik

        if not parentIndex.isValid():
            parentItem = self.kokSayfa
        else:
            parentItem = parentIndex.internalPointer()

        ic_sayfa = parentItem.ic_sayfa(row)
        if ic_sayfa:
            return self.createIndex(row, column, ic_sayfa)
        else:
            return QModelIndex()

    # ---------------------------------------------------------------------
    def supportedDropActions(self):
        # return Qt.CopyAction | Qt.MoveAction
        return Qt.DropAction.MoveAction

    # ---------------------------------------------------------------------
    def supportedDragActions(self):
        return Qt.DropAction.MoveAction

    # def flags(self, index):
    #     defaultFlags = QAbstractItemModel.flags(self, index)
    #
    #     if index.isValid():
    #         return Qt.ItemIsEditable | Qt.ItemIsDragEnabled | \
    #                Qt.ItemIsDropEnabled | defaultFlags
    #
    #     else:
    #         return Qt.ItemIsDropEnabled | defaultFlags

    # def mimeTypes(self):
    #     types = ['application/x-ets-qt4-instance']
    #     return types
    #
    # def mimeData(self, Iterable, QModelIndex=None):
    #
    #     node = self.sayfa_indexten(QModelIndex[0])
    #     mimeData = PyMimeData(node)
    #     return mimeData

    # def dropMimeData(self, mimedata, action, row, column, parentIndex):
    #     if action == Qt.IgnoreAction:
    #         return True
    #
    #     dragNode = mimedata.instance()
    #     print(row,column)
    #     parentNode = self.sayfa_indexten(parentIndex)
    #
    #     # make an copy of the node being moved
    #     newNode = deepcopy(dragNode)
    #     newNode.setParent(parentNode)
    #     self.insertRow(len(parentNode) - 1, parentIndex)
    #     self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
    #               parentIndex, parentIndex)
    #     return True

    def mimeTypess(self):
        return ['text/sayfa']

    def mimeDataa(self, indexes, idx=None):

        print(indexes, idx)
        print(self.sayfa_indexten(indexes[0]).adi)

        mimedata = QMimeData()
        # mimedata.setData('text/sayfa', b'mimeDasdfsdfsdfsdfta')
        mimedata.setData('text/sayfa', QByteArray())
        return mimedata

        # mimedata = QMimeData()
        # encoded_data = QtCore.QByteArray()
        # stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)
        # for index in indexes:
        #     if index.isValid():
        #         text = self.data(index, 0)
        # stream << QtCore.QByteArray(text.encode('utf-8'))
        # mimedata.setData('application/vnd.treeviewdragdrop.list', encoded_data)
        #
        #
        # return mimedata

    # # ---------------------------------------------------------------------
    # def canDropMimeData(self, data, Qt_DropAction, row, column, QModelIndex):
    #     print(row,column)
    #     print(data.formats())
    #     if not data.hasFormat("text/sayfa"):
    #         return False
    #     return True

    def dropMiemeData(self, data, action, row, column, parent):

        if not self.canDropMimeData(data, action, row, column, parent):
            return True

        print("asdasdsfsadfasdf")

        # print('dropMimeData %s %s %s %s' % (data.data('text/xml').decode("utf-8"), action, row, parent))

        if action == Qt.DropAction.IgnoreAction:
            return True
        if not data.hasFormat('text/xml'):
            return False
        if column > 0:
            return False

        num_rows = self.rowCount(QModelIndex())
        if num_rows <= 0:
            return False

        if row < 0:
            if parent.isValid():
                row = parent.row()
            else:
                return False

        # return QAbstractItemModel.dropMimeData(self, data, action, row, column, parent)

    #
    # def moveItem(self, fromi, toi):
    #     print("move %d->%d" % (fromi, toi))
    #
    #     self.beginMoveRows(QtCore.QModelIndex(), fromi, fromi, QtCore.QModelIndex(), toi)
    #
    #     item = self.lst.pop(fromi)
    #     self.lst.insert(toi, item)
    #
    #     self.endMoveRows()
    #
    #     print("done")

    # def moveRow(self, QModelIndex, p_int, QModelIndex_1, p_int_1):
    #     pass

    # ---------------------------------------------------------------------
    # def moveRows(self, QModelIndex, p_int, p_int_1, QModelIndex_1, p_int_2):
    def moveRows(self, sourceParent, sourceRow, count, hedefParentIndex, hedefRow):
        kaynak_ust_sayfa = self.sayfa_indexten(sourceParent)
        hedef_ust_sayfa = self.sayfa_indexten(hedefParentIndex)

        # print(kaynak_ust_sayfa.adi,kaynak_ust_sayfa.satirSayisi(),
        # sourceRow, "--", hedef_ust_sayfa.satirSayisi(), hedefRow)
        tasinan_sayfa = kaynak_ust_sayfa.ic_sayfa(sourceRow)

        if hedefRow == -11:  # on item
            hedefRowYeni = hedef_ust_sayfa.satirSayisi() - 1
            # if hedef_ust_sayfa == kaynak_ust_sayfa:
            # print(sourceRow, hedefRow, hedefRowYeni)
            self.removeRow(sourceRow, sourceParent)
            # self.beginMoveRows(sourceParent, sourceRow, count, hedefParentIndex, hedefRowYeni)
            # kaynak_ust_sayfa.sayfa_sil(tasinan_sayfa)
            self.beginInsertRows(hedefParentIndex, hedefRowYeni, hedefRowYeni)
            hedef_ust_sayfa.sayfa_ekle(tasinan_sayfa)
            self.endInsertRows()

        elif hedefRow == -22:  # on view port
            hedefRowYeni = hedef_ust_sayfa.satirSayisi() - 1
            if hedef_ust_sayfa == kaynak_ust_sayfa:
                if hedefRowYeni == sourceRow:  # o seviyedeki son nesne ayni kendi yerine birakilinca
                    return
                # self.beginMoveRows(sourceParent, sourceRow, count, hedefParentIndex, hedefRowYeni)
                # hedef_ust_sayfa.sayfa_sira_degistir(tasinan_sayfa, hedefRowYeni)
                # # self.layoutChanged.emit()
                # self.endMoveRows()
            # print(sourceRow, hedefRow, hedefRowYeni)
            self.removeRow(sourceRow, sourceParent)
            # self.beginMoveRows(sourceParent, sourceRow, count, hedefParentIndex, hedefRowYeni)
            # kaynak_ust_sayfa.sayfa_sil(tasinan_sayfa)
            self.beginInsertRows(hedefParentIndex, hedefRowYeni, hedefRowYeni)
            hedef_ust_sayfa.sayfa_ekle(tasinan_sayfa)
            self.endInsertRows()

        # hedef row burda gercek
        else:  # hedef row itemin alt veya ustu farkli parent de olabilir
            hedefRowYeni = hedefRow
            if hedef_ust_sayfa == kaynak_ust_sayfa:
                # sourceRow < hedefRow  icin hedefRow dogru degerde geliyor
                if sourceRow > hedefRow:
                    hedefRowYeni = hedefRow + 1
            else:
                hedefRowYeni = hedefRow + 1
            self.removeRow(sourceRow, sourceParent)
            # kaynak_ust_sayfa.sayfa_sil(tasinan_sayfa)
            # self.beginMoveRows(sourceParent, sourceRow, count, hedefParentIndex, hedefRow)
            # print(sourceRow, hedefRow, hedefRowYeni)
            self.beginInsertRows(hedefParentIndex, hedefRowYeni, hedefRowYeni)
            hedef_ust_sayfa.sayfa_araya_ekle(hedefRowYeni, tasinan_sayfa)
            self.endInsertRows()

            # if hedef_ust_sayfa == kaynak_ust_sayfa:
            #     self.beginMoveRows(sourceParent, sourceRow, count, hedefParentIndex, hedefRowYeni)
            #     hedef_ust_sayfa.sayfa_sira_degistir(tasinan_sayfa, hedefRowYeni)
            #     self.layoutChanged.emit()
            #     self.endMoveRows()
            # else:

        # print("moveRows",sourceParent, sourceRow, count, destinationParent, destinationChildRow)
        # self.data = self.data[1] + self.data[0] + self.data[2]
        # self.endMoveRows()
        # print("moveRows finished")

    # # ---------------------------------------------------------------------
    # def moveRow(self, QModelIndex, p_int, QModelIndex_1, p_int_1):
    # sourceParent, sourceRow, destinationParent, destinationChild)
    #     print("asdasdsadasdasd")
    #     pass

    # ---------------------------------------------------------------------
    # bu 4 her modelde lazım
    # ---------------------------------------------------------------------
    def flags(self, index: QModelIndex):
        """her modelde mutlaka lazım,
        editable icin ayrica Qt::ItemIsEditable lazım"""
        # if not index.isValid():
        #     return 0

        return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | \
               Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled | \
               Qt.ItemFlag.ItemIsDropEnabled
        # return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # ---------------------------------------------------------------------
    def data(self, index: QModelIndex, role: int = None):
        """her modelde mutlaka lazım"""
        if not index.isValid():
            # return None
            return

        # TODO: bu alt satir problem, >= eşitten mi acaba, bazi satirlari bos gosteriyordu.
        # if index.row() >= self.rowCount():
        #     return QVariant()

        # if not index.parent().isValid():
        #     return None

        # if role != Qt.DisplayRole and role != Qt.EditRole:
        #     return None

        # her row her column icin cagriliyor bu,,
        # pixel pixel set etmek gibi eski tvlerde kayan nokta
        sayfa = self.sayfa_indexten(index)
        # print(sayfa.adi, "sayfa adi datadan")
        # sayfa = index.internalPointer()        # return item.data(index.column())

        # !!! delege kullandigimiz icin burda buyuk ihtimalle sadece qt.editrole kismi kullaniliyor.
        # o da cift tiklayinca mesela

        if role == Qt.ItemDataRole.DisplayRole:
            # return self.items[index.row()]
            return sayfa.adi

        if role == Qt.ItemDataRole.EditRole:
            if sayfa.adi[0] == "★":
                return sayfa.adi[2:]
            return sayfa.adi

        elif role == Qt.ItemDataRole.ToolTipRole:
            return sayfa.adi

        elif role == Qt.ItemDataRole.DecorationRole:
            return sayfa.ikon

        elif role == Qt.ItemDataRole.ForegroundRole:
            if sayfa.scene.isModified():
                return renk_degismis_nesne_yazi_rengi
            else:
                return self.yaziRengi
        elif role == Qt.ItemDataRole.SizeHintRole:
            return self.treeViewIkonBoyutu

        # elif role == Qt.ItemDataRole.BackgroundRole:
        #
        #     if self.items[index.row()][:2] == "!!":
        #         return QColor(50, 50, 50)
        #         # return self.colorPathAlternateA
        #     else:
        #         # if self.data(index, QtCore.Qt.ItemDataRole.ToolTipRole) in self.openPaths:
        #         if index.data(Qt.ItemDataRole.DisplayRole) == self.activePath:
        #             # return QtGui.QColor(100,100,255)
        #             return self.colorActivePathBg
        #         else:
        #             if index.row() % 2 == 0:
        #                 # return QtGui.QColor(100,100,100)
        #                 return self.colorPathAlternateA
        #             else:
        #                 # return QtGui.QColor(80,80,80)
        #                 return self.colorPathAlternateB

        # elif role == Qt.ItemDataRole.ForegroundRole:
        #
        #     if self.items[index.row()][:2] == "!!":
        #         return QColor(100, 100, 100)
        #     else:
        #         if index.data(Qt.ItemDataRole.DisplayRole) == self.activePath:
        #             # return QtGui.QColor(100,255,100)
        #             return self.colorActivePathText
        #         else:
        #             # return QtGui.QColor(200,200,200)
        #             return self.colorPathsText

        # elif role == Qt.ItemDataRole.FontRole:
        #     font = QFont()
        #     if index.data(Qt.ItemDataRole.DisplayRole) == self.activePath:
        #
        #         font.setBold(True)
        #     else:
        #         font.setBold(False)
        #
        #     if index.data(Qt.ItemDataRole.DisplayRole) in self.openPaths:
        #         font.setItalic(True)
        #     else:
        #         font.setItalic(False)
        #
        #     return font

        else:
            return  # None

    # ---------------------------------------------------------------------
    def headerData(self, section, orientation, role=None):
        """her modelde mutlaka lazım"""
        # if orientation == Qt.Horizontal and role == Qt.DisplayRole:
        if (orientation, role) == (Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole):
            # return self.root.data(section)
            return "Sayfalar"
        return "Sayfalar"

    # ---------------------------------------------------------------------
    # def rowCount(self, parentIndex=QModelIndex()):
    def rowCount(self, parent=QModelIndex()):
        """her modelde mutlaka lazım"""
        # return self.kokSayfa.satirSayısı()
        #
        # parentItem = self.getItem(parent)
        #
        # return parentItem.childCount()

        # parent = self.index_sayfadan(parentIndex)

        # if parent.column() > 0:
        #     return 0

        if not parent.isValid():
            parentNode = self.kokSayfa
        else:
            parentNode = parent.internalPointer()

        return parentNode.satirSayisi()
        # return len(parentNode)

    # ---------------------------------------------------------------------
    # tree, table icin
    # ---------------------------------------------------------------------
    def columnCount(self, parent: QModelIndex = None, *args, **kwargs) -> int:
        """ the following functions must be implemented in direct subclasses of
         QAbstractTableModel and QAbstractItemModel:"""

        # return self.kokSayfa.sutunSayısı()

        return 1

        # if index.isValid():
        #     return index.internalPointer().columnCount()
        # return self._root.columnCount()

    # ---------------------------------------------------------------------
    def setData(self, index: QModelIndex, value: Any, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return False

        """
        if (index.isValid() && role == Qt::EditRole) {

        stringList.replace(index.row(), value.toString());
        emit dataChanged(index, index, {role});
        return true;
    }
    return false;"""

        sayfa = self.sayfa_indexten(index)
        # if role == Qt.ItemDataRole.DisplayRole:
        #     sayfa.adi = value
        #     # print(value)
        #     self.dataChanged.emit(index, index)
        #     return True

        if role == Qt.ItemDataRole.EditRole:
            # self.items[index.row()] = value
            if sayfa.adi == value:  # cift tiklayip mesela hic bir sey degistirmeyince degisimis diye isaretlenmesin..
                return False

            sayfa_eski_adi = sayfa.adi
            if sayfa.scene.isModified():
                sayfa.adi = "★ {}".format(value)
            else:
                sayfa.adi = value

            self.dataChanged.emit(index, index)
            self.nesneDegisti.emit(self.sayfa_indexten(index), sayfa_eski_adi)
            return True

        return False

    # ---------------------------------------------------------------------
    def setHeaderData(self, p_int, Qt_Orientation, _any, role=None):
        self.headerDataChanged.emit()

    # ---------------------------------------------------------------------
    # resizable
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    def sayfaEkleIndexIle(self, sayfa, index):
        if not index or not index.isValid():
            ustSayfa = self.kokSayfa
        else:
            ustSayfa = index.internalPointer()
            ustSayfa.sayfa_ekle(sayfa)

    def insertRowss(self, position, rows=1, index=QModelIndex()):
        indexSelected = self.index(position, 0)
        itemSelected = indexSelected.data().toPyObject()

        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.items.insert(position + row, "%s_%s" % (itemSelected, self.added))
            self.added += 1
        self.endInsertRows()
        return True

    def insertRows(self, position, rows, parent: QModelIndex = None, sayfa=None, *args, **kwargs):
        print("insert")
        parentSayfa = self.sayfa_indexten(parent)
        self.beginInsertRows(parent, position, position + rows - 1)

        sonuc = False
        for row in range(rows):
            sayfa = Sayfa(adi='Unknown')
            sonuc = parentSayfa.sayfa_araya_ekle(row, sayfa)
        self.endInsertRows()
        return sonuc

    """
    bool StringListModel::insertRows(int position, int rows, const QModelIndex &parent)
{
    beginInsertRows(QModelIndex(), position, position+rows-1);

    for (int row = 0; row < rows; ++row) {
        stringList.insert(position, "");
    }

    endInsertRows();
    return true;
}"""

    # ---------------------------------------------------------------------
    def sayfa_ekle(self, satir=None, scene=None, view=None, ikon=None, ustSayfa=None):

        adi = self.tr("Untitled")
        sayfa = Sayfa(adi=adi, scene=scene, view=view, ikon=ikon, parent=ustSayfa)

        # parentIndex = self.index_sayfadan(ustSayfa)

        # self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        # pos =ustSayfa.sayfa_sayisi()
        # self.beginInsertRows(QModelIndex(),pos ,pos)

        if satir:
            if ustSayfa == self.kokSayfa:
                # print("aaa")
                self.kokSayfa.sayfa_araya_ekle(satir + 1, sayfa)
            else:
                # print("bbbb")

                ustSayfa.sayfa_araya_ekle(satir + 1, sayfa)
        else:  # alt sayfa eklerken
            # if ustSayfa == self.kokSayfa:
            #     self.kokSayfa.sayfa_ekle(sayfa)
            # else:
            #     ustSayfa.sayfa_ekle(sayfa)

            if ustSayfa == self.kokSayfa:
                # print("cccc")
                self.kokSayfa.sayfa_ekle(sayfa)

            else:
                # print("ddd")
                # print(ustSayfa.ic_sayfalar())
                ustSayfa.sayfa_ekle(sayfa)
                # print(ustSayfa.ic_sayfalar())

        # self.endInsertRows()

        # idx = self.index_sayfadan(sayfa)
        # self.dataChanged.emit(parentIndex, parentIndex)
        # self.dataChanged.emit(idx, idx)
        if not ustSayfa:
            self.enSonAktifSayfa = sayfa
        self.layoutChanged.emit()

        # print("----" * 5)
        #
        # for ic_sayfa in self.kokSayfa.ic_sayfalar():
        #     print(ic_sayfa.adi)
        #     for ic_sayfa2 in ic_sayfa.ic_sayfalar():
        #         print("--    ",ic_sayfa2.adi)
        #         for ic_sayfa3 in ic_sayfa2.ic_sayfalar():
        #             print("++       ", ic_sayfa3.adi)
        #             for ic_sayfa4 in ic_sayfa3.ic_sayfalar():
        #                 print("**           ", ic_sayfa4.adi)
        #
        # # print(list(self.iterItems(self.kokSayfa)))
        # print("----" * 5)

        return sayfa

    # ---------------------------------------------------------------------
    def sifirla(self):
        # TODO: eski sayfa cop toplanıyor mu
        self.beginResetModel()
        self.kokSayfa = Sayfa()
        self.endResetModel()

    # ---------------------------------------------------------------------
    def satir_sil(self, sayfa):
        row = sayfa.satir()
        # scene = sayfa.scene
        # view = sayfa.view

        # if sayfa._ic_sayfalar:
        #     self._ic_sayfa_sil(sayfa._ic_sayfalar)

        # TODO:: bu  alttaki tek satir da hallediyor eger tek row silinecekse
        # self.removeRow(row, self.index_sayfadan(sayfa.parent()))

        # if not sayfa.parent() is self.kokSayfa:

        if not sayfa.parent() == self.kokSayfa:
            # print("sil, parent var")
            self.beginRemoveRows(self.index_sayfadan(sayfa.parent()), row, row)
            # itemPointerList = sayfa.parent().takeRow(row)
            # sonuc = self.removeRow(row, self.index_sayfadan(sayfa.parent()))
            sonuc = sayfa.parent().sayfa_sil(sayfa)
        else:
            self.beginRemoveRows(QModelIndex(), row, row)
            # sonuc = self.removeRow(row, QModelIndex())
            sonuc = self.kokSayfa.sayfa_sil(sayfa)

        self.endRemoveRows()
        # self.layoutChanged.emit()

        # print(sonuc, "removed")

        # if sonuc:
        #     ##################################
        #     # !!! ONEMLI ONEMLI ONEMLI !!!
        #     ## bu alttaki  grup yukarda iken bir tabtan sayfa silince diger tabtaki dokumani kapatabiliyordu veya
        #     ## sayfa silinen dokumani da kapatabiliyordu. (kapatmak = tabi silmek), o yuzden asagi aldik,
        #     ## modelden sayfa silindikten sonra bu alttaki temizlikleri yapiyoruz artik..
        #     ## muhtemelen asagida view set parent none diyoruz, o esnada tabwidgetin o anki widgeti view oldugu icin
        #     ## tabwidget viewi kaybedince yerine de yenisi gelmeyince,ki
        #     ## tabwidget updatelerini kapamamaiza ragmen boyleydi..
        #     ## ...
        #     ## simdi model degistigi icin tabWidget in o anki widgeti da yeni model gore set ediliyor
        #     ## dolayısı ile alttakini silebiliyoruz.
        #     # del sayfa
        #     # scene.parent(None) yapmak, scene.undoStack lari temizlemiyor..
        #     # sayfa.scene.parent().undoGroup.blockSignals(True)
        #     scene.parent().undoGroup.removeStack(scene.undoStack)
        #     scene.undoStack.setParent(None)
        #     scene.undoStack.deleteLater()
        #     # sayfa.scene.parent().undoGroup.blockSignals(False)
        #
        #     view.setParent(None)
        #     scene.setParent(None)
        #     view.deleteLater()
        #     scene.deleteLater()

    # ---------------------------------------------------------------------
    def removeRowss(self, position, rows=1, index=QModelIndex()):
        print("\n\t\t ...removeRows() Starting position: '%s'" % position, 'with the total rows to be deleted: ', rows)
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self.items = self.items[:position] + self.items[position + rows:]
        self.endRemoveRows()

        return True

    # ---------------------------------------------------------------------
    def removeRows(self, row, count, parent: QModelIndex = None, *args, **kwargs):
        if row < 0 or row > self.rowCount():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)

        parentSayfa = self.sayfa_indexten(parent)
        # sayfa = parentSayfa.ic_sayfa(row)

        # parentSayfa.sayfa_sil(sayfa)
        print(parentSayfa)
        print(self.kokSayfa)
        print(parentSayfa == self.kokSayfa, "esitler imisler")
        sonuc = parentSayfa.sayfa_sil_sira_ile(row)

        self.endRemoveRows()
        self.layoutChanged.emit()
        return sonuc

        # node = self.sayfa_indexten(parent)
        # self.beginRemoveRows(parent, position,
        #                      position + count - 1)
        # for row in range(count):
        #     del node.children[position + row]
        # self.endRemoveRows()
        # return True

    # def insertColumns(self, p_int, parent=None, *args, **kwargs):
    #     self.beginInsertColumns()
    #     self.endInsertColumns()
    #
    # def removeColumns(self, p_int, p_int_1, parent=None, *args, **kwargs):
    #     self.beginRemoveColumns()
    #     self.endRemoveColumns()

    # ---------------------------------------------------------------------
    # diger
    # ---------------------------------------------------------------------

    # def roleNames(self):
    #     return self._roleNames

# class ListModel(QAbstractItemModel):
#
#     def __init__(self):
#         super().__init__()
#         self._items = []
#
#         meta = klass().metaObject()
#
#         self._roleNames = {}
#         for i in range(0, meta.propertyCount()):
#             self._roleNames[i] = meta.property(i).name()
#
#     def rowCount(self, parent=QModelIndex()):
#         return len(self._items)
#
#     def columnCount(self, parent=QModelIndex()):
#         return 1
#
#     def parent(self, index):
#         return QModelIndex()
#
#     def roleNames(self):
#         return self._roleNames
#
#     def data(self, index, role):
#         item = self._items[index.row()]
#         return item.property(self._roleNames[role])
#
#     @Slot(int, str, str)
#     def setProperty(self, index, prop, value):
#         item = self._items[index]
#         item.setProperty(prop, value)
#
#     def index(self, row, column=0, parent=QModelIndex()):
#         return self.createIndex(row, column, parent)
#
#     def append(self, item):
#         index = self.rowCount()
#         self.beginInsertRows(QModelIndex(), index, index)
#         self._items.append(item)
#         self.endInsertRows()
#
#     def update(self, index, item):
#         self._items[index] = item
#         self.dataChanged.emit(self.index(index), self.index(index))
#
#     def remove(self, item):
#         index = self._items.index(item)
#         self.beginRemoveRows(QModelIndex(), index, index)
#         self._items.remove(item)
#         self.endRemoveRows()
