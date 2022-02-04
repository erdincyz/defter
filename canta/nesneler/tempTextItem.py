# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '5/11/16'

# from math import fabs
import uuid
from PySide6.QtGui import QTextOption
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtWidgets import QGraphicsTextItem
from canta import shared


########################################################################
class TempTextItem(QGraphicsTextItem):
    Type = shared.TEMP_TEXT_ITEM_TYPE

    # textItemFocusedOut = Signal(QGraphicsTextItem)
    # textItemFocusedOut = Signal(object)
    textItemFocusedOut = Signal()

    # textItemSelectedChanged = Signal(QGraphicsTextItem)

    def __init__(self, width, font, color, text=None, parent=None):
        super(TempTextItem, self).__init__(text, parent)

        self._kim = uuid.uuid4().hex
        self.setFlags(self.ItemIsFocusable)

        self.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.setTextWidth(width)
        self.setFont(font)
        self.setDefaultTextColor(color)

        self.textOption = QTextOption()
        self.textOption.setAlignment(Qt.AlignCenter)
        self.textOption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.document().setDefaultTextOption(self.textOption)

        self.setTransformOriginPoint(self.boundingRect().center())

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return TempTextItem.Type

    # ---------------------------------------------------------------------
    def scaleWithOffset(self, scale):
        cEski = self.sceneCenter()
        self.setScale(scale)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())
        # self.update_resize_handles() # TODO: we use this because of scaled group's ungroup.

    # ---------------------------------------------------------------------
    def rotateWithOffset(self, angle):
        # 1Million thanks to this guy.
        # https://stackoverflow.com/a/32734103
        # ayrica bu rotate with offsetlerde mod 360 yapmiyoruz
        # cunku buraya gelen illaki modlanmis geliyor.
        # bunu niye yazdim. undoya gitmeden rotate olabiliyor bununla,
        # (undoRotatelerde mod var.)
        cEski = self.sceneCenter()
        self.setRotation(angle)
        cYeni = self.sceneCenter()
        diff = cEski - cYeni
        self.moveBy(diff.x(), diff.y())

    # ---------------------------------------------------------------------
    def setCenter(self, center: QPointF):
        c = self.boundingRect().center()
        dx = center.x() - c.x()
        dy = center.y() - c.y()
        self.moveBy(dx, dy)

    # ---------------------------------------------------------------------
    def paint(self, painter, option, widget):

        # # # # # # debug start - pos() # # # # #
        # p = self.pos()
        # s = self.scenePos()
        # painter.drawText(self.boundingRect(),
        #                  "{0:.2f},  {1:.2f}\n{2:.2f},  {3:.2f}".format(p.x(), p.y(), s.x(), s.y()))
        # # t = self.transformOriginPoint()
        # # painter.drawRect(t.x()-12, t.y()-12,24,24)
        # mapped = self.mapToScene(self.rect().topLeft())
        # painter.drawText(self.rect().x(), self.rect().y(), "{0:.2f}  {1:.2f}".format(mapped.x(), mapped.y()))
        # r = self.textItem.boundingRect()
        # r = self.mapRectFromItem(self.textItem, r)
        # painter.drawRect(r)
        # painter.drawText(self.rect().center(), "{0:f}  {1:f}".format(self.sceneWidth(), self.sceneHeight()))
        # # # # # # debug end - pos() # # # # #

        # option2 = QStyleOptionGraphicsItem(option)
        # option2.state = 0
        # option.state &= ~(QStyle.State_Selected | QStyle.State_HasFocus)
        # option2.exposedRect.setSize(self.document().pageSize())
        # option2.exposedRect.setSize(self.document().documentLayout().documentSize())

        # option.exposedRect = self.boundingRect()
        # option.rect = option.exposedRect.toRect()

        # rect = QRectF(self.rect())
        # rect.moveTo(0, 0)
        # option2.exposedRect = rect
        # option.exposedRect = self._rect
        # option.rect = self._rect.toRect()

        # painter.setClipRect(option.exposedRect)
        super(TempTextItem, self).paint(painter, option, widget)

        # self.doc.drawContents(painter, self.rect())

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
    def fontPointSize(self):
        return self.font().pointSize()

    # ---------------------------------------------------------------------
    def focusOutEvent(self, event):
        # self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setTextInteractionFlags(Qt.NoTextInteraction)

        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        # self.textItemFocusedOut.emit(self)
        self.textItemFocusedOut.emit()
        super(TempTextItem, self).focusOutEvent(event)

    # ---------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        # if self.textInteractionFlags() == Qt.NoTextInteraction:
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()
        # self.clearFocus()
        super(TempTextItem, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clearFocus()
            self.setSelected(False)

        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.clearFocus()
                self.setSelected(False)

        super(TempTextItem, self).keyPressEvent(event)
