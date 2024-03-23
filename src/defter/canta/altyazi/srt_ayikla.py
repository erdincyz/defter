# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'E.Y.'
__date__ = '14/03/2024'

from datetime import timedelta


########################################################################
class SrtAyikla:

    # ---------------------------------------------------------------------
    def __init__(self, dosya_adresi):

        self.dosya_adresi = dosya_adresi

        # self.blokSozluk = {}

        self.satirlar = []

        self.baslamaZamanlari = []
        self.bitisZamanlari = []
        self.yazilar = []

    # ---------------------------------------------------------------------
    def oku(self):
        with open(self.dosya_adresi, "r", encoding="utf-8") as f:
            self.satirlar = f.readlines()

    # # ---------------------------------------------------------------------
    # def sozluge_ayikla(self):
    #     self.oku()
    #     su_an_ki_sira = 0
    #
    #     i = 0
    #     for i in range (len(self.satirlar)):
    #         satir = self.satirlar[i].strip()
    #         if satir:
    #             if satir.isdigit():
    #                 satir_int = int(satir)
    #                 sonraki_sira_no_indexi = self.sonraki_sira_no_ve_indexi(i, satir_int)
    #                 self.boslari_temizle_blok_sozluge_ekle(satir_int,i+1,sonraki_sira_no_indexi)
    #                 i=sonraki_sira_no_indexi
    #                 continue
    #         i += 1
    #
    #     # print(self.blokSozluk)
    #     # for k,v in self.blokSozluk.items():
    #     #     print(k)
    #     #     print(v)

    # # ---------------------------------------------------------------------
    # def boslari_temizle_blok_sozluge_ekle(self, satir_int, z, sonraki_sira_no_indexi):
    #     # self.blokSozluk[satir_int] = (self.satirlar[i:sonraki_sira_no_indexi])
    #     blok_liste = []
    #     yazi = ""
    #     for y in range(z, sonraki_sira_no_indexi):
    #         satir = self.satirlar[y].strip()
    #         if satir:
    #             if not blok_liste:
    #                 bas,son =self.ilk_son_zaman_cevir(satir)
    #                 blok_liste.extend((bas,son))
    #             else:
    #                 yazi =f"{yazi} {satir}"
    #         y += 1
    #
    #     if yazi:
    #         blok_liste.append(yazi)
    #         self.blokSozluk[satir_int] = blok_liste

    # ---------------------------------------------------------------------
    def sonraki_altyazinin_sira_no_indexini_bul(self, su_an_ki_sira, satir_int):
        satir_int_arti_bir = satir_int + 1
        for i, satir in enumerate(self.satirlar[su_an_ki_sira:]):
            satir = satir.strip()
            if satir:
                if satir.isdigit():
                    satir_int = int(satir)
                    # TODO: burda mesela yazi satiri "10" olsa ve biz 9. altyaziyi ayikliyor olsak
                    # problem olabilir, dusuk de olsa ihtimal var.
                    # sonraki bir kaç satira da bakmak lazim
                    if satir_int == satir_int_arti_bir:
                        # mesela belki,
                        # if "-->" in self.satirlar[su_an_ki_sira + i + 1]:
                        #     break
                        break
        return i + su_an_ki_sira

    # ---------------------------------------------------------------------
    def listelere_ayikla(self):

        self.oku()

        i = 0
        while i < len(self.satirlar):
            satir = self.satirlar[i].strip()
            if satir:
                if satir.isdigit():
                    satir_int = int(satir)
                    sonraki_sira_no_indexi = self.sonraki_altyazinin_sira_no_indexini_bul(i, satir_int)
                    self.boslari_temizle_listelere_ekle(i + 1, sonraki_sira_no_indexi)
                    # i ve sonraki_sira_no_indexi arasindaki satirlar islendi listelere eklendi
                    # dolayisi ile i= sonraki_sira_no_indexi deyip, ordan devam ediyoruz
                    i = sonraki_sira_no_indexi
                    continue
            i += 1

        return self.baslamaZamanlari, self.yazilar, self.bitisZamanlari

    # ---------------------------------------------------------------------
    def boslari_temizle_listelere_ekle(self, blok_icerik_baslangic, sonraki_sira_no_indexi):
        # self.blokSozluk[satir_int] = (self.satirlar[i:sonraki_sira_no_indexi])
        # blok_liste = []
        yazi = ""
        bas = son = None
        for i in range(blok_icerik_baslangic, sonraki_sira_no_indexi):
            satir = self.satirlar[i].strip()
            if satir:
                if bas is None:
                    bas, son = self.ilk_son_zaman_cevir(satir)
                else:
                    yazi = f"{yazi} {satir}"
            i += 1

        if yazi:
            try:
                if yazi in self.yazilar[-1]:
                    self.yazilar[-1] = yazi
                    # self.baslamaZamanlari[-1] = bas
                    self.bitisZamanlari[-1] = son
                else:
                    self.yazilar.append(yazi)
                    self.baslamaZamanlari.append(bas)
                    self.bitisZamanlari.append(son)
            except IndexError:
                self.yazilar.append(yazi)
                self.baslamaZamanlari.append(bas)
                self.bitisZamanlari.append(son)

    # ---------------------------------------------------------------------
    def ilk_son_zaman_cevir(self, zaman):

        # :)
        zaman = zaman.replace(".", " ").replace(",", " ").replace(":", " ").replace("-->", " ")

        basH, basM, basS, basMs, sonH, sonM, sonS, sonMs = zaman.split()

        bas_ms = timedelta(hours=int(basH),
                           minutes=int(basM),
                           seconds=int(basS),
                           milliseconds=int(basMs)) // timedelta(milliseconds=1)

        son_ms = timedelta(hours=int(sonH),
                           minutes=int(sonM),
                           seconds=int(sonS),
                           milliseconds=int(sonMs)) // timedelta(milliseconds=1)

        return bas_ms, son_ms


# ---------------------------------------------------------------------
def calistir():
    # pass
    altyaziAdres = "altyazi2.srt"
    s = SrtAyikla(altyaziAdres)
    # bir_sey_dondurmuyor = s.sozluge_ayikla()
    basL, yaziL, sonL = s.listelere_ayikla()
    print(basL)
    print(yaziL)
    print(sonL)


# ---------------------------------------------------------------------
if __name__ == "__main__":
    calistir()
