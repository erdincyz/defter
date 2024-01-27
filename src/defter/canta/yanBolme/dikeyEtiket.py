# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '10/13/23'
__author__ = 'E. Y.'

from PySide6.QtGui import QPainter, QFontMetrics
from PySide6.QtWidgets import QLabel


#######################################################################
class DikeyEtiket(QLabel):

    # ---------------------------------------------------------------------
    def __init__(self, *args, dikey=True):
        super(DikeyEtiket, self).__init__(*args)
        self.dikey = dikey

    # ---------------------------------------------------------------------
    def paintEvent(self, event):
        if self.dikey:
            painter = QPainter(self)
            painter.translate(0, self.height())
            painter.rotate(-90)
            # calculate the size of the font
            fm = QFontMetrics(painter.font())
            xoffset = int(fm.boundingRect(self.text()).width() / 2)
            yoffset = int(fm.boundingRect(self.text()).height() / 2)
            x = int(self.width() / 2) + yoffset
            y = int(self.height() / 2) - xoffset
            # because we rotated the label, x affects the vertical placement, and y affects the horizontal
            painter.drawText(y, x, self.text())
            painter.end()
        else:
            super(DikeyEtiket, self).paintEvent(event)

    # ---------------------------------------------------------------------
    def minimumSizeHint(self):
        if self.dikey:
            return QLabel.minimumSizeHint(self).transposed()
        else:
            return QLabel.minimumSizeHint(self)

    # ---------------------------------------------------------------------
    def sizeHint(self):
        if self.dikey:
            return QLabel.sizeHint(self).transposed()
        else:
            return QLabel.sizeHint(self)
