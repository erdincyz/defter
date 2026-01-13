# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '20/Aug/2016'

from urllib.request import Request, urlopen
from urllib.error import HTTPError
from PySide6.QtCore import QObject, Signal, QRunnable, QPointF, Slot


# from PySide6.QtGui import QIcon

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


class WorkerSignals(QObject):
    """
    QRunnable sinyal gönderemediği için sinyalleri taşıyan yardımcı sınıf.
    """
    finished = Signal(str, str, QPointF, object)  # url, path, pos, targetItem
    failed = Signal(str)
    log = Signal(str, int, int)
    percentage = Signal(int)


class DownloadWorker(QRunnable):
    """
    QRunnable tabanlı Worker. QThreadPool tarafından yönetilir.
    """

    def __init__(self, url, imageSavePath, scenePos, targetItem=None):
        super(DownloadWorker, self).__init__()
        self.url = url
        self.imageSavePath = imageSavePath
        self.scenePos = scenePos
        # Hedef nesneyi (targetItem) burada saklıyoruz, böylece indirme bitince
        # 'activeItem' değişmiş olsa bile doğru nesneyi bulabiliriz.
        self.targetItem = targetItem
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            self.signals.log.emit(f"Downloading image from: {self.url}", 5000, 0)

            # User-Agent eklemek önemli, bazı siteler Python requestlerini engeller.
            request = Request(
                self.url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )

            with urlopen(request, timeout=10) as response:  # Timeout eklemek iyidir
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                block_size = 8192

                with open(self.imageSavePath, "wb") as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break

                        f.write(buffer)
                        downloaded += len(buffer)

                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            self.signals.percentage.emit(percent)

            self.signals.log.emit("Image successfully downloaded", 5000, 1)
            # İşlem başarılı, gerekli verileri geri gönder
            self.signals.finished.emit(self.url, self.imageSavePath, self.scenePos, self.targetItem)

        except HTTPError as e:
            self.signals.log.emit(f"Could not load image: {self.url} ({e})", 5000, 2)
            self.signals.failed.emit(self.url)
        except Exception as e:
            self.signals.log.emit(f"Download error: {str(e)}", 5000, 2)
            self.signals.failed.emit(self.url)
