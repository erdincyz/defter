# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '25/Oct/2018'
__author__ = 'Erdinç Yılmaz'

import os

from shiboken6 import Shiboken
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QGraphicsScene
from . import shared
from .nesneler.kutuphane_nesnesi import KutuphaneNesnesi


#######################################################################
class Eleman:
    # ---------------------------------------------------------------------
    def __init__(self, tip, adres):
        self.tip = tip
        self.adres = adres

    # ---------------------------------------------------------------------
    def __hash__(self):
        return hash(self.adres)

    # ---------------------------------------------------------------------
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        # burda None==None mevzuu olabilir ama bizde none adres yok.
        return self.adres == other.adres and self.tip == other.tip


########################################################################
class SahneKutuphane(QGraphicsScene):

    # ---------------------------------------------------------------------
    def __init__(self, aktif_sahne, sayfalar, tempDirPath, parent=None):
        super(SahneKutuphane, self).__init__(parent)

        self.aktif_sahnedeki_dosya_isimleri = []

        self.sayfalar = sayfalar
        self.aktif_sahne = aktif_sahne
        self.tempDirPath = tempDirPath

        self.sonZDeger = 0

        self.belge_olceginde_islem_yap = False

        self.suruklenmekte_olan_nesne = None

        self.desteklenen_tipler = [shared.IMAGE_ITEM_TYPE, shared.VIDEO_ITEM_TYPE, shared.DOSYA_ITEM_TYPE]

    # ---------------------------------------------------------------------
    def tum_nesneleri_sil(self):
        # self.clear()
        for nesne in self.items():
            if Shiboken.isValid(nesne):
                Shiboken.delete(nesne)
                # print(Shiboken.isValid(nesne))
                # del nesne
        # print(len(self.items()))

    # ---------------------------------------------------------------------
    def zDeger_arttir(self, nesne):
        self.sonZDeger += 1
        nesne.setZValue(self.sonZDeger)

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
        mousePos = event.buttonDownScenePos(Qt.MouseButton.LeftButton)
        # self.movingItem = self.itemAt(mousePos)
        self.suruklenmekte_olan_nesne = self.itemAt(mousePos, self.views()[0].transform())
        # if self.suruklenmekte_olan_nesne:  # and event.button() == Qt.LeftButton
        super(SahneKutuphane, self).mousePressEvent(event)

    # ---------------------------------------------------------------------
    def aktif_sahnedeki_linkli_dosya_adresleri(self):
        kume = set()

        for item in self.aktif_sahne.items():
            if item.type() in self.desteklenen_tipler:
                if not item.isEmbeded:
                    kume.add(Eleman(tip=item.type(), adres=item.filePathForSave))
        return kume

    # ---------------------------------------------------------------------
    def tum_sahnelerdeki_linkli_dosya_adresleri(self):
        kume = set()

        for sayfa in self.sayfalar:
            for item in sayfa.scene.items():
                if item.type() in self.desteklenen_tipler:
                    if not item.isEmbeded:
                        kume.add(Eleman(tip=item.type(), adres=item.filePathForSave))
        return kume

    # ---------------------------------------------------------------------
    def aktif_sahnedeki_gomulu_dosya_adresleri(self):
        kume = set()

        for item in self.aktif_sahne.items():
            if item.type() in self.desteklenen_tipler:
                if item.isEmbeded:
                    kume.add(Eleman(tip=item.type(), adres=item.filePathForSave))
        return kume

    # ---------------------------------------------------------------------
    def tum_sahnelerdeki_gomulu_dosya_adresleri(self):
        """ bu belgedeki butun gomulu olanlardan farklı """
        # yukardakileri kullanmiyoruz cunku her bir sayfa icin yeni kume olusturma falan
        # gerkesiz belki ama boyle daha hizli
        kume = set()

        for sayfa in self.sayfalar:
            for item in sayfa.scene.items():
                if item.type() in self.desteklenen_tipler:
                    if item.isEmbeded:
                        kume.add(Eleman(tip=item.type(), adres=item.filePathForSave))
            if sayfa.view.backgroundImagePathIsEmbeded:
                kume.add(Eleman(tip=shared.IMAGE_ITEM_TYPE, adres=sayfa.view.backgroundImagePath))
        return kume

    # ---------------------------------------------------------------------
    def diskteki_tum_gomulu_dosya_adresleri(self):
        self.belge_olceginde_islem_yap = True
        # bunu inite tasima sayfa ve dokuman degistikce self.tempDirPath degisiyor.
        # self yapilcaksa, self.tempDirPath property yapilmali
        resimler_klasoru = os.path.join(self.tempDirPath, "images", "")
        videolar_klasoru = os.path.join(self.tempDirPath, "videos", "")
        dosyalar_klasoru = os.path.join(self.tempDirPath, "files", "")

        kume = set()
        try:
            for f in os.listdir(resimler_klasoru):
                kume.add((Eleman(tip=shared.IMAGE_ITEM_TYPE,
                                 adres=os.path.join(resimler_klasoru, f))))
        except FileNotFoundError:
            pass
            # print("FileNotFoundError: ", resimler_klasoru)

        try:
            for f in os.listdir(videolar_klasoru):
                kume.add((Eleman(tip=shared.VIDEO_ITEM_TYPE,
                                 adres=os.path.join(videolar_klasoru, f))))
        except FileNotFoundError:
            pass
            # print("FileNotFoundError: ", videolar_klasoru)

        try:
            for f in os.listdir(dosyalar_klasoru):
                kume.add((Eleman(tip=shared.DOSYA_ITEM_TYPE,
                                 adres=os.path.join(dosyalar_klasoru, f))))
        except FileNotFoundError:
            pass
            # print("FileNotFoundError: ", dosyalar_klasoru)

        return kume

    # ---------------------------------------------------------------------
    def diskteki_html_imaj_adresleri(self):
        self.belge_olceginde_islem_yap = True
        # bunu inite tasima sayfa ve dokuman degistikce self.tempDirPath degisiyor.
        # self yapilcaksa, self.tempDirPath property yapilmali
        images_html_klasoru = os.path.join(self.tempDirPath, "images-html", "")

        kume = set()
        try:
            for f in os.listdir(images_html_klasoru):
                kume.add(os.path.join(images_html_klasoru, f))
        except FileNotFoundError:
            pass
            # print("FileNotFoundError: ", images_html_klasoru)
        return kume

    # ---------------------------------------------------------------------
    def sahnedeki_linkli_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = False
        self.clear()

        self._dosyalari_goster(self.aktif_sahnedeki_linkli_dosya_adresleri(),
                               isEmbeded=False)

    # ---------------------------------------------------------------------
    def sahnedeki_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = False
        self.clear()

        self._dosyalari_goster(self.aktif_sahnedeki_gomulu_dosya_adresleri(),
                               isEmbeded=True)

    # ---------------------------------------------------------------------
    def belgedeki_linkli_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = True
        self.clear()

        self._dosyalari_goster(self.tum_sahnelerdeki_linkli_dosya_adresleri(),
                               isEmbeded=False)

    # ---------------------------------------------------------------------
    def belgedeki_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = True
        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        diskteki_tum_gomulu_dosya_adresleri_kumesi = self.diskteki_tum_gomulu_dosya_adresleri()
        toplam_kume_tum_sahneler = self.tum_sahnelerdeki_gomulu_dosya_adresleri()
        toplam_kume_aktif_sahne = self.aktif_sahnedeki_gomulu_dosya_adresleri()

        for eleman in diskteki_tum_gomulu_dosya_adresleri_kumesi:
            if eleman in toplam_kume_tum_sahneler:
                belgede_kullaniliyor_mu = True
            else:
                belgede_kullaniliyor_mu = False
            if eleman in toplam_kume_aktif_sahne:
                sahnede_kullaniliyor_mu = True
            else:
                sahnede_kullaniliyor_mu = False

            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, tip=eleman.tip,
                                                 dosya_adresi=eleman.adres,
                                                 sahnede_kullaniliyor_mu=sahnede_kullaniliyor_mu,
                                                 belgede_kullaniliyor_mu=belgede_kullaniliyor_mu,
                                                 isEmbeded=True)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

        self.setSceneRect(0, 0, 250, pos.y())

    # ---------------------------------------------------------------------
    def _dosyalari_goster(self, kume, isEmbeded, pozisyonSifirla=True):

        self.sonZDeger = 0

        if pozisyonSifirla:
            pos = QPoint(5, 5)
            self.enSonElemanPos = pos
        else:
            pos = self.enSonElemanPos
        sayac = 1
        for eleman in kume:
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, tip=eleman.tip,
                                                 dosya_adresi=eleman.adres,
                                                 isEmbeded=isEmbeded)
            self.zDeger_arttir(kutuphane_nesnesi)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

        self.enSonElemanPos = pos

        # self.setSceneRect(self.itemsBoundingRect())
        # self.views()[0].zoomToFit()
        self.setSceneRect(0, 0, 250, pos.y())

    # ---------------------------------------------------------------------
    def belgedeki_linkli_ve_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = True
        self.clear()

        self._dosyalari_goster(self.tum_sahnelerdeki_linkli_dosya_adresleri(),
                               isEmbeded=False, pozisyonSifirla=True)

        self._dosyalari_goster(self.tum_sahnelerdeki_gomulu_dosya_adresleri(),
                               isEmbeded=True, pozisyonSifirla=False)

    # ---------------------------------------------------------------------
    def sahnedeki_linkli_ve_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = False
        self.clear()

        self._dosyalari_goster(self.aktif_sahnedeki_linkli_dosya_adresleri(),
                               isEmbeded=False, pozisyonSifirla=True)

        self._dosyalari_goster(self.aktif_sahnedeki_gomulu_dosya_adresleri(),
                               isEmbeded=True, pozisyonSifirla=False)

    # ---------------------------------------------------------------------
    def sahnede_kullanilmayan_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = False

        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        diskteki_tum_gomulu_dosya_adresleri_kumesi = self.diskteki_tum_gomulu_dosya_adresleri()
        toplam_kume = self.aktif_sahnedeki_gomulu_dosya_adresleri()

        fark_liste = list(diskteki_tum_gomulu_dosya_adresleri_kumesi - toplam_kume)

        for eleman in fark_liste:
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, tip=eleman.tip,
                                                 dosya_adresi=eleman.adres,
                                                 sahnede_kullaniliyor_mu=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

        self.setSceneRect(0, 0, 250, pos.y())

    # ---------------------------------------------------------------------
    def belgede_kullanilmayan_gomulu_dosyalari_goster(self):
        self.belge_olceginde_islem_yap = True

        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        diskteki_tum_gomulu_dosya_adresleri_kumesi = self.diskteki_tum_gomulu_dosya_adresleri()
        toplam_kume = self.tum_sahnelerdeki_gomulu_dosya_adresleri()

        fark_liste = list(diskteki_tum_gomulu_dosya_adresleri_kumesi - toplam_kume)
        for eleman in fark_liste:
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, tip=eleman.tip,
                                                 dosya_adresi=eleman.adres,
                                                 belgede_kullaniliyor_mu=False)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

        self.setSceneRect(0, 0, 250, pos.y())

    # ---------------------------------------------------------------------
    def kullanilmayanlari_isaretle(self):

        if self.belge_olceginde_islem_yap:

            diskteki_tum_gomulu_dosya_adresleri_kumesi = self.diskteki_tum_gomulu_dosya_adresleri()
            toplam_kume = self.tum_sahnelerdeki_gomulu_dosya_adresleri()
            fark_liste = list(diskteki_tum_gomulu_dosya_adresleri_kumesi - toplam_kume)
            fark_liste_adresler = [eleman.adres for eleman in fark_liste]

            for nesne in self.items():
                if nesne.dosya_adresi in fark_liste_adresler:
                    nesne.belgede_kullaniliyor_mu = False
                    nesne.update()
        else:
            toplam_kume = self.aktif_sahnedeki_gomulu_dosya_adresleri()
            toplam_kume_adresler = [eleman.adres for eleman in toplam_kume]
            for nesne in self.items():
                if nesne.dosya_adresi in toplam_kume_adresler:
                    continue
                nesne.sahnede_kullaniliyor_mu = False
                nesne.update()

    # ---------------------------------------------------------------------
    def secilen_nesneleri_sil(self):
        toplam_kume = self.aktif_sahnedeki_gomulu_dosya_adresleri()

        adresler = [eleman.adres for eleman in toplam_kume]

        for nesne in self.selectedItems():
            if nesne.dosya_adresi in adresler:
                continue
            os.unlink(nesne.dosya_adresi)
            self.removeItem(nesne)

    # ---------------------------------------------------------------------
    def belgede_kullanilmayan_gomulu_dosyalari_listele(self):
        diskteki_tum_gomulu_dosya_adresleri_kumesi = self.diskteki_tum_gomulu_dosya_adresleri()

        toplam_kume = self.tum_sahnelerdeki_gomulu_dosya_adresleri()

        fark_liste = list(diskteki_tum_gomulu_dosya_adresleri_kumesi - toplam_kume)

        return fark_liste

    # ---------------------------------------------------------------------
    def belgede_kullanilmayan_gomulu_dosyalari_sil(self, liste):
        if liste:
            for eleman in liste:
                try:
                    os.remove(eleman.adres)
                    self.parent().log(f"Dosya silindi: {eleman.adres}", level=1, toLogOnly=True)
                except Exception as e:
                    msj = f"HATA: Dosya silinemedi : {eleman.adres} {e}"
                    self.parent().log(msj, level=3, toLogOnly=True)
                    print(msj)

            self.parent().log(f"{len(liste)} adet dosya başarı ile silindi", level=1)

    # ---------------------------------------------------------------------
    def belgedeki_html_imajlari_goster(self):
        self.belge_olceginde_islem_yap = True
        self.clear()
        pos = QPoint(5, 5)
        sayac = 1

        diskteki_html_imaj_adresleri = self.diskteki_html_imaj_adresleri()

        for html_imaj_adresi in diskteki_html_imaj_adresleri:
            kutuphane_nesnesi = KutuphaneNesnesi(pos=pos, tip=shared.IMAGE_ITEM_TYPE,
                                                 dosya_adresi=html_imaj_adresi,
                                                 isHtmlImage=True,
                                                 isEmbeded=True)
            self.addItem(kutuphane_nesnesi)
            pos.setX(pos.x() + 50)
            if sayac % 5 == 0:
                pos.setX(5)
                pos.setY(pos.y() + 50)
            sayac += 1

        self.setSceneRect(0, 0, 250, pos.y())
