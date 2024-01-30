# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '30/1/24'

from PySide6.QtGui import QAction, QKeySequence


#######################################################################
class Action(QAction):
    # ---------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)

        # arguman ile gelen shortcut da setShortcuti cagiriyor zaten.
        # if not self.shortcut().isEmpty():
        #     self.setToolTip(f"{self.toolTip()}    {self.shortcut().toString(QKeySequence.NativeText)}")

    # ---------------------------------------------------------------------
    def setShortcut(self, *args, **kwargs):
        super(Action, self).setShortcut(*args, **kwargs)
        self.setToolTip(f"{self.toolTip()}    {self.shortcut().toString(QKeySequence.NativeText)}")

