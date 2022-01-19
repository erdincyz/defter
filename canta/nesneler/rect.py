# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '3/28/16'

from canta.nesneler.base import BaseItem
from canta import shared


########################################################################
class Rect(BaseItem):
    Type = shared.RECT_ITEM_TYPE

    # ---------------------------------------------------------------------
    def __init__(self, pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent=None):
        super(Rect, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)

        # print(self.transformOriginPoint())
        # self.setTransformOriginPoint(self.mapRectFromScene(self.rect()).center())
        # print(self.transformOriginPoint())

        # self.doc = QTextDocument()
        # self.docLayout = self.doc.documentLayout()
        # self.docLayout.documentSizeChanged.connect(self.doc_layout_changed)
        # # self.doc.setPageSize(self._rect.size())
        # textOption = QTextOption()
        # textOption.setAlignment(Qt.AlignCenter)
        # textOption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        # self.doc.setDefaultTextOption(textOption)
        # self.doc.setPlainText("asdasdasdasdasdasdasd")

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return Rect.Type

    # # ---------------------------------------------------------------------
    # @pyqtSlot(QSizeF)
    # def doc_layout_changed(self, size):
    #     pass
    #     # print("asdasdad", size)
    #
    #
    # # ---------------------------------------------------------------------
    # def paint(self, painter, option, widget=None):
    #     self.doc.setPageSize(self._rect.size())
    #     # self.doc.setTextWidth(self.rect().size().width())
    #     # layout = QAbstractTextDocumentLayout(doc)
    #
    #     painter.save()
    #     # painter.translate(self._rect.center())
    #     # metrics = painter.fontMetrics()
    #     # txt = metrics.elidedText(self._text, Qt.ElideRight, self._rect.width() / scale)
    #     # painter.drawText(self._rect, Qt.AlignCenter | Qt.AlignVCenter, txt)
    #     self.doc.drawContents(painter, self.rect())
    #     painter.restore()
    #     # painter.restore()
    #     super(Rect, self).paint(painter, option, widget)
