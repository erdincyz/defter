# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '27/Aug/2016'

from PySide6.QtWidgets import QListWidgetItem, QStyledItemDelegate
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt


#######################################################################
class ListWidgetItem(QListWidgetItem):
    # ---------------------------------------------------------------------
    def __init__(self, view=None, tip=None):
        super(ListWidgetItem, self).__init__(view, tip)

        self._pen = QPen()
        # self._fontPointSize = 10
        self._presetFont = self.font()
        self._cizgiRengi = QColor(Qt.GlobalColor.transparent)

    # ---------------------------------------------------------------------
    def setCizgiRengi(self, col):
        self._cizgiRengi = col

    # ---------------------------------------------------------------------
    def cizgiRengi(self):
        return self._cizgiRengi

    # ---------------------------------------------------------------------
    def setPresetFont(self, font):
        self._presetFont = font

    # ---------------------------------------------------------------------
    def presetFont(self):
        return self._presetFont

    # # ---------------------------------------------------------------------
    # def setFont(self, font):
    #     # self.setFontPointSize(font.pointSize())
    #     # listede fazla yer kaplamasin diye,
    #     # bu sınıfta kullandıgımız self._fontPointSize, stili uygularken kullanacagimiz kaydedilmis font boyutu
    #     # hemen asagida set settigimiz font boyutu stilin listWidgetItem olarak listwidgette cizdirilen boyutu.
    #     # if self._fontPointSize >= 72:
    #     #     font.setPointSize(72)
    #     font.setPointSize(10)
    #     super(ListWidgetItem, self).setFont(font)

    # ---------------------------------------------------------------------
    def setPen(self, pen):
        if self._pen == pen:
            return
        self._pen = pen

    # ---------------------------------------------------------------------
    def pen(self):
        return self._pen


########################################################################
class ListWidgetItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        # QStyledItemDelegate.__init__(self)
        super(ListWidgetItemDelegate, self).__init__(parent)
        # self.offset = 2

        # self.linePen = QPen(QColor(Qt.transparent))
        # self.linePen.setWidth(2)

        # self.textPen = QPen(QColor(Qt.black))

        # self.alignment = Qt.AlignHCenter | Qt.AlignVCenter

    def paint(self, painter, option, index):
        super(ListWidgetItemDelegate, self).paint(painter, option, index)

        painter.save()
        # bu alttaki yerine userrole falan mi kullansak
        cizgiRengi = self.parent().item(index.row()).cizgiRengi()
        # linePen = QPen(cizgiRengi)
        # linePen.setWidth(2)
        # linePen.setStyle()
        # linePen.setCapStyle()
        # linePen.setMiterLimit()Style()
        # painter.setPen(linepen)
        painter.setPen(QPen(cizgiRengi, 5))
        # itemRect = option.rect.adjusted(self.offset, self.offset, -self.offset, -self.offset)
        # painter.drawRect(option.rect)
        painter.drawLine(option.rect.topLeft(), option.rect.bottomLeft())
        painter.drawLine(option.rect.topRight(), option.rect.bottomRight())

        painter.restore()
        # text = index.data(Qt.DisplayRole)
        # painter.setPen(self.textpen)
        # painter.drawText(option.rect, self.AlignmentFlag, text)
