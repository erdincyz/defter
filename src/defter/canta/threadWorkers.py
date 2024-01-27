# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '20/Aug/2016'

from urllib.error import HTTPError
# from urllib.request import urlretrieve
from urllib.request import URLopener
from PySide6.QtCore import QObject, Slot, Signal, QPointF


# from PyQt5.QtGui import QIcon

# ########################################################################
# class IkonOlusturucuWorker(QObject):
#     ikon_olustur_sinyal = Signal(object, int)
#     ikon_olusturuldu = Signal(QIcon)
#
#     # ---------------------------------------------------------------------
#     def __init__(self, parent=None):
#         super(IkonOlusturucuWorker, self).__init__(parent)
#
#         self.ikon_olustur_sinyal.connect(self.act_ikon_olustur)
#
#     # ---------------------------------------------------------------------
#     @Slot(object, int)
#     def act_ikon_olustur(self, sayfa, tree_view_genislik):
#         view = sayfa.view
#         if view:
#             pixmap = view.grab(view.viewport().rect())
#             # pixmap = pixmap.scaled(128,128,Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
#             pixmap = pixmap.scaledToWidth(tree_view_genislik, Qt.FastTransformation)
#
#             self.ikon_olusturuldu.emit(QIcon(pixmap))
#
#             # idx = treeView.currentIndex()
#             # treeView.dataChanged(idx, idx)
#             print("tamam")
#         else:
#             "olmadi"


########################################################################
class DownloadWorker(QObject):
    downloadWithThread = Signal(str, str, QPointF)

    finished = Signal(str, str, QPointF, QObject)
    failed = Signal(QObject)
    log = Signal(str, int, int)
    percentage = Signal(int)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(DownloadWorker, self).__init__(parent)

        self.downloadWithThread.connect(self.download)

    # ---------------------------------------------------------------------
    @Slot(str, str, QPointF)
    def download(self, url, imageSavePath, scenePos):

        try:
            self.log.emit("Downloading image from: {}".format(url), 5000, 0)
            # urlretrieve(url, imageSavePath, reporthook=self.report)
            opener = URLopener()
            opener.addheader('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1')
            # filename, headers = opener.retrieve(url, imageSavePath, reporthook=self.report)
            opener.retrieve(url, imageSavePath, reporthook=self.report)

            self.log.emit("Image succesfully downloaded", 5000, 1)
            self.finished.emit(url, imageSavePath, scenePos, self)

        except HTTPError as e:
            self.log.emit("Could not load image: {} ({})".format(url, e), 5000, 2)
            self.failed.emit(self)

    # ---------------------------------------------------------------------
    def report(self, count, blockSize, totalSize):
        percent = int(count * blockSize * 100 / totalSize)

        self.log.emit("\r{0:d}% complete".format(percent), 1000, 0)
