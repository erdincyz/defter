# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

import os
import zipfile

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsItem

DEFTER_KLASOR_ADRES = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DEFTER_AYARLAR_DOSYA_ADRES = os.path.join(DEFTER_KLASOR_ADRES, "_settings.ini")
DEFTER_ORG_NAME = "defter"
DEFTER_ORG_DOMAIN = "defter"
DEFTER_APP_NAME = "Defter"

renk_degismis_nesne_yazi_rengi = QColor(232, 50, 120)
# renk_degismis_nesne_yazi_rengi = QColor(0,0,255)
renk_kirmizi = QColor(Qt.red)
renk_siyah = QColor(Qt.black)
renk_mavi = QColor(Qt.blue)
activeItemLineColor = QColor(Qt.red)

# bunlarin degerleri degismesin, cunku nesneler kaydedilirken bu degerler de kaydediliyor.
# sonra eski dosyalar acilmaz, degisiklik yapilirsa
userType = QGraphicsItem.UserType
BASE_ITEM_TYPE = userType + 1
RECT_ITEM_TYPE = userType + 2
ELLIPSE_ITEM_TYPE = userType + 3
IMAGE_ITEM_TYPE = userType + 4
PATH_ITEM_TYPE = userType + 5
TEXT_ITEM_TYPE = userType + 6
WEB_ITEM_TYPE = userType + 7
VIDEO_ITEM_TYPE = userType + 8
GROUP_ITEM_TYPE = userType + 9
MIRRORLINE_TYPE = userType + 10
TEMP_TEXT_ITEM_TYPE = userType + 11
KUTUPHANE_NESNESI = userType + 12
LINE_ITEM_TYPE = userType + 13
DOSYA_ITEM_TYPE = userType + 14
YUVARLAK_FIRCA_BOYUTU_ITEM_TYPE = userType + 15


# ---------------------------------------------------------------------
def unicode_to_bool(what):
    if what == "false" or what is False:
        return 0
    elif what == "true" or what is True:
        return 1


# ---------------------------------------------------------------------
def calculate_alpha(delta, col):
    alpha = col.alpha()

    if delta > 0:
        if alpha + 10 < 256:
            col.setAlpha(alpha + 10)
        else:
            col.setAlpha(255)
    else:
        if alpha - 10 > 0:
            col.setAlpha(alpha - 10)
        else:
            col.setAlpha(0)

    return col

    # return QColor().fromRgb(col.red(), col.green(),col.blue(),col.alpha())


# ---------------------------------------------------------------------
def ziple(zip_dosya_tam_adres, kaynak_klasor):
    # bunun yerine asagidaki zipfile tercih edildi.
    # cunku sıkıstırma oranı secebiliyoruz
    # shutil.make_archive(base_name=zippedFolderSavePath, format="zip", root_dir=tempDirPath)
    # shutil.make_archive ziplenmis dosya sonuna .zip ekliyor, ####.def.zip oluyor
    # os.rename("{}.zip".format(zippedFolderSavePath), zippedFolderSavePath)

    # kaynak_klasor kendisi haric sadece icini kaydediyoruz.
    len_kaynak_klasor = len(kaynak_klasor)
    with zipfile.ZipFile(zip_dosya_tam_adres, "w", zipfile.ZIP_STORED) as zipf:
        for root, dirs, files in os.walk(kaynak_klasor):
            # !! Olasi bos klasorleri eklememeyi tercih ettik !!
            #
            for dosya_adi in files:
                kaynak_dosya_tam_adres = os.path.join(root, dosya_adi)
                dosya_zip_icindeki_adres = kaynak_dosya_tam_adres[len_kaynak_klasor:]
                zipf.write(kaynak_dosya_tam_adres, dosya_zip_icindeki_adres)
