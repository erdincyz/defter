# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '5/11/16'

# from math import fabs
from PySide6.QtGui import QTextOption
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtWidgets import QGraphicsTextItem
from .. import shared


########################################################################
class TempTextItem(QGraphicsTextItem):
    Type = shared.TEMP_TEXT_ITEM_TYPE

    # textItemFocusedOut = Signal(QGraphicsTextItem)
    # textItemFocusedOut = Signal(object)
    textItemFocusedOut = Signal()

    # textItemSelectedChanged = Signal(QGraphicsTextItem)

    # ---------------------------------------------------------------------
    def __init__(self, width, font, color, text=None, parent=None):
        super(TempTextItem, self).__init__(text, parent)

        self._kim = shared.kim(kac_basamak=16)
        self.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable)

        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)

        self.setTextWidth(width)
        self.setFont(font)
        self.setDefaultTextColor(color)

        self.textOption = QTextOption()
        self.textOption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textOption.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.document().setDefaultTextOption(self.textOption)

        self.setTransformOriginPoint(self.boundingRect().center())

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return TempTextItem.Type

    # ---------------------------------------------------------------------
    def setCenter(self, center: QPointF):
        c = self.boundingRect().center()
        dx = center.x() - c.x()
        dy = center.y() - c.y()
        self.moveBy(dx, dy)

    # ---------------------------------------------------------------------
    def changeImageItemTextBackgroundColorAlpha(self, delta):
        self.clearFocus()

    # ---------------------------------------------------------------------
    def changeBackgroundColorAlpha(self, delta):
        self.clearFocus()

    # ---------------------------------------------------------------------
    def changeLineColorAlpha(self, delta):
        self.clearFocus()

    # ---------------------------------------------------------------------
    def fontPointSizeF(self):
        return self.font().pointSizeF()

    # ---------------------------------------------------------------------
    def focusOutEvent(self, event):
        # self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        # self.textItemFocusedOut.emit(self)
        self.textItemFocusedOut.emit()
        super(TempTextItem, self).focusOutEvent(event)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        # if self.textInteractionFlags() == Qt.NoTextInteraction:
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        # self.clearFocus()
        super(TempTextItem, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
            self.setSelected(False)

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                self.clearFocus()
                self.setSelected(False)

        super(TempTextItem, self).keyPressEvent(event)

    # # ---------------------------------------------------------------------
    # def paint(self, painter, option, widget):
    #
    #     # # # # # # debug start - pos() # # # # #
    #     # p = self.pos()
    #     # s = self.scenePos()
    #     # painter.drawText(self.boundingRect(),
    #     #                  "{0:.2f},  {1:.2f}\n{2:.2f},  {3:.2f}".format(p.x(), p.y(), s.x(), s.y()))
    #     # # t = self.transformOriginPoint()
    #     # # painter.drawRect(t.x()-12, t.y()-12,24,24)
    #     # mapped = self.mapToScene(self.rect().topLeft())
    #     # painter.drawText(self.rect().x(), self.rect().y(), "{0:.2f}  {1:.2f}".format(mapped.x(), mapped.y()))
    #     # r = self.textItem.boundingRect()
    #     # r = self.mapRectFromItem(self.textItem, r)
    #     # painter.drawRect(r)
    #     # painter.drawText(self.rect().center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
    #     # # # # # # debug end - pos() # # # # #
    #
    #     # option2 = QStyleOptionGraphicsItem(option)
    #     # option2.state = 0
    #     # option.state &= ~(QStyle.State_Selected | QStyle.State_HasFocus)
    #     # option2.exposedRect.setSize(self.document().pageSize())
    #     # option2.exposedRect.setSize(self.document().documentLayout().documentSize())
    #
    #     # option.exposedRect = self.boundingRect()
    #     # option.rect = option.exposedRect.toRect()
    #
    #     # rect = QRectF(self.rect())
    #     # rect.moveTo(0, 0)
    #     # option2.exposedRect = rect
    #     # option.exposedRect = self._rect
    #     # option.rect = self._rect.toRect()
    #
    #     # painter.setClipRect(option.exposedRect)
    #     super(TempTextItem, self).paint(painter, option, widget)
    #
    #     # self.doc.drawContents(painter, self.rect())

    # ---------------------------------------------------------------------
    def html_dive_cevir(self, html_klasor_kayit_adres, dosya_kopyalaniyor_mu):
        # Ola ki bu nesne aktif iken HTML olarak kaydet cagrilirsa diye
        # None dondurmeyelim stringe ekleniyor bu
        return ""
