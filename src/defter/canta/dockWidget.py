# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/29/22'

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QHBoxLayout, QPushButton, QDockWidget, QWidget


#######################################################################
class DockWidget(QDockWidget):

    # ---------------------------------------------------------------------
    def __init__(self, baslik, parent=None):
        super(DockWidget, self).__init__(parent)

        self.renkYazi = QColor(255, 255, 255)
        self.renkArkaplan = QColor(153, 170, 187)

        self.setContentsMargins(0,0,0,0)

        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                         QDockWidget.DockWidgetFeature.DockWidgetClosable |
                         # QDockWidget.DockWidgetFeature.DockWidgetVerticalTitleBar|
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable
                         )

        self.setWindowTitle(baslik)

        # baslik
        baslikWidget = QWidget(self)
        baslikWidget.setFixedHeight(20)
        baslikWidget.setContentsMargins(0, 0, 0, 0)
        baslikWidget.setAutoFillBackground(True)

        p = baslikWidget.palette()
        p.setColor(baslikWidget.foregroundRole(), self.renkYazi)
        p.setColor(baslikWidget.backgroundRole(), self.renkArkaplan)
        baslikWidget.setPalette(p)

        # baslikWidget.setStyleSheet("QWidget {"
        #                            # "font-size:1.3em; "
        #                            # "font-weight:bold;"
        #                            # "margin-right:10px;"
        #                            # "margin-left:10px;"
        #                            # "margin-top:1px;"
        #                            # "padding-top:1px;"
        #                            # "padding-bottom:1px;"
        #                            "color:#fff; "
        #                            # "background-color:#9ab;"
        #                            "}")

        etiket = QLabel(baslik, baslikWidget)
        etiket.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QHBoxLayout(baslikWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        btnKapat = QPushButton("x", baslikWidget)
        btnKapat.setFixedWidth(18)
        btnKapat.setFlat(True)
        btnKapat.setAutoFillBackground(True)
        btnKapat.clicked.connect(self.close)

        p = btnKapat.palette()
        p.setColor(btnKapat.foregroundRole(), self.renkYazi)
        p.setColor(btnKapat.backgroundRole(), self.renkArkaplan)
        btnKapat.setPalette(p)

        btnYuzdur = QPushButton("o", baslikWidget)
        btnYuzdur.setFixedWidth(18)
        btnYuzdur.setFlat(True)
        btnYuzdur.setAutoFillBackground(True)
        btnYuzdur.clicked.connect(lambda: self.setFloating(not self.isFloating()))

        p = btnYuzdur.palette()
        p.setColor(btnYuzdur.foregroundRole(), self.renkYazi)
        p.setColor(btnYuzdur.backgroundRole(), self.renkArkaplan)
        btnYuzdur.setPalette(p)

        # lay.addStretch()
        lay.addSpacing(36)
        lay.addWidget(etiket)
        lay.addWidget(btnYuzdur)
        lay.addWidget(btnKapat)

        baslikWidget.setLayout(lay)

        self.setTitleBarWidget(baslikWidget)
