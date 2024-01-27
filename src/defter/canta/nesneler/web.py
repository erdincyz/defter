# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '21/Aug/2016'

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEngineSettings  # , QWebEngineProfile, QWebEnginePage
from PySide6.QtWidgets import QGraphicsProxyWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from ..nesneler.base import BaseItem
from .. import shared


########################################################################
class Web(BaseItem):
    Type = shared.WEB_ITEM_TYPE

    # ---------------------------------------------------------------------
    def __init__(self, html, dosyaAdresi, pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent=None):
        super(Web, self).__init__(pos, rect, yaziRengi, arkaPlanRengi, pen, font, parent)

        # web = QWebEngineView(self)
        # web.setAttribute(Qt.WA_DontShowOnScreen)
        # web.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        # web.settings().setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        # web.load(QUrl.fromLocalFile(dosyaAdresi))

        self.proxy = QGraphicsProxyWidget(self)
        # self.proxy.setFlags(self.ItemIsSelectable |
        #               self.ItemIsMovable |
        #               self.ItemIsFocusable)

        self.wView = QWebEngineView()
        # self.wView.setAttribute(Qt.WA_DontShowOnScreen)
        self.wView.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        if html:
            self.wView.setHtml(html)
        else:
            self.wView.load(QUrl.fromLocalFile(dosyaAdresi))

        # self.proxy.resize(self.wView.size())
        # self.proxy.resize(self.wView.size())
        # self.proxy.geometryChanged.connect(self.proxy_geometrisi_degisince_doc_size_ayarla)
        # self.proxy.setGeometry()

        self.proxy.setWidget(self.wView)
        # self.setRect(QRectF(self.wView.rect()))
        # self.proxy.resize(QSizeF(self.wView.size()))

        self.wView.resize(self._rect.size().toSize())

    # ---------------------------------------------------------------------
    def type(self):
        # Enable the use of qgraphicsitem_cast with this item.
        return Web.Type

    # ---------------------------------------------------------------------
    def varsaEnUsttekiGrubuGetir(self):
        parentItem = self.parentItem()
        while parentItem:
            if parentItem.type() == shared.GROUP_ITEM_TYPE:
                return parentItem
            parentItem = parentItem.parentItem()
        return None
