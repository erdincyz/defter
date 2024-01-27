# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '23/06/22'

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QLinearGradient, QPainter
from .slider import Slider


#######################################################################
class SliderRenk(Slider):
    """  """
    degerDegisti = Signal(int)
    sliderClosed = Signal()

    # ----------------------------------------------------------------------
    def __init__(self, parent=None):
        """ Constructor """
        super(SliderRenk, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.valueChanged.connect(lambda x: self.degerDegisti.emit(x))

        # self.setFocusPolicy(Qt.NoFocus)
        # self.setFocusPolicy(Qt.WheelFocus)
        # self.setFocusPolicy(Qt.ClickFocus)

        self.setRange(0, 255)
        self.setOrientation(Qt.Orientation.Horizontal)

        self.setGeometry(0, 0, 150, 50)

        self.setStyleSheet(" QSlider::groove:horizontal "
                           "{border: 0px solid #999999;"
                           "height: 20px;} "
                           # " /* the groove expands to the size of the slider by default."
                           # " by giving it a height, it has a fixed size */ "
                           # "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, } "
                           # "stop:0 #B1B1B1,}  "
                           # "stop:1 #c4c4c4);} "
                           # "margin: 2px 0;}  "

                           "QSlider::handle:horizontal "
                           "{ "
                           "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                           "stop:0 #fff, "
                           "stop:1 #00000000);  "
                           # "background:#fff;"
                           "border: 3px solid #fff;  "
                           "width: 7px;  "
                           "margin: -1px -5px; }"

                           )
        # "/* handle is placed by default on the contents rect of the groove."
        # " Expand outside the groove */ "
        # " border-radius: 0px; }")
        self.bgGradient = QLinearGradient(0, 0, 1, 0)
        self.bgGradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectMode)

    # ---------------------------------------------------------------------
    def setBgGradient(self, bgGradient):
        self.bgGradient = bgGradient
        self.update()

    # ----------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bgGradient)
        # painter.setBrush(self.bgGradient)
        # painter.drawRect(self.rect())

        super(SliderRenk, self).paintEvent(event)


#######################################################################
class SliderRenkYalniz(SliderRenk):
    """  """

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        """ Constructor """
        super(SliderRenkYalniz, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # self.setFocusPolicy(Qt.NoFocus)
        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        # self.setFocusPolicy(Qt.ClickFocus)

    # ---------------------------------------------------------------------
    def focusOutEvent(self, event):
        # self.close()
        self.hide()
        # TODO bu signal kullanmamisiz. comment edelim..
        self.sliderClosed.emit()
        # print("focus out")
        super(SliderRenkYalniz, self).focusOutEvent(event)

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            # self.close()
            self.hide()
        super(SliderRenkYalniz, self).keyPressEvent(event)
