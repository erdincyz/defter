# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '5/4/16'

from PySide6.QtWidgets import QSlider, QProxyStyle
from PySide6.QtCore import Signal, Slot, Qt


#######################################################################
class ProxyStyle(QProxyStyle):
    """Gostergenin, fare sol tus ile tiklanan yere gitmesi icin. Yoksa adim adim(stepSize) gidiyor"""

    def styleHint(self, hint, opt=None, widget=None, returnData=None):
        res = super().styleHint(hint, opt, widget, returnData)
        if hint == QProxyStyle.StyleHint.SH_Slider_AbsoluteSetButtons:
            res |= Qt.MouseButton.LeftButton.value
        return res


#######################################################################
class Slider(QSlider):
    valueChangedFromSliderGuiNotBySetValue = Signal(int)

    # valueChangedWithSetValue = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(Slider, self).__init__(parent)
        self.setStyle(ProxyStyle())
        self.kodIleSetEdiliyor = False
        self.valueChanged.connect(self.on_value_changed)

    # ---------------------------------------------------------------------
    def setValue(self, val):
        self.kodIleSetEdiliyor = True
        # self.setValue(val)
        QSlider.setValue(self, val)
        self.kodIleSetEdiliyor = False

    @Slot(int)
    def on_value_changed(self, val):
        if not self.kodIleSetEdiliyor:
            self.valueChangedFromSliderGuiNotBySetValue.emit(val)
        # else:
        #     self.valueChangedWithSetValue.emit(val)
