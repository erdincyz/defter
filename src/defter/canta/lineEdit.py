# -*- coding: utf-8 -*-
# .

__project_name__ = 'defter'
__date__ = '9/18/23'
__author__ = 'E. Y.'

from PySide6.QtCore import Signal, QSize, Qt, Slot
from PySide6.QtWidgets import QLineEdit, QToolButton, QStyle
from . import icons_rc


#######################################################################
class AraLineEdit(QLineEdit):
    temizleBtnClicked = Signal()
    shiftEnterVeyaReturnBasildi = Signal()
    returnVeyaEnterBasildi = Signal()
    aramaMetniDegisti = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(AraLineEdit, self).__init__(parent)

        self.temizleBtn = QToolButton(self)
        self.temizleBtn.setIconSize(QSize(16, 16))
        # self.temizleBtn = QtGui.QPushButton(self)
        # self.temizleBtn.setText("clear")
        # self.temizleBtn.setIcon(QIcon(':icons/filtre-temizle-aktif.png'))
        self.temizleBtn.setStyleSheet(
            'QToolButton {border: 0px; padding: 0px; image: url(:canta/icons/filtre-temizle-pasif.png);}'
            'QToolButton:hover {image: url(:icons/filtre-temizle-uzerinde.png);}'
            'QToolButton:pressed {image: url(:icons/filtre-temizle-basili.png);}')
        # self.temizleBtn.setCursor(Qt.CursorShape.ArrowCursor)
        self.temizleBtn.clicked.connect(self.act_temizle)

        frameWidth = self.style().pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth)
        buttonSize = self.temizleBtn.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth * 2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth * 2 + 2))

        self.textEdited.connect(self.temizleBtn_durum_guncelle)
        self.textEdited.connect(self.aramaMetniDegisti)

    # ---------------------------------------------------------------------
    def resizeEvent(self, event):
        buttonSize = self.temizleBtn.sizeHint()
        frameWidth = self.style().pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth)
        self.temizleBtn.move(self.rect().right() - frameWidth - buttonSize.width(),
                             (self.rect().bottom() - buttonSize.height() + 1) / 2)
        super(AraLineEdit, self).resizeEvent(event)

    # ---------------------------------------------------------------------
    def act_temizle(self):
        self.clear()
        self.temizleBtn_durum_guncelle()
        self.aramaMetniDegisti.emit()

    # ---------------------------------------------------------------------
    @Slot()
    def temizleBtn_durum_guncelle(self):

        if self.text():
            self.temizleBtn.setStyleSheet(
                'QToolButton {border: 0px; padding: 0px; image: url(:icons/filtre-temizle-aktif.png);}'
                'QToolButton:hover {image: url(:icons/filtre-temizle-uzerinde.png);}'
                'QToolButton:pressed {image: url(:icons/filtre-temizle-basili.png);}')

        else:
            self.temizleBtn.setStyleSheet(
                'QToolButton {border: 0px; padding: 0px; image: url(:icons/filtre-temizle-pasif.png);}'
                'QToolButton:hover {image: url(:icons/filtre-temizle-uzerinde.png);}'
                'QToolButton:pressed {image: url(:icons/filtre-temizle-basili.png);}')

    # ---------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:

            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.shiftEnterVeyaReturnBasildi.emit()
            else:  # diger modiferlar da kaliyor ama olsun, cok onemli degil..
                self.returnVeyaEnterBasildi.emit()

        super(AraLineEdit, self).keyPressEvent(event)
