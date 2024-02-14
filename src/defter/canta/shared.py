# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

import os
from unicodedata import normalize
from re import sub
from uuid import uuid4

from PySide6.QtCore import Qt, QRectF, QSizeF
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush, QTransform
from PySide6.QtWidgets import QGraphicsItem

DEFTER_KLASOR_ADRES = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DEFTER_AYARLAR_DOSYA_ADRES = os.path.join(DEFTER_KLASOR_ADRES, "_ayarlar.ini")
DEFTER_AYARLAR_ARACLAR_DOSYA_ADRES = os.path.join(DEFTER_KLASOR_ADRES, "_ayarlar_araclar.ini")
DEFTER_ORG_NAME = "argekod"
DEFTER_ORG_DOMAIN = "argekod.com"
DEFTER_APP_NAME = "Defter"

renk_degismis_nesne_yazi_rengi = QColor(232, 50, 120)
# renk_degismis_nesne_yazi_rengi = QColor(0,0,255)
renk_kirmizi = QColor(Qt.GlobalColor.red)
renk_siyah = QColor(Qt.GlobalColor.black)
renk_mavi = QColor(Qt.GlobalColor.blue)
activeItemLineColor = QColor(Qt.GlobalColor.red)

handleBrushAcik = QBrush(QColor(250, 250, 250))
handleBrushKoyu = QBrush(QColor(25, 25, 25))

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
def kim(kac_basamak):
    # veya str(uuid.uuid4())[:5] yerine uuid.uuid4().hex[:5]
    return uuid4().hex[:kac_basamak]


# ---------------------------------------------------------------------
def slugify(value, allow_unicode=False):
    # veya = "".join([x if x.isalnum() else "_" for x in value])
    # return veya
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = normalize('NFKC', value)
    else:
        value = normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = sub(r'[^\w\s-]', '', value.lower())
    return sub(r'[-\s]+', '-', value).strip('-_')


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
def kutulu_arkaplan_olustur(widget, kareBoyutu=10):
    kb = kareBoyutu

    pMap = QPixmap(2 * kb, 2 * kb)
    p = QPainter(pMap)
    p.fillRect(0, 0, kb, kb, QColor(200, 200, 200))
    p.fillRect(kb, kb, kb, kb, QColor(210, 210, 210))
    p.fillRect(0, kb, kb, kb, QColor(190, 190, 190))
    p.fillRect(kb, 0, kb, kb, QColor(200, 200, 200))
    p.end()
    palette = widget.palette()
    palette.setBrush(widget.backgroundRole(), QBrush(pMap))
    widget.setAutoFillBackground(True)
    widget.setPalette(palette)


# ---------------------------------------------------------------------
def _scaleChildItemsByResizing(nesne, scaleFactorX, scaleFactorY=None, resizeGroup=False):
    if not scaleFactorY:
        scaleFactorY = scaleFactorX

    if nesne.type() == GROUP_ITEM_TYPE and resizeGroup:
        childItems = nesne.allFirstLevelGroupChildren
    else:
        childItems = nesne.childItems()

    for c in childItems:
        if c.childItems():
            _scaleChildItemsByResizing(c, scaleFactorX)

        if c.type() == TEXT_ITEM_TYPE:

            # c.setTransformOriginPoint(c.boundingRect().center())
            fontPointSizeF = c.fontPointSizeF() * scaleFactorX
            c.setFontPointSizeF(fontPointSizeF)
            c.yazi_kutusunu_daralt()

        elif c.type() == GROUP_ITEM_TYPE:
            # rect = QRectF(c._rect.topLeft(), c._rect.size() * scaleFactorX)
            # rect.moveTo(0, 0)
            w = c.rect().width() * scaleFactorX
            h = c.rect().height() * scaleFactorY
            rect = QRectF(0, 0, w, h)
            c._rect = rect
            c.update_resize_handles()

        elif c.type() == PATH_ITEM_TYPE:
            scaleMatrix = QTransform()
            scaleMatrix.scale(scaleFactorX, scaleFactorY)
            scaledPath = c.path() * scaleMatrix
            c.setPath(scaledPath)

            c.update_resize_handles()
            c.update_painter_text_rect()

        elif c.type() == LINE_ITEM_TYPE:
            scaleMatrix = QTransform()
            scaleMatrix.scale(scaleFactorX, scaleFactorY)
            scaledLine = c.line() * scaleMatrix
            c.setLine(scaledLine)

            c.update_resize_handles()
            c.update_painter_text_rect()

        else:
            # rect = QRectF(c.rect().topLeft(), c.rect().size() * scaleFactorX)
            w = c.rect().width() * scaleFactorX
            h = c.rect().height() * scaleFactorY
            rect = QRectF(0, 0, w, h)
            c.setRect(rect)

            c.update_resize_handles()
            c.update_painter_text_rect()

        c.setX(c.x() * scaleFactorX)
        c.setY(c.y() * scaleFactorY)
        # c.setX((c.x() + fark.x()) * scaleFactorX)
        # c.setY((c.y() + fark.y()) * scaleFactorY)
        # c.moveBy(fark.x(), fark.y() )


# # ---------------------------------------------------------------------
# def _scaleChildItemsByResizing(nesne, scaleFactor):
#     for c in nesne.childItems():
#         if c.childItems():
#             _scaleChildItemsByResizing(c, scaleFactor)
#
#         if c.type() == TEXT_ITEM_TYPE:
#
#             # c.setTransformOriginPoint(c.boundingRect().center())
#             fontPointSizeF = c.fontPointSizeF() * scaleFactor
#             c.setFontPointSizeF(fontPointSizeF)
#             c.yazi_kutusunu_daralt()
#
#         elif c.type() == GROUP_ITEM_TYPE:
#             rect = QRectF(c._rect.topLeft(), c._rect.size() * scaleFactor)
#             rect.moveTo(0, 0)
#             c._rect = rect
#
#         elif c.type() == PATH_ITEM_TYPE:
#             scaleMatrix = QTransform()
#             scaleMatrix.scale(scaleFactor, scaleFactor)
#             scaledPath = c.path() * scaleMatrix
#             c.setPath(scaledPath)
#
#             c.update_resize_handles()
#             c.update_painter_text_rect()
#
#         elif c.type() == LINE_ITEM_TYPE:
#             scaleMatrix = QTransform()
#             scaleMatrix.scale(scaleFactor, scaleFactor)
#             scaledLine = c.line() * scaleMatrix
#             c.setLine(scaledLine)
#
#             c.update_resize_handles()
#             c.update_painter_text_rect()
#
#         else:
#             rect = QRectF(c.rect().topLeft(), c.rect().size() * scaleFactor)
#             rect.moveTo(0, 0)
#             c.setRect(rect)
#
#             c.update_resize_handles()
#             c.update_painter_text_rect()
#
#         c.setX(c.x() * scaleFactor)
#         c.setY(c.y() * scaleFactor)


# ---------------------------------------------------------------------
def _update_scene_rect_recursively(items, rect):
    for c in items:
        rect = rect.united(c.sceneBoundingRect())
        if c.type() == GROUP_ITEM_TYPE:
            if c.parentedWithParentOperation:
                rect = _update_scene_rect_recursively(c.parentedWithParentOperation, rect)
        else:
            if c.childItems():
                rect = _update_scene_rect_recursively(c.childItems(), rect)

    return rect


# ---------------------------------------------------------------------
def sceneBoundingRectWithChildren(nesne):
    # rect = QRectF(self.sceneBoundingRect())
    rect = nesne.sceneBoundingRect()
    if nesne.type() == GROUP_ITEM_TYPE:
        ic_nesneler = nesne.parentedWithParentOperation
    else:
        ic_nesneler = nesne.childItems()
    for c in ic_nesneler:
        rect = rect.united(c.sceneBoundingRect())
        if c.type() == GROUP_ITEM_TYPE:
            if c.parentedWithParentOperation:
                rect = _update_scene_rect_recursively(c.parentedWithParentOperation, rect)
        else:
            if c.childItems():
                rect = _update_scene_rect_recursively(c.childItems(), rect)
    return rect
