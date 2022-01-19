# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'argekod'
__date__ = '3/28/16'

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit
from PySide6.QtCore import Qt, Slot, QCoreApplication, QSettings


########################################################################
class CommandDialog(QDialog):

    # logger = Signal(str)

    # def __init__(self, item, blenderHistory=None, parent=None):
    def __init__(self, item, parent=None):
        super(CommandDialog, self).__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
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

        self.init_settings()
        self.read_settings()
        # commandDialog.accepted.connect()

    # ---------------------------------------------------------------------
    def closeEvent(self, event):
        self.write_settings()
        event.accept()

    # ---------------------------------------------------------------------
    def init_settings(self):
        QCoreApplication.setOrganizationName("argekod")
        QCoreApplication.setOrganizationDomain("argekod")
        QCoreApplication.setApplicationName("Defter")
        self.settings = QSettings("./_settings.ini", QSettings.IniFormat)
        # self.settings.clear()

    # ---------------------------------------------------------------------
    def read_settings(self):
        self.settings.beginGroup("CommandDialogSettings")
        if self.settings.contains("CWinGeometry"):
            self.restoreGeometry(self.settings.value("CWinGeometry"))
        self.settings.endGroup()

    # ---------------------------------------------------------------------
    def write_settings(self):
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
