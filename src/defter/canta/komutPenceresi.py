# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit, QApplication
from PySide6.QtCore import Qt, Slot, QSettings
from . import shared


########################################################################
class CommandDialog(QDialog):

    # logger = Signal(str)

    # def __init__(self, item, blenderHistory=None, parent=None):
    def __init__(self, item, parent=None):
        super(CommandDialog, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout(self)
        btnLayout = QHBoxLayout()

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setPlaceholderText("Title")
        layout.addWidget(self.lineEdit)
        self.textEdit = QTextEdit(self)
        layout.addWidget(self.textEdit)
        command = item.command()
        if command:
            self.lineEdit.setText(command["title"])
            self.textEdit.setPlainText(command["command"])

        # blenderHistoryListWidget = QListWidget(self)
        # editlayout.addWidget(blenderHistoryListWidget)
        closeBtn = QPushButton("&Close", self)
        closeBtn.setDefault(True)
        closeBtn.clicked.connect(self.reject)
        saveBtn = QPushButton("&Save", self)
        saveBtn.clicked.connect(lambda: self.act_save_command(item))
        btnLayout.addStretch()
        btnLayout.addWidget(closeBtn)
        btnLayout.addWidget(saveBtn)
        layout.addLayout(btnLayout)

        self.olustur_ayarlar()
        self.oku_ayarlar()
        # commandDialog.accepted.connect()

    # ---------------------------------------------------------------------
    def closeEvent(self, event):
        self.yaz_ayarlar()
        event.accept()

    # ---------------------------------------------------------------------
    def olustur_ayarlar(self):
        QApplication.setOrganizationName(shared.DEFTER_ORG_NAME)
        QApplication.setOrganizationDomain(shared.DEFTER_ORG_DOMAIN)
        QApplication.setApplicationName(shared.DEFTER_APP_NAME)
        self.settings = QSettings(shared.DEFTER_AYARLAR_DOSYA_ADRES, QSettings.Format.IniFormat)
        # self.settings.clear()

    # ---------------------------------------------------------------------
    def oku_ayarlar(self):
        self.settings.beginGroup("CommandDialogSettings")
        if self.settings.contains("CWinGeometry"):
            self.restoreGeometry(self.settings.value("CWinGeometry"))
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    def yaz_ayarlar(self):
        self.settings.beginGroup("CommandDialogSettings")
        self.settings.setValue("CWinGeometry", self.saveGeometry())
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    @Slot()
    def act_save_command(self, item):
        title = self.lineEdit.text()
        command = self.textEdit.toPlainText()
        if command:
            item.setCommand(title=title,
                            command=command)
            item.setText(title)
        # else:
        #     self.logger.emit("no command")
