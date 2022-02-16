# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from canta.nesneler.base import BaseItem
from canta import shared


########################################################################
class Rect(BaseItem):
    Type = shared.RECT_ITEM_TYPE

    # ---------------------------------------------------------------------
    def __init__(self, pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent=None):
        super(Rect, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return Rect.Type
