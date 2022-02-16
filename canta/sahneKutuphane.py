# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '25/Oct/2018'
__author__ = 'Erdinç Yılmaz'

import os
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QGraphicsScene
from canta import shared
from canta.nesneler.kutuphane_nesnesi import KutuphaneNesnesi

########################################################################
class SahneKutuphane(QGraphicsScene):
    # clean_changed = Signal(bool)
    # itemMoved = Signal(QGraphicsItem, QPointF)
    # textItemSelected = Signal(QGraphicsTextItem)

    # ---------------------------------------------------------------------
    def __init__(self, asil_sahne, sayfalar, tempDirPath, parent=None):
        super(SahneKutuphane, self).__init__(parent)

        self.asil_sahnedeki_dosya_isimleri = []

        self.sayfalar = sayfalar
        self.asil_sahne = asil_sahne
        self.tempDirPath = tempDirPath

        self.belge_olceginde_islem_yap = False

        self.suruklenmekte_olan_nesne = None

    # ---------------------------------------------------------------------
    def dragEnterEvent(self, e):
        # print(e)
        e.ignore()

    # ---------------------------------------------------------------------
    def dragMoveEvent(self, e):
        # print(e)
        e.acceptProposedAction()

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        mousePos = event.buttonDownScenePos(Qt.LeftButton)
        # self.movingItem = self.itemAt(mousePos)
        self.suruklenmekte_olan_nesne = self.itemAt(mousePos, self.views()[0].transform())
        # if self.suruklenmekte_olan_nesne:  # and event.button() == Qt.LeftButton
        super(SahneKutuphane, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def asil_sahnedeki_linkli_dosya_adresleri(self):
        kume = set()
        for item in self.asil_sahne.items():
            if item.type() == shared.IMAGE_ITEM_TYPE and not item.isEmbeded:
                kume.add(item.filePathForSave)
        return kume

    # ---------------------------------------------------------------------
    def asil_sahnedeki_gomulu_dosya_adresleri(self):
        kume = set()
        for item in self.asil_sahne.items():
            if item.type() == shared.IMAGE_ITEM_TYPE and item.isEmbeded:
                kume.add(item.filePathForSave)
        return kume

    # ---------------------------------------------------------------------
    def _belgedeki_linkli_dosya_adresleri(self):
        # yukardakileri kullanmiyoruz cunku her bir sayfa icin yeni kume olusturma falan
        # gerkesiz belki ama boyle daha hizli

        kume = set()

        for sayfa in self.sayfalar:
            for item in sayfa.scene.items():
                if item.type() == shared.IMAGE_ITEM_TYPE and not item.isEmbeded:
                    kume.add(item.filePathForSave)
        return kume

    # ---------------------------------------------------------------------
    def butun_sahnedelerdeki_gomulu_dosya_adresleri(self):
        """ bu belgedeki butun gomulu olanlardan farklı """
        # yukardakileri kullanmiyoruz cunku her bir sayfa icin yeni kume olusturma falan
        # gerkesiz belki ama boyle daha hizli
        kume = set()

        for sayfa in self.sayfalar:
            for item in sayfa.scene.items():
                if item.type() == shared.IMAGE_ITEM_TYPE and item.isEmbeded:
                    kume.add(item.filePathForSave)
        return kume

    # ---------------------------------------------------------------------
    def belgedeki_gomulu_dosya_adresleri(self):
        self.belge_olceginde_islem_yap = True
        # bunu inite tasima sayfa ve dokuman degistikce self.tempDirPath degisiyor.
        # self yapilcaksa, self.tempDirPath property yapilmali
        images_klasoru = os.path.join(self.tempDirPath, "images", "")

        kume = set()
        try:
            for f in os.listdir(images_klasoru):
                kume.add(os.path.join(images_klasoru, f))
        except FileNotFoundError:
            print("FileNotFoundError: ", images_klasoru)
        return kume

    # ---------------------------------------------------------------------
    def belgedeki_html_imaj_adresleri(self):
        self.belge_olceginde_islem_yap = True
        # bunu inite tasima sayfa ve dokuman degistikce self.tempDirPath degisiyor.
        # self yapilcaksa, self.tempDirPath property yapilmali
        images_html_klasoru = os.path.join(self.tempDirPath, "images-html", "")

        kume = set()
        try:
            for f in os.listdir(images_html_klasoru):
                kume.add(os.path.join(images_html_klasoru, f))
        except FileNotFoundError:
            print("FileNotFoundError: ", images_html_klasoru)
        return kume

    # ---------------------------------------------------------------------
    def belgedeki_linkli_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = True
        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        belgedeki_linkli_dosya_adresleri = self._belgedeki_linkli_dosya_adresleri()

        for dosya_adresi in belgedeki_linkli_dosya_adresleri:
            print("asdasd", dosya_adresi)
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi, isEmbeded=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

    # ---------------------------------------------------------------------
    def sahnedeki_linkli_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = False
        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        for dosya_adresi in self.asil_sahnedeki_linkli_dosya_adresleri():
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi, isEmbeded=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

    # ---------------------------------------------------------------------
    def belgedeki_linkli_ve_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = True
        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        belgedeki_linkli_dosya_adresleri = self._belgedeki_linkli_dosya_adresleri()

        for dosya_adresi in belgedeki_linkli_dosya_adresleri:
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi, isEmbeded=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

        for dosya_adresi in self.belgedeki_gomulu_dosya_adresleri():
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

    # ---------------------------------------------------------------------
    def sahnedeki_linkli_ve_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = False

        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        for dosya_adresi in self.asil_sahnedeki_gomulu_dosya_adresleri():
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

        for dosya_adresi in self.asil_sahnedeki_linkli_dosya_adresleri():
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi, isEmbeded=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

    # ---------------------------------------------------------------------
    def belgedeki_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = True
        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        # for item in self.asil_sahne.items():
        #     if item.type() == shared.IMAGE_ITEM_TYPE:
        #         kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=item.filePathForSave)
        #         self.addItem(kutuphane_nesnesi)
        #         pos.setX(pos.x()+50)
        #         if sayac % 5 == 0:
        #             pos.setX(5)
        #             pos.setY(pos.y()+50)
        #         sayac += 1

        # bunu inite tasima sayfa ve dokuman degistikce self.tempDirPath degisiyor.
        # self yapilcaksa, self.tempDirPath property yapilmali

        butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi = self.butun_sahnedelerdeki_gomulu_dosya_adresleri()
        asil_sahnedeki_gomulu_dosya_adresleri_kumesi = self.asil_sahnedeki_gomulu_dosya_adresleri()

        images_klasoru = os.path.join(self.tempDirPath, "images", "")

        try:
            for f in os.listdir(images_klasoru):
                tam_adres = os.path.join(images_klasoru, f)
                if tam_adres in butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi:
                    belgede_kullaniliyor_mu = True
                else:
                    belgede_kullaniliyor_mu = False
                if tam_adres in asil_sahnedeki_gomulu_dosya_adresleri_kumesi:
                    sahnede_kullaniliyor_mu = True
                else:
                    sahnede_kullaniliyor_mu = False
                kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=tam_adres,
                                                     sahnede_kullaniliyor_mu=sahnede_kullaniliyor_mu,
                                                     belgede_kullaniliyor_mu=belgede_kullaniliyor_mu)
                self.addItem(kutuphane_nesnesi)
                pos.setX(pos.x() + 50)
                if sayac % 5 == 0:
                    pos.setX(5)
                    pos.setY(pos.y() + 50)
                sayac += 1
        except FileNotFoundError:
            print("FileNotFoundError: ", images_klasoru)

    # ---------------------------------------------------------------------
    def sahnedeki_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = False

        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        for dosya_adresi in self.asil_sahnedeki_gomulu_dosya_adresleri():
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

    # ---------------------------------------------------------------------
    def sahnede_kullanilmayan_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = False

        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        belgedeki_gomulu_dosya_adresleri_kumesi = self.belgedeki_gomulu_dosya_adresleri()
        sahnedeki_gomulu_dosya_adresleri_kumesi = self.asil_sahnedeki_gomulu_dosya_adresleri()

        fark_liste = list(belgedeki_gomulu_dosya_adresleri_kumesi - sahnedeki_gomulu_dosya_adresleri_kumesi)

        for dosya_adresi in fark_liste:
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi, sahnede_kullaniliyor_mu=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

    # ---------------------------------------------------------------------
    def belgede_kullanilmayan_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = True

        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        belgedeki_gomulu_dosya_adresleri_kumesi = self.belgedeki_gomulu_dosya_adresleri()

        butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi = self.butun_sahnedelerdeki_gomulu_dosya_adresleri()

        print(belgedeki_gomulu_dosya_adresleri_kumesi)
        print(butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi)

        fark_liste = list(belgedeki_gomulu_dosya_adresleri_kumesi - butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi)

        for dosya_adresi in fark_liste:
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=dosya_adresi, belgede_kullaniliyor_mu=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

    # ---------------------------------------------------------------------
    def kullanilmayanlari_isaretle(self):

        if self.belge_olceginde_islem_yap:

            belgedeki_gomulu_dosya_adresleri_kumesi = self.belgedeki_gomulu_dosya_adresleri()
            butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi = self.butun_sahnedelerdeki_gomulu_dosya_adresleri()

            fark_liste = list(
                belgedeki_gomulu_dosya_adresleri_kumesi - butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi)

            for nesne in self.items():
                if nesne.dosya_adresi in fark_liste:
                    nesne.belgede_kullaniliyor_mu = False
                    nesne.update()
        else:
            gomulu_dosya_adresleri_kumesi = self.asil_sahnedeki_gomulu_dosya_adresleri()
            for nesne in self.items():
                if nesne.dosya_adresi in gomulu_dosya_adresleri_kumesi:
                    continue
                nesne.sahnede_kullaniliyor_mu = False
                nesne.update()

    # ---------------------------------------------------------------------
    def secilen_nesneleri_sil(self):
        gomulu_dosya_isimleri_kumesi = self.asil_sahnedeki_gomulu_dosya_adresleri()
        for nesne in self.selectedItems():
            if nesne.dosya_adresi in gomulu_dosya_isimleri_kumesi:
                continue
            os.unlink(nesne.dosya_adresi)
            self.removeItem(nesne)

    # ---------------------------------------------------------------------
    def belgede_kullanilmayan_gomulu_dosyalari_sil(self):
        belgedeki_gomulu_dosya_adresleri_kumesi = self.belgedeki_gomulu_dosya_adresleri()

        butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi = self.butun_sahnedelerdeki_gomulu_dosya_adresleri()

        fark_liste = list(belgedeki_gomulu_dosya_adresleri_kumesi - butun_sahnedelerdeki_gomulu_dosya_adresleri_kumesi)

        for dosya_adresi in fark_liste:
            print("siliniyor", dosya_adresi)
            os.remove(dosya_adresi)

    # ---------------------------------------------------------------------
    def belgedeki_html_imajlari_goster(self):
        self.belge_olceginde_islem_yap = True
        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        belgedeki_html_imaj_adresleri = self.belgedeki_html_imaj_adresleri()

        for html_imaj_adresi in belgedeki_html_imaj_adresleri:
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, dosya_adresi=html_imaj_adresi, isHtmlImage=True,
                                                 isEmbeded=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1
