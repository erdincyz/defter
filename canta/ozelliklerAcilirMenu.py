# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '2/16/15'

from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot


########################################################################
class OzelliklerAcilirMenu(QWidget):
    def __init__(self, baslik, parent=None):
        super(OzelliklerAcilirMenu, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        anaLayout = QVBoxLayout()
        anaLayout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        self.setLayout(anaLayout)

        # self.dugme = QPushButton("V     {}".format(baslik), self)
        self.dugme = QPushButton(baslik, self)
        # self.dugme.setIconSize(QSize(3,3))
        self.dugme.setIcon(QIcon(':/icons/expanded.png'))
        # TODO: basligi sola hizala
        self.dugme.setFlat(True)
        # self.dugme.setFixedWidth(200)
        self.dugme.setStyleSheet("QPushButton{"
                                 "text-align:left;"
                                 "font-size:1.2em; "
                                 "font-weight:bold;"
                                 # "margin-right:10px;"
                                 # "margin-left:10px;"
                                 # "margin-top:10px;"
                                 "padding-left:10px;"
                                 # "color:#fff; "
                                 "color:#578; "
                                 "background-color:#9ab;}")
        self.dugme.clicked.connect(self.ac_kapa)
        self.icerikWidget = QWidget(self)
        anaLayout.addWidget(self.dugme)
        anaLayout.addWidget(self.icerikWidget)
        # anaLayout.addStretch()

        # self.setStyleSheet("QWidget{background-color:#ccc;}")

        self.show()

    # ---------------------------------------------------------------------
    @Slot()
    def ac_kapa(self):
        # self.containerWidget.setVisible(not self.containerWidget.isVisible())
        if self.icerikWidget.isVisible():
            self.icerikWidget.hide()
            # baslik = "V     {}".format(self.dugme.text()[6:])
            self.dugme.setIcon(QIcon(':/icons/collapsed.png'))
        else:
            self.icerikWidget.show()
            # baslik = ">     {}".format(self.dugme.text()[6:])
            self.dugme.setIcon(QIcon(':/icons/expanded.png'))

        # self.dugme.setText(baslik)

    # ---------------------------------------------------------------------
    def al_icerik_widgetin_layoutunu(self):
        return self.icerikWidget.layout()

    #
    # # ---------------------------------------------------------------------
    # @Slot()
    # def ac_kapa(self):
