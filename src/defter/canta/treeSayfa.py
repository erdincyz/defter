# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '01/Jun/2018'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from .shared import kim, slugify


########################################################################
class Sayfa(object):
    # class Sayfa(QObject):
    sayfa_no = 0  # 0 kok sayfaya gidiyor

    # ---------------------------------------------------------------------
    def __init__(self, adi=None, ikon=None, scene=None, view=None, parent=None):
        # super(Sayfa, self).__init__(parent)
        # self.setParent(parent)
        self._ic_sayfalar = []

        # print("sayfa parent", parent)

        # self.sayfaParent = parent

        self._parent = parent
        self._scene = scene
        self._view = view
        self._ikon = ikon

        self._kim = kim(kac_basamak=16)

        self._no = Sayfa.sayfa_no
        self._adi = "{} - {}".format(adi, self._no)
        # @adi.setter da temizleniyor, bu ilk olusturma
        self._kayit_adi = "{} - {}".format(slugify(self._adi, False), self._kim)

        # print(self.adi)

        Sayfa.sayfa_no += 1

        # #TODO: bu parent sayfa mı kontrol etmek lazım. bu herhangi bir nesne tip gelirse de calışır aşağıki kod yoksa
        # bu olmaz modelin kok sayfasına ekleyemeyiz burdan, parent none ise..
        # if parent is not None:
        #     parent.sayfa_ekle(self)

    # @pyqtProperty(str)
    @property
    def adi(self):
        return self._adi

    @adi.setter
    def adi(self, adi):
        self._adi = adi
        self._kayit_adi = "{} - {}".format(slugify(self._adi, False), self._kim)

    # @pyqtProperty(str)
    @property
    def ikon(self):
        return self._ikon

    @ikon.setter
    def ikon(self, ikon):
        self._ikon = ikon

    # @pyqtProperty(Scene)
    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, scene):
        self._scene = scene

    # @pyqtProperty(View)
    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, view):
        self._view = view

    # ---------------------------------------------------------------------
    def ustSayfa(self):
        return self._parent

    # ---------------------------------------------------------------------
    def parent(self):
        return self._parent

    # # ---------------------------------------------------------------------
    # def setUstSayfa(self, parent):
    #     self._parent = parent

    # ---------------------------------------------------------------------
    def ic_sayfa_var_mi(self):
        return bool(len(self._ic_sayfalar))

    # ---------------------------------------------------------------------
    def satirSayisi(self):
        return len(self._ic_sayfalar)

        # if self.parentItem:
        #     return self.parentItem.childItems.index(self)
        # return 0

    # ---------------------------------------------------------------------
    def sutunSayisi(self):
        # return len(self.itemData)
        return 1

    # ---------------------------------------------------------------------
    def ic_sayfalar(self):
        return self._ic_sayfalar

    # ---------------------------------------------------------------------
    def ic_sayfa(self, satir):
        # print(self.ic_sayfalar(), satir)
        # if self.ic_sayfalar():
        #     return self._ic_sayfalar[satir]
        return self._ic_sayfalar[satir]

    # ---------------------------------------------------------------------
    # def parent(self):
    #     return self.parent()

    # def __len__(self):
    #     return len(self._ic_sayfalar)

    # ---------------------------------------------------------------------
    def satir(self):  # row
        if self.parent():
            return self.parent().ic_sayfalar().index(self)  # bu index python liste indexi

        return 0  # kokSayfa

    # ---------------------------------------------------------------------
    def sutun(self):  # column
        return 1

    # # ---------------------------------------------------------------------
    # modelden silip eklemek , removeRow insertRow ile daha saglikli.
    # def sayfa_sira_degistir(self, sayfa, hedefSira):
    #     # sayfa = self._ic_sayfalar.pop(self._ic_sayfalar.index(sayfa))
    #     self._ic_sayfalar.remove(sayfa)
    #     self._ic_sayfalar.insert(hedefSira, sayfa)

    # ---------------------------------------------------------------------
    def sayfa_ekle(self, sayfa):
        # TODO: if not mantikli mi???
        if sayfa not in self._ic_sayfalar:
            self._ic_sayfalar.append(sayfa)
            # self._ic_sayfalar.append(sayfa)
            sayfa._parent = self
            # print(sayfa.ikon)
            return True

    #
    # def childAtRow(self, row):
    #     """The row-th child of this node."""
    #
    #     assert 0 <= row <= len(self.children)
    #     return self.children[row]
    #
    # def insertChild(self, child, position=0):
    #     """Insert a child in a group node."""
    #     self.children.insert(position, child)

    # ---------------------------------------------------------------------
    def sayfa_araya_ekle(self, satir, sayfa):
        # TODO: if not mantikli mi???
        if satir < 0 or satir > len(self._ic_sayfalar):
            return False

        self._ic_sayfalar.insert(satir, sayfa)
        sayfa._parent = self
        return True

    # ---------------------------------------------------------------------
    def sayfa_sil(self, sayfa):
        if sayfa in self._ic_sayfalar:
            self._ic_sayfalar.remove(sayfa)
            return True
        return False

    # ---------------------------------------------------------------------
    def sayfa_sil_sira_ile(self, sira):

        if sira < 0 or sira > len(self._ic_sayfalar):
            return False
        sayfa = self._ic_sayfalar.pop(sira)
        # sayfa.setParent(None)  # QObject oldugu icin
        # del sayfa
        return True

    # # ---------------------------------------------------------------------
    # def __eq__(self, other):
    #
    #     print(type(self), type(other))
    #     if other:
    #         return self.__dict__ == other.__dict__
    #     return False
    #
    # # ---------------------------------------------------------------------
    # def __ne__(self, other):
    #     if other is not self:
    #         return False
    #     return self.__dict__ != other.__dict__
