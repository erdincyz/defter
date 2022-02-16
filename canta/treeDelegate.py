# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '24/May/2018'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem, QApplication

from canta.shared import renk_degismis_nesne_yazi_rengi


########################################################################
class TreeDelegate(QStyledItemDelegate):
    Margin = 6

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(TreeDelegate, self).__init__(parent)
        # QStyledItemDelegate.__init__(self, parent, *args)

        self._satirYuksekligi = 128

        self.satirYuksekligi_QSize = QSize(self.satirYuksekligi, self.satirYuksekligi)

        self.iconSizeWidth = 25
        self.fontSize = 15
        self.colorModifiedFileBg = QColor().fromRgb(200, 210, 220)
        self.colorOpenedFileBg = QColor().fromRgb(200, 210, 255)
        self.colorOpenedFileText = QColor().fromRgb(200, 210, 255)
        self.colorSelectionText = QColor().fromRgb(200, 255, 255)
        self.colorModifiedFileText = QColor().fromRgb(255, 200, 210)
        self.renkSecim = QApplication.palette().highlight().color().lighter().lighter()

    @property
    def satirYuksekligi(self):
        return self._satirYuksekligi

    @satirYuksekligi.setter
    def satirYuksekligi(self, boyut):
        self._satirYuksekligi = boyut
        self.satirYuksekligi_QSize = QSize(boyut, boyut)

    def sizeHint(self, option, index):
        if not index.isValid():
            return QSize()
        return self.satirYuksekligi_QSize

    def updateEditorGeometry(self, editor, option, index):
        option.decorationPosition = QStyleOptionViewItem.Top
        option.displayAlignment = Qt.AlignHCenter | Qt.AlignBottom
        option.viewItemPosition = QStyleOptionViewItem.Middle
        # a = QRect(option.rect)
        # a.adjust(20,100,0,0)
        # print(option.rect ,a)
        # # editor.setGeometry(option.rect)
        # editor.setGeometry(a)

        rect = QRect(option.rect)
        rect.setHeight(20)
        rect.moveBottomLeft(option.rect.bottomLeft())
        editor.setGeometry(rect)

        # super(TreeDelegate, self).updateEditorGeometry(editor, option, index)

    # ---------------------------------------------------------------------
    def paintttt(self, painter, option, index):
        option.decorationPosition = QStyleOptionViewItem.Top
        # option.decorationAlignment = Qt.AlignLeft
        # option.decorationAlignment = Qt.AlignHCenter | Qt.AlignCenter
        # option.displayAlignment = Qt.AlignBottom
        # option.displayAlignment = Qt.AlignLeft | Qt.AlignVCenter
        option.displayAlignment = Qt.AlignHCenter | Qt.AlignBottom
        # option.displayAlignment = Qt.AlignHCenter |Qt.AlignVCenter
        # option.displayPosition = QStyleOptionViewItem.Bottom
        # option.font.setWeight(option.font.Bold)
        option.viewItemPosition = QStyleOptionViewItem.Middle

        # a = QRect(option.rect)
        # a.adjust(20, 100, 0, 0)
        # option.rect = a
        painter.save()
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(Qt.red))
        painter.drawRect(option.rect.adjusted(0, 110, 0, 0))
        # painter.fillRect(option.rect, painter.brush())
        # painter.fillRect(option.rect, QBrush(Qt.red))
        painter.restore()

        super(TreeDelegate, self).paint(painter, option, index)

    # ---------------------------------------------------------------------
    def paint(self, painter, option, index):

        # option.decorationPosition = QStyleOptionViewItem.Top
        # option.decorationAlignment = Qt.AlignLeft
        # option.displayAlignment = Qt.AlignBottom
        # option.displayAlignment = Qt.AlignLeft | Qt.AlignVCenter
        # option.font.setWeight(option.font.Bold)

        # a = QRect(option.rect)
        # a.adjust(20, 100, 0, 0)
        # option.rect = a

        # super(TreeDelegate, self).paint(painter, option, index)
        #
        # if index.column() == 1:  # ?? gerek var mi

        sayfa = index.internalPointer()
        # print(option.rect)

        ikon = sayfa.ikon
        # ikon.paint(painter, solaHizaliRect)

        # QPalette.alternateBase()
        # ikon.paint(painter, option.rect)
        if option.state & QStyle.State_Selected:
            # secilen nesne arkaplan rengi
            painter.save()
            painter.setPen(QPen(Qt.NoPen))
            # painter.setBrush(QApplication.palette().highlight())
            painter.setBrush(self.renkSecim)
            painter.drawRect(option.rect)

            # ikon
            rect = QRect(option.rect)
            rect.setTop(option.rect.top() + 10)
            # yazi boyutu 20, yani yazi baslamadan bitsin kare
            rect.setBottom(option.rect.bottom() - 20)
            ikon.paint(painter, rect)

            # # yazi arkaplan
            # rect = QRect(option.rect)
            # rect.setHeight(20)
            # rect.moveBottomLeft(option.rect.bottomLeft())
            # painter.drawRect(rect)

            painter.restore()

            # kutu altindaki yazinin arkaplanini boyamak icin
            # painter.save()
            # painter.setPen(QPen(Qt.NoPen))
            # #painter.setBrush(QApplication.palette().highlight())
            # #painter.setBrush(QApplication.palette().highlight().color().lighter())
            # painter.setBrush(Qt.red)
            # rect = QRect(option.rect)
            # rect.setHeight(20)
            # rect.moveBottomLeft(option.rect.bottomLeft())
            # painter.drawRect(rect)
            # painter.restore()

            # if sayfa.scene.isModified():
            #     yazi_pen = QPen(renk_degismis_nesne_yazi_rengi)
            # else:
            #     #yazi_pen = QPen(Qt.white)
            #     yazi_pen = QPen(sayfa.yaziRengi)
            # #yazi_pen = QPen(Qt.white)

        else:

            # painter.save()
            # painter.setPen(QPen(Qt.NoPen))
            # painter.setBrush(QApplication.palette().highlight())
            # painter.drawRect(option.rect)
            # painter.restore()

            # ikon
            rect = QRect(option.rect)
            rect.moveTop(option.rect.top() + 10)
            # yazi boyutu 20, yani yazi baslamadan bitsin kare
            rect.setBottom(option.rect.bottom() - 20)
            ikon.paint(painter, rect)

            painter.save()
            painter.setPen(QPen(Qt.NoPen))
            if index.row() % 2 == 1:
                painter.setBrush(QApplication.palette().alternateBase())
            else:
                painter.setBrush(QApplication.palette().base())

            painter.restore()

            # # yazi arka plan rengi
            # rect = QRect(option.rect)
            # rect.setHeight(20)
            # rect.moveBottomLeft(option.rect.bottomLeft())
            # painter.drawRect(rect)
            # painter.restore()

            # if sayfa.scene.isModified():
            #     yazi_pen = QPen(renk_degismis_nesne_yazi_rengi)
            # else:
            #     yazi_pen = QPen(sayfa.yaziRengi)

            #     painter.setBrush(QApplication.palette().highlight())
        # The original C++ example used option.palette.foreground() to
        # get the brush for painting, but there are a couple of
        # problems with that:
        #   - foreground() is obsolete now, use windowText() instead
        #   - more importantly, windowText() just returns a brush
        #     containing a flat color, where sometimes the style
        #     would have a nice subtle gradient or something.
        # Here we just use the brush of the painter object that's
        # passed in to us, which keeps the row highlighting nice
        # and consistent.
        #     painter.fillRect(option.rect, painter.brush())

        # # painter.save()
        # if option.state & QStyle.State_Selected:
        #     painter.setPen(QPen(Qt.NoPen))
        #     painter.setBrush(QApplication.palette().highlight())
        #     painter.drawRect(option.rect)
        #     # painter.restore()
        #     # painter.save()
        #     font = painter.font
        #     pen = painter.pen()
        #     pen.setColor(QApplication.palette().color(QPalette.HighlightedText))
        #     painter.setPen(pen)
        # else:
        #     painter.setPen(QPen(Qt.black))

        # solaHizaliRect = QRect(option.rect)
        # solaHizaliRect = QRect(0, 0, 128, 128)
        # painter.drawRect(solaHizaliRect)

        # painter.drawText(option.rect, Qt.AlignLeft | Qt.AlignVCenter, sayfa.adi)
        # painter.drawText(option.rect, Qt.AlignCenter | Qt.AlignBottom, text)
        # painter.drawText(option.rect, Qt.AlignHCenter | Qt.AlignBottom, sayfa.adi)
        # painter.setPen(QPen(sayfa.yaziRengi))

        if sayfa.scene.isModified():
            painter.setPen(QPen(renk_degismis_nesne_yazi_rengi))
        else:
            painter.setPen(QPen(sayfa.yaziRengi))

        # painter.setPen(yazi_pen)
        rect = QRect(option.rect)
        rect.setLeft(option.rect.left() + 7)
        rect.moveTop(option.rect.top() - 2)
        painter.drawText(rect, Qt.AlignLeft | Qt.AlignBottom, sayfa.adi)

        # painter.save()
        # # burdan bazi seyler treeview icindeki yeni stile tasinabilir sanki!
        # painter.setPen(QPen(Qt.lightGray))
        # painter.drawRect(option.rect)
        # painter.restore()

    # ---------------------------------------------------------------------
    def paintt(self, painter, option, index):
        # rect = QRect(option.rect.x() + self.iconSizeWidth, option.rect.y(), option.rect.width() - self.iconSizeWidth,
        #              option.rect.height())

        # QStyledItemDelegate.paint(self, painter, option, index)

        painter.save()

        solaHizaliRect = QRect(option.rect)
        # solaHizaliRect.moveLeft(-option.rect.width()/3)

        # print(index.internalPointer())

        ikon = index.data(Qt.DecorationRole)
        # ikon.paint(painter, option.rect)
        ikon.paint(painter, solaHizaliRect)

        text = index.data(Qt.DisplayRole)
        is_sayfa_modified = index.data(Qt.UserRole).scene.isModified()

        if is_sayfa_modified:
            text = ("* %s" % text)

        # painter.drawText(option.rect, Qt.AlignLeft | Qt.AlignVCenter, text)
        painter.drawText(option.rect, Qt.AlignCenter | Qt.AlignBottom, text)

        painter.restore()

        # option.icon.paint(painter, rect)
        # pix = option.icon.pixmap(128,128)
        # painter.drawPixmap(option.rect, pix)

    # ---------------------------------------------------------------------
    def painttt(self, painter, option, index):
        # QStyledItemDelegate.paint(self, painter, option, index)

        # option.decorationPosition = QStyleOptionViewItem.Right
        # option.decorationPosition = QStyleOptionViewItem.Bottom
        option.decorationPosition = QStyleOptionViewItem.Top
        option.decorationAlignment = Qt.AlignLeft
        super(TreeDelegate, self).paint(painter, option, index)

        # return
        painter.save()

        font = painter.font()
        font.setPointSize(self.fontSize)
        painter.setFont(font)
        # fontBold = painter.font()
        # fontBold.setBold(True)

        text = index.data(Qt.DisplayRole)

        rect = QRect(option.rect.x() + self.iconSizeWidth, option.rect.y(), option.rect.width() - self.iconSizeWidth,
                     option.rect.height())
        # rectForModified = QRect(option.rect.x() + self.iconSizeWidth,
        # option.rect.y(), option.rect.width() - self.iconSizeWidth + 5, option.rect.height())

        if index.column() == 0:

            # painter.drawIcon()

            is_sayfa_modified = index.data(Qt.UserRole).scene.isModified()

            if is_sayfa_modified:
                text = ("* %s" % text)
                if index.row() % 2 == 1:
                    painter.fillRect(rect, self.colorModifiedFileBg.darker(110))
                else:
                    painter.fillRect(rect, self.colorModifiedFileBg)
                painter.setPen(QPen(self.colorModifiedFileText))
                # painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, modifiedText)

            else:
                if index.row() % 2 == 1:
                    painter.fillRect(rect, self.colorOpenedFileBg.lighter(90))
                else:
                    painter.fillRect(rect, self.colorOpenedFileBg)
                painter.setPen(QPen(self.colorOpenedFileText))

            if option.state & QStyle.State_Selected:
                painter.setPen(QPen(QColor(self.colorSelectionText)))
            painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)

        # else:
        #     super(TreeDelegate, self).paint(painter, option, index)

        # # set background color
        # painter.setPen(QPen(Qt.NoPen))
        # if option.state & QStyle.State_Selected:
        #     painter.setBrush(QBrush(Qt.red))
        # else:
        #     painter.setBrush(QBrush(Qt.white))
        # painter.drawRect(option.rect)

        # set text color
        # painter.setPen(QPen(Qt.black))
        # text = index.data(Qt.DisplayRole)
        # if text:
        #     painter.drawText(option.rect, Qt.AlignLeft, text)
        #
        painter.restore()

    # def paint(self, painter, option, index):
    #     if option.widget is not None:
    #         style = option.widget.style()
    #     else:
    #         style = QApplication.style()
    #
    #     style.drawPrimitive(
    #         QStyle.PE_PanelItemViewRow, option, painter,
    #         option.widget)
    #     style.drawPrimitive(
    #         QStyle.PE_PanelItemViewItem, option, painter,
    #         option.widget)
    #
    #     rect = option.rect
    #     val = index.data(Qt.DisplayRole)
    #     if isinstance(val, float):
    #         minv, maxv = self.scale
    #         val = (val - minv) / (maxv - minv)
    #         painter.save()
    #         if option.state & QStyle.State_Selected:
    #             painter.setOpacity(0.75)
    #         painter.setBrush(self.brush)
    #         painter.drawRect(
    #             rect.adjusted(1, 1, - rect.width() * (1.0 - val) - 2, -2))
    #         painter.restore()

    ########################################################################
    #  DİKEY CIZDIRIYOR---------------------------------------------------------------------
    ########################################################################

    #
    # def sizeHint(self, option, index):
    #     sh = super().sizeHint(option, index)
    #     return QSize(sh.height() + self.Margin * 2, sh.width())
    #
    # def paint(self, painter, option, index):
    #     option = QStyleOptionViewItem(option)
    #     self.initStyleOption(option, index)
    #
    #     if not option.text:
    #         return
    #
    #     if option.widget is not None:
    #         style = option.widget.style()
    #     else:
    #         style = QApplication.style()
    #     style.drawPrimitive(
    #         QStyle.PE_PanelItemViewRow, option, painter,
    #         option.widget)
    #     cell_rect = option.rect
    #     itemrect = QRect(0, 0, cell_rect.height(), cell_rect.width())
    #     opt = QStyleOptionViewItem(option)
    #     opt.rect = itemrect
    #     textrect = style.subElementRect(
    #         QStyle.SE_ItemViewItemText, opt, opt.widget)
    #
    #     painter.save()
    #     painter.setFont(option.font)
    #
    #     if option.displayAlignment & (Qt.AlignTop | Qt.AlignBottom):
    #         brect = painter.boundingRect(
    #             textrect, option.displayAlignment, option.text)
    #         diff = textrect.height() - brect.height()
    #         offset = max(min(diff / 2, self.Margin), 0)
    #         if option.displayAlignment & Qt.AlignBottom:
    #             offset = -offset
    #
    #         textrect.translate(0, offset)
    #
    #     painter.translate(option.rect.x(), option.rect.bottom())
    #     painter.rotate(-90)
    #     painter.drawText(textrect, option.displayAlignment, option.text)
    #     painter.restore()
    ########################################################################
    #  DİKEY CIZDIRIYOR---------------------------------------------------------------------
    ########################################################################

    class BoldFontDelegate(QStyledItemDelegate):
        """Paints the text of associated cells in bold font.

        Can be used e.g. with QTableView.setItemDelegateForColumn() to make
        certain table columns bold, or if callback is provided, the item's
        model index is passed to it, and the item is made bold only if the
        callback returns true.

        Parameters
        ----------
        parent: QObject
            The parent QObject.
        callback: callable
            Accepts model index and returns True if the item is to be
            rendered in bold font.
        """

        def __init__(self, parent=None, callback=None):
            super().__init__(parent)
            self._callback = callback

        def paint(self, painter, option, index):
            """Paint item text in bold font"""
            if not callable(self._callback) or self._callback(index):
                option.font.setWeight(option.font.Bold)
            super().paint(painter, option, index)

        def sizeHint(self, option, index):
            """Ensure item size accounts for bold font width"""
            if not callable(self._callback) or self._callback(index):
                option.font.setWeight(option.font.Bold)
            return super().sizeHint(option, index)

        ########################################################################
