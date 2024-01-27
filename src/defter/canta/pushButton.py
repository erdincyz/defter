# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '2/7/21'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtGui import QBrush, QPainter
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal
from .shared import kutulu_arkaplan_olustur


########################################################################
class PushButton(QPushButton):

    # ---------------------------------------------------------------------
    def __init__(self, yazi, genislik=None, yukseklik=None, renkArkaplan=None, renkYazi=None, parent=None):
        super(PushButton, self).__init__(yazi, parent)

        self.setFlat(True)

        if genislik:
            self.setFixedWidth(genislik)
        if yukseklik:
            self.setFixedHeight(yukseklik)

        if renkArkaplan or renkYazi:
            self.setAutoFillBackground(True)

            p = self.palette()
            if renkYazi:
                p.setColor(self.foregroundRole(), renkYazi)
            if renkArkaplan:
                p.setColor(self.backgroundRole(), renkArkaplan)
            self.setPalette(p)

        else:
            stil = """
            QPushButton{
                background-color: #eee;
                border: 0;
                padding: 3px;
                border-radius: 3px;
            }
            QPushButton:hover{
                background-color: #def;
            }
            QPushButton:pressed{
                background-color: #cde;
            }
            QPushButton:checked{
                background-color: #ced5e1;
            }
                """
            self.setStyleSheet(stil)


#######################################################################

class PushButtonRenk(QPushButton):
    sagTiklandi = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, yazi, genislik, yukseklik, renk=None, parent=None):
        super(PushButtonRenk, self).__init__(yazi, parent)

        if renk:
            self.renk = renk
        else:
            self.renk = None  # renk yoksa dugmeye ilk tiklandiginda renk secme araci aciliyor
        self.renkGuncelle(renk)
        self.setFixedWidth(genislik)
        self.setFixedHeight(yukseklik)
        kutulu_arkaplan_olustur(self, 3)

    # ---------------------------------------------------------------------
    def renkGuncelle(self, renk):
        self.renk = renk
        self.update()

    # ---------------------------------------------------------------------
    def paintEvent(self, event):
        if self.renk:
            p = QPainter(self)
            # p.begin()
            if self.renk:
                p.fillRect(self.rect(), QBrush(self.renk))
            else:
                p.fillRect(self.rect(), QBrush(Qt.GlobalColor.lightGray))
            # p.setBrush(self.renk)
            # p.drawRect(self.rect())
            p.end()

        # super(PushButtonRenk, self).paintEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.sagTiklandi.emit()
            event.accept()

        super(PushButtonRenk, self).mousePressEvent(event)
