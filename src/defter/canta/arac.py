# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '05/07/22'
__author__ = 'E. Y.'

from PySide6.QtGui import QPen, QFont, QColor, Qt, QPixmap, QCursor, QIcon
from PySide6.QtCore import QT_TRANSLATE_NOOP


#######################################################################
class Arac(object):
    # [tip] = (imlecAdresi , ikonAdresi, aracAdi)
    aracSozluk = {'secimAraci': (Qt.CursorShape.ArrowCursor,
                                 ":icons/arrow.png",
                                 QT_TRANSLATE_NOOP('DefterAnaPencere', 'selection')),
                  'okAraci': (":icons/cursor-line.png",
                              ":icons/line.png",
                              QT_TRANSLATE_NOOP('DefterAnaPencere', 'line')),
                  'kutuAraci': (":icons/cursor-rectangle.png",
                                ":icons/rectangle.png",
                                QT_TRANSLATE_NOOP('DefterAnaPencere', 'rectangle')),
                  'yuvarlakAraci': (":icons/cursor-circle.png",
                                    ":icons/circle.png",
                                    QT_TRANSLATE_NOOP('DefterAnaPencere', 'ellipse')),
                  'kalemAraci': (":icons/cursor-pen.png",
                                 ":icons/pen.png",
                                 QT_TRANSLATE_NOOP('DefterAnaPencere', 'draw path')),
                  'yaziAraci': (":icons/cursor-text.png",
                                ":icons/t.png",
                                QT_TRANSLATE_NOOP('DefterAnaPencere', 'text')),
                  'resimAraci': (":icons/cursor-image.png",
                                 ":icons/file-image.png",
                                 QT_TRANSLATE_NOOP('DefterAnaPencere', 'image')),
                  'videoAraci': (":icons/cursor-pen.png",
                                 ":icons/file-video.png",
                                 QT_TRANSLATE_NOOP('DefterAnaPencere', 'video')),
                  'dosyaAraci': (":icons/cursor-pen.png",
                                 ":icons/import-file.png",
                                 QT_TRANSLATE_NOOP('DefterAnaPencere', 'file')),
                  'aynalaXAraci': (Qt.CursorShape.ArrowCursor,
                                   "",
                                   ""),
                  'aynalaYAraci': (Qt.CursorShape.ArrowCursor,
                                   "",
                                   ""),
                  'resimKirpAraci': (Qt.CursorShape.CrossCursor,
                                     "",
                                     "")
                  }

    # ---------------------------------------------------------------------
    def __init__(self, tip):
        # self.tip = tip

        self.tip = tip

        self.imlecAdresi = Arac.aracSozluk[tip][0]
        self.ikonAdresi = Arac.aracSozluk[tip][1]
        self.adi = Arac.aracSozluk[tip][2]
        self._imlec = None

        self.kalem = QPen(QColor(0, 0, 0),
                          0,
                          Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.FlatCap,
                          Qt.PenJoinStyle.RoundJoin)

        self.arkaPlanRengi = QColor(225, 225, 225)
        self.yaziRengi = QColor(0, 0, 0)
        # asagida property olarak var
        # self.cizgiRengi = kalem.color()

        self.yaziTipi = QFont()
        self.yaziHiza = Qt.AlignmentFlag.AlignLeft
        self.karakter_bicimi_sozluk = {"b": False,
                                       "i": False,
                                       "u": False,
                                       "s": False,
                                       "o": False,
                                       }

    # ---------------------------------------------------------------------
    def oku_ozellikler(self):
        return {
            "kalem": self.kalem,
            "yaziTipi": self.yaziTipi,
            "arkaPlanRengi": self.arkaPlanRengi,
            "yaziRengi": self.yaziRengi,
            "cizgiRengi": self.cizgiRengi,
            "yaziHiza": int(self.yaziHiza),
            "karakter_bicimi_sozluk": self.karakter_bicimi_sozluk,
        }

    # ---------------------------------------------------------------------
    def yaz_ozellikler(self, aracOzellikleriSozluk):
        self.kalem = aracOzellikleriSozluk["kalem"]
        self.yaziTipi = aracOzellikleriSozluk["yaziTipi"]
        self.arkaPlanRengi = aracOzellikleriSozluk["arkaPlanRengi"]
        self.yaziRengi = aracOzellikleriSozluk["yaziRengi"]
        self.cizgiRengi = aracOzellikleriSozluk["cizgiRengi"]
        self.yaziHiza = Qt.AlignmentFlag(int(aracOzellikleriSozluk["yaziHiza"]))
        self.karakter_bicimi_sozluk = aracOzellikleriSozluk["karakter_bicimi_sozluk"]

    # ---------------------------------------------------------------------
    @property
    def imlec(self):
        if not self._imlec:
            if type(self.imlecAdresi) is str:
                self._imlec = QCursor(QPixmap(self.imlecAdresi))
            else:  # Qt.CursorShape
                self._imlec = self.imlecAdresi  # Qt.ArrowCursor gibi

        return self._imlec

    # ---------------------------------------------------------------------
    @property
    def arkaPlanSeffaflik(self):
        return self.arkaPlanRengi.alpha()

    # ---------------------------------------------------------------------
    @arkaPlanSeffaflik.setter
    def arkaPlanSeffaflik(self, alpha):
        self.arkaPlanRengi.setAlpha(alpha)

    # ---------------------------------------------------------------------
    @property
    def yaziSeffaflik(self):
        return self.yaziRengi.alpha()

    # ---------------------------------------------------------------------
    @yaziSeffaflik.setter
    def yaziSeffaflik(self, alpha):
        self.yaziRengi.setAlpha(alpha)

    # ---------------------------------------------------------------------
    @property
    def yaziBoyutu(self):
        return self.yaziTipi.pointSize()

    # ---------------------------------------------------------------------
    @yaziBoyutu.setter
    def yaziBoyutu(self, boyut):
        self.yaziTipi.setPointSize(boyut)

    # ---------------------------------------------------------------------
    @property
    def cizgiRengi(self):
        return self.kalem.color()

    # ---------------------------------------------------------------------
    @cizgiRengi.setter
    def cizgiRengi(self, renk):
        self.kalem.setColor(renk)

    # ---------------------------------------------------------------------
    @property
    def cizgiSeffaflik(self):
        return self.cizgiRengi.alpha()

    # ---------------------------------------------------------------------
    @cizgiSeffaflik.setter
    def cizgiSeffaflik(self, alpha):
        self.cizgiRengi.setAlpha(alpha)

    # ---------------------------------------------------------------------
    @property
    def cizgiKalinligi(self):
        return self.kalem.widthF()

    # ---------------------------------------------------------------------
    @cizgiKalinligi.setter
    def cizgiKalinligi(self, kalinlik):
        self.kalem.setWidthF(kalinlik)

    # ---------------------------------------------------------------------
    @property
    def cizgiTipi(self):
        return self.kalem.style()

    # ---------------------------------------------------------------------
    @cizgiTipi.setter
    def cizgiTipi(self, lineStyle):
        self.kalem.setStyle(lineStyle)

    # ---------------------------------------------------------------------
    @property
    def cizgiBirlesimTipi(self):
        return self.kalem.joinStyle()

    # ---------------------------------------------------------------------
    @cizgiBirlesimTipi.setter
    def cizgiBirlesimTipi(self, joinStyle):
        self.kalem.setJoinStyle(joinStyle)

    # ---------------------------------------------------------------------
    @property
    def cizgiUcuTipi(self):
        return self.kalem.capStyle()

    # ---------------------------------------------------------------------
    @cizgiUcuTipi.setter
    def cizgiUcuTipi(self, capStyle):
        self.kalem.setCapStyle(capStyle)
