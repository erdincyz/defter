# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '26/1/22'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtCore import Qt, QPoint, Signal, QMimeData
from PySide6.QtGui import QColor, QDrag, QPixmap, QPainter, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QSizePolicy

from ..yanBolme.dikeyEtiket import DikeyEtiket


#######################################################################
class BaslikWidget(QWidget):
    sol_tiklandi = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, kapatilabilir_mi=False, parent=None):
        super(BaslikWidget, self).__init__(parent)
        self.solClickKucultBuyult = False

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        super(BaslikWidget, self).mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.solClickKucultBuyult = True
            self.mGPos = event.globalPosition()

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(BaslikWidget, self).mouseReleaseEvent(event)
        if self.solClickKucultBuyult:
            hareket = event.globalPosition().toPoint() - self.mGPos.toPoint()
            if hareket.manhattanLength() < 3:
                self.sol_tiklandi.emit()
                # event.ignore()
                # return
            self.solClickKucultBuyult = False


#######################################################################
class YuzenWidget(QWidget):
    kenaraAlVeyaKapatTiklandi = Signal(QWidget, bool)

    # ---------------------------------------------------------------------
    def __init__(self, kapatilabilir_mi=False, parent=None):
        super(YuzenWidget, self).__init__(parent)

        self.kapatilabilir_mi = kapatilabilir_mi
        self.parkPos = QPoint(0, 100)
        self.eskiAcikPos = QPoint(0, 100)
        self.eskiYuzenPos = QPoint(0, 0)
        self.eskiSize = self.size()
        self.setMinimumSize(100, 100)
        self.eskiMinimumSize = self.minimumSize()

        self.kucuk_mu = False
        self.dikey_mi = False
        self.yuzerken_dikey_miydi = False
        # ilk acilista True olmasi
        self.cubukta_mi = False
        self.sol_cubukta_mi = True
        self.sira = 0

        self.dugme = None

        self.renkYazi = QColor(255, 255, 255)
        # self.renkArkaplan = QColor(200, 205, 210)
        self.renkArkaplan = QColor(153, 170, 187)

        # self.setMinimumHeight(400)
        self.setAutoFillBackground(True)
        # self.setStyleSheet("QWidget {background-color: #ccc;}")
        self.setContentsMargins(0, 0, 0, 0)
        # ~ self.setWindowFlags(Qt.FramelessWindowHint|Qt.NoDropShadowWindowHint| Qt.Tool)
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowType.WindowStaysOnTopHint)
        # Tool olunca pencere disina da tasabiliyoır ve pencere ile hareket etmiyor.
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # self.setSizeGripEnabled(True)
        self.setStatusTip(self.tr("Move with left mouse button, resize with right mouse button."))
        # self.setToolTip(self.tr("Move with left mouse button, resize with right mouse button."))

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.mPos = QPoint()
        self.sagClick = False
        self.solClick = False
        self.solClickKucultBuyult = False

        self.baslikWidget = BaslikWidget(self)
        self.baslikWidget.sol_tiklandi.connect(self.kucult_buyult)
        # self.baslikWidget.setFixedHeight(20)
        self.baslikWidget.setContentsMargins(0, 0, 0, 0)
        self.baslikWidget.setAutoFillBackground(True)

        p = self.baslikWidget.palette()
        p.setColor(self.baslikWidget.foregroundRole(), self.renkYazi)
        p.setColor(self.baslikWidget.backgroundRole(), self.renkArkaplan)
        self.baslikWidget.setPalette(p)

        self.baslikEtiket = DikeyEtiket(self.baslikWidget, dikey=False)
        self.baslikEtiket.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btnKucult = QPushButton("<", self.baslikWidget)
        self.btnKucult.setFixedWidth(20)
        self.btnKucult.setFlat(True)
        self.btnKucult.setAutoFillBackground(True)
        self.btnKucult.clicked.connect(self.kucult_buyult)

        p = self.btnKucult.palette()
        p.setColor(self.btnKucult.foregroundRole(), self.renkYazi)
        p.setColor(self.btnKucult.backgroundRole(), self.renkArkaplan)
        self.btnKucult.setPalette(p)

        self.btnDondur = QPushButton("o", self.baslikWidget)
        self.btnDondur.setFixedWidth(20)
        self.btnDondur.setFlat(True)
        self.btnDondur.setAutoFillBackground(True)
        self.btnDondur.clicked.connect(lambda: self.dondur(not self.dikey_mi))
        # self.btnDondur.hide()

        p = self.btnDondur.palette()
        p.setColor(self.btnDondur.foregroundRole(), self.renkYazi)
        p.setColor(self.btnDondur.backgroundRole(), self.renkArkaplan)
        self.btnDondur.setPalette(p)

        if self.kapatilabilir_mi:
            yazi = "x"
        else:
            yazi = "#"
        self.btnKenaraAlVeyaKapat = QPushButton(yazi, self.baslikWidget)
        self.btnKenaraAlVeyaKapat.setFixedWidth(20)
        self.btnKenaraAlVeyaKapat.setFlat(True)
        self.btnKenaraAlVeyaKapat.setAutoFillBackground(True)
        self.btnKenaraAlVeyaKapat.clicked.connect(self.kenara_al_veya_kapat)

        p = self.btnKenaraAlVeyaKapat.palette()
        p.setColor(self.btnKenaraAlVeyaKapat.foregroundRole(), self.renkYazi)
        p.setColor(self.btnKenaraAlVeyaKapat.backgroundRole(), self.renkArkaplan)
        self.btnKenaraAlVeyaKapat.setPalette(p)

        self.anaLay = QVBoxLayout(self)
        self.anaLay.setContentsMargins(0, 0, 0, 0)
        self.anaLay.setSpacing(0)
        # self.anaLay.setSizeConstraint(QVBoxLayout.SetFixedSize)

        self.layBaslik = QHBoxLayout()
        self.layBaslik.setContentsMargins(0, 0, 0, 0)
        # self.layBaslik.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMaximumSize)

        # lay.addStretch()
        # 2 dugme icin 36
        # lay.addSpacing(36)
        # 1 dugme icin 16
        # lay.addSpacing(16)
        self.layBaslik.addWidget(self.btnKenaraAlVeyaKapat)
        self.layBaslik.addWidget(self.btnDondur)
        self.layBaslik.addWidget(self.baslikEtiket)
        self.layBaslik.addWidget(self.btnKucult)

        self.baslikWidget.setLayout(self.layBaslik)

        self.anaLay.addWidget(self.baslikWidget)

        self.icerikScroll = QScrollArea()
        self.icerikScroll.setContentsMargins(0, 0, 0, 0)
        # icerikScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # icerikScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.icerikScroll.setWidgetResizable(True)
        # scroll.setLayout(self.anaLay)
        self.anaLay.addWidget(self.icerikScroll)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    # ---------------------------------------------------------------------
    def yazBaslik(self, yazi):
        self.baslikEtiket.setText(yazi)

    # ---------------------------------------------------------------------
    def restoreGeometry(self, geo):
        super(YuzenWidget, self).restoreGeometry(geo)
        self.eskiSize = self.size()

    # ---------------------------------------------------------------------
    def ekleWidget(self, widget):
        # self.resize(widget.size())

        # gripper = QSizeGrip(widget)
        # l = QHBoxLayout(widget)
        #
        # l.setContentsMargins(0, 0, 0, 0)
        # l.addWidget(gripper, 0, Qt.AlignRight | Qt.AlignBottom)

        self.icerikScroll.setWidget(widget)
        # self.anaLay.addWidget(widget)

        # self.adjustSize()

    # # ---------------------------------------------------------------------
    # def sizeHint(self):
    #     # return self.baslikWidget.size() + self.icerikScroll.size()
    #
    #     if self.kucuk_mu:
    #         return self.baslikWidget.size()
    #     if self.dikey_mi:
    #         return self.icerikScroll.size() + QSize(20, 0)
    #     else:
    #         return self.icerikScroll.size() + QSize(0, 20)

    # # ---------------------------------------------------------------------
    # def resizeEvent(self, event):
    #
    #     super(YuzenWidget, self).resizeEvent(event)

    # ---------------------------------------------------------------------
    def kaydetme_bilgisi(self):
        return f"{int(self.dikey_mi)}" \
               f"{int(self.kucuk_mu)}" \
               f"{int(self.cubukta_mi)}" \
               f"{int(self.sol_cubukta_mi)}" \
               f"{self.sira}"

    # ---------------------------------------------------------------------
    def yukleme_bilgisi(self, bilgi):
        dikey_mi = bool(int(bilgi[0]))
        self.kucuk_mu = bool(int(bilgi[1]))
        self.cubukta_mi = bool(int(bilgi[2]))
        self.sol_cubukta_mi = bool(int(bilgi[3]))
        self.sira = int(bilgi[4])

        if self.cubukta_mi:
            # kenaraAlVeyaKapatTiklandi asil emit edildigi yer burasi degil
            # simdilik mekanizmadan faydalaniyoruz, acilista, kaydedilmis bilgiler
            # okunup ywler burda guncellenince, dugmeye tiklanmis gibi eski yerlerine yerlestiriyoruz
            self.kenaraAlVeyaKapatTiklandi.emit(self, True)
        else:
            # self.dondur(dikey_dondur=dikey_mi)
            if dikey_mi:
                self.dikey_dondur()

        # degiskene bilgi girildi ama daha kucultulup buyutulmedigi icin terslemiyoruz degiskeni
        if self.kucuk_mu:
            self.kucult(ilk_acilis_mi=True)
        else:
            self.buyult(ilk_acilis_mi=True)

    # ---------------------------------------------------------------------
    def setMinimumWidthVeEskiMinimumSize(self, width):
        # metod override ozellikle yapilmadi
        self.setMinimumWidth(width)
        self.eskiMinimumSize = self.minimumSize()

    # ---------------------------------------------------------------------
    def moveEvent(self, event):
        if self.kucuk_mu:
            # self.parkPos = event.oldPos()
            self.parkPos = event.pos()
        else:
            self.eskiAcikPos = event.pos()
        super(YuzenWidget, self).moveEvent(event)

    # ---------------------------------------------------------------------
    def sola_yasla(self):
        self.layBaslik.setDirection(QHBoxLayout.Direction.LeftToRight)
        self.btnKucult.setText("<")
        self.sol_cubukta_mi = True

    # ---------------------------------------------------------------------
    def saga_yasla(self):
        self.layBaslik.setDirection(QHBoxLayout.Direction.RightToLeft)
        self.btnKucult.setText(">")
        self.sol_cubukta_mi = False

    # ---------------------------------------------------------------------
    def cubuga_tasindi_yuklenirken(self, solSag):
        self.eskiYuzenPos = self.pos()
        self.eskiSize = self.size()

        if solSag == "sol":
            self.sola_yasla()
        elif solSag == "sag":
            self.saga_yasla()

        # self.baslikWidget.hide()
        self.btnDondur.hide()
        # self.btnKenaraAlVeyaKapat.hide()

    # ---------------------------------------------------------------------
    def cubuga_tasindi(self, solSag):

        self.eskiYuzenPos = self.pos()
        self.eskiSize = self.size()
        self.dikey_mi = self.baslikEtiket.dikey

        if self.dikey_mi:
            self.yuzerken_dikey_miydi = True
            self.yatay_dondur()
        else:
            self.yuzerken_dikey_miydi = False

        if solSag == "sol":
            self.sola_yasla()
        elif solSag == "sag":
            self.saga_yasla()

        # self.baslikWidget.hide()
        if self.kucuk_mu:
            self.buyult()
        self.btnDondur.hide()
        # # self.btnKucult.hide()
        # self.btnKenaraAlVeyaKapat.hide()
        self.cubukta_mi = True

    # ---------------------------------------------------------------------
    def cubuktan_atildi(self):
        self.baslikWidget.show()
        self.btnDondur.show()
        # # self.btnKucult.show()
        # self.btnKenaraAlVeyaKapat.show()

        if self.yuzerken_dikey_miydi:
            self.dikey_dondur()

        self.cubukta_mi = False
        self.move(self.eskiYuzenPos)
        self.resize(self.eskiSize)
        self.adjustSize()

    # ---------------------------------------------------------------------
    def kenara_al_veya_kapat(self):

        if self.kapatilabilir_mi:
            self.hide()
        else:
            # kenara aliyoruz
            # self.btnKenaraAlVeyaKapat.hide()
            # self.kucult()
            # self.move(self.parkPos)

            self.kenaraAlVeyaKapatTiklandi.emit(self, False)

    # ---------------------------------------------------------------------
    def dondur(self, dikey_dondur):
        # self.icerikScroll.setVisible(not self.icerikScroll.isVisible())

        if dikey_dondur:
            self.dikey_dondur()
        else:
            self.yatay_dondur()

    # ---------------------------------------------------------------------
    def dikey_dondur(self):
        self.setMinimumWidth(20)
        self.dikey_mi = True
        self.baslikEtiket.dikey = True
        self.baslikEtiket.setFixedSize(16777215, 16777215)
        self.baslikEtiket.resize(self.baslikEtiket.size().transposed())
        self.baslikEtiket.setFixedWidth(20)
        self.baslikEtiket.update()
        self.baslikWidget.setFixedSize(16777215, 16777215)
        self.baslikWidget.resize(self.baslikWidget.size().transposed())
        self.baslikWidget.setFixedWidth(20)
        self.baslikWidget.update()
        self.layBaslik.setDirection(QVBoxLayout.Direction.TopToBottom)
        if self.sol_cubukta_mi:
            self.anaLay.setDirection(QVBoxLayout.Direction.LeftToRight)
        else:
            self.anaLay.setDirection(QVBoxLayout.Direction.RightToLeft)
        self.adjustSize()
        # self.resize(self.size().transposed())

    # ---------------------------------------------------------------------
    def yatay_dondur(self):
        self.setMinimumHeight(20)
        self.dikey_mi = False
        self.baslikEtiket.dikey = False
        self.baslikEtiket.setFixedSize(16777215, 16777215)
        self.baslikEtiket.resize(self.baslikEtiket.size().transposed())
        self.baslikEtiket.setFixedHeight(20)
        self.baslikEtiket.update()
        self.baslikWidget.setFixedSize(16777215, 16777215)
        # self.baslikWidget.setFixedSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
        self.baslikWidget.resize(self.baslikWidget.size().transposed())
        self.baslikWidget.setFixedHeight(20)
        self.baslikWidget.update()
        self.layBaslik.setDirection(QVBoxLayout.Direction.LeftToRight)
        self.anaLay.setDirection(QVBoxLayout.Direction.TopToBottom)

        self.adjustSize()
        # self.resize(self.size().transposed())

    # ---------------------------------------------------------------------
    def kucult(self, ilk_acilis_mi=False):
        # if self.baslikEtiket.dikey:
        #     if self.anaLay.direction() == QVBoxLayout.Direction.RightToLeft:
        #         self.move(self.pos() + QPoint(self.icerikScroll.rect().width(), 0))

        self.kucuk_mu = True
        if self.cubukta_mi:
            self.hide()
            self.dugme.renk_degistir(acik_mi=False)
            # if not self.dikey_mi:
            #     self.dikey_dondur()
        else:
            self.eskiSize = self.size()
            self.icerikScroll.hide()
            # yuzuyor olsa da hangi cubukta dugmesi var
            if self.sol_cubukta_mi:
                self.btnKucult.setText(">")
            else:
                if self.dikey_mi:
                    self.btnKucult.setText("<")
                    if not ilk_acilis_mi:
                        self.move(self.pos() + QPoint(self.width() - 20, 0))
                else:
                    self.btnKucult.setText(">")

            if self.dikey_mi:
                self.setMinimumWidth(20)
            else:
                self.setMinimumHeight(20)
            self.adjustSize()
            # self.resize(self.baslikWidget.size())

    # ---------------------------------------------------------------------
    def buyult(self, ilk_acilis_mi=False):
        # if self.dikey_mi:
        #     if (self.pos().x() + self.icerikScroll.rect().width()) < self.parent().rect().width():
        #         self.anaLay.setDirection(QVBoxLayout.Direction.RightToLeft)
        #     else:
        #         self.anaLay.setDirection(QVBoxLayout.Direction.LeftToRight)
        #
        #     if self.anaLay.direction() == QVBoxLayout.Direction.RightToLeft:
        #         self.move(self.pos() + self.mapToParent(self.rect().topLeft()))
        #
        # else:
        #     if self.pos().y() + self.icerikScroll.rect().height() < self.parent().rect().height():
        #         self.anaLay.setDirection(QVBoxLayout.Direction.TopToBottom)
        #     else:
        #         self.anaLay.setDirection(QVBoxLayout.Direction.BottomToTop)

        self.kucuk_mu = False
        self.setMinimumSize(self.eskiMinimumSize)
        if self.cubukta_mi:
            self.show()
            self.dugme.renk_degistir(acik_mi=True)
        else:
            self.icerikScroll.show()
            self.resize(self.eskiSize)
            self.adjustSize()
            # yuzuyor olsa da hangi cubukta dugmesi var
            if self.sol_cubukta_mi:
                self.btnKucult.setText("<")
            else:
                if self.dikey_mi:
                    self.btnKucult.setText(">")
                    if not ilk_acilis_mi:
                        self.move(self.pos() - QPoint(self.icerikScroll.width(), 0))
                else:
                    self.btnKucult.setText("<")
            # self.btnKucult.setText("<")

    # ---------------------------------------------------------------------
    def kucult_buyult(self):

        if self.kucuk_mu:
            self.buyult()
        else:
            self.kucult()

    # # ---------------------------------------------------------------------
    # def mouseDoubleClickEvent(self, event):
    #
    #     self.kenara_al_veya_kapat()
    #     # self.kucult_buyult()
    #
    #     # if self.cubukta_mi:
    #     #     self.kenara_al_veya_kapat()
    #     # else:
    #     #     self.kucult_buyult()
    #     super(YuzenWidget, self).mouseDoubleClickEvent(event)

    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):

        super(YuzenWidget, self).mousePressEvent(event)

        if not self.cubukta_mi:
            self.raise_()

            if event.button() == Qt.MouseButton.LeftButton:
                self.mPos = event.pos()
                self.solClick = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

            if event.button() == Qt.MouseButton.RightButton and self.icerikScroll.isVisible():
                self.sagDragx = event.x()
                self.sagDragy = event.y()
                self.enSagX = self.width()
                self.enAltY = self.height()
                self.sagClick = True
                self.setCursor(Qt.CursorShape.SizeAllCursor)

    # ---------------------------------------------------------------------
    def sag_kenara_yanastir(self):
        pr = self.parent().rect()
        self.move(pr.right() - self.width() - 9, pr.top() + 30)

    # ---------------------------------------------------------------------
    def sol_kenara_yanastir(self):
        pr = self.parent().rect()
        self.move(10, pr.top() + 30)

    # ---------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        super(YuzenWidget, self).mousePressEvent(event)
        if not self.cubukta_mi:
            if event.buttons() & Qt.MouseButton.LeftButton:
                if self.solClick:
                    fark = event.pos() - self.mPos
                    yeniPos = self.pos() + fark
                    pr = self.parent().rect()
                    if yeniPos.x() < 10:
                        yeniPos.setX(10)
                        # self.dikey_dondur()
                        # self.anaLay.setDirection(QVBoxLayout.Direction.LeftToRight)
                    elif yeniPos.x() + self.width() > pr.right() - 9:
                        yeniPos.setX(pr.right() - self.width() - 9)
                        # self.dikey_dondur()
                        # self.anaLay.setDirection(QVBoxLayout.Direction.RightToLeft)

                    # if yeniPos.y() < 0:
                    #     yeniPos.setY(0)
                    if yeniPos.y() < 30:
                        yeniPos.setY(30)
                        # self.yatay_dondur()
                        # self.anaLay.setDirection(QVBoxLayout.Direction.TopToBottom)
                    elif yeniPos.y() + self.height() > pr.bottom():
                        yeniPos.setY(pr.bottom() - self.height())
                        # self.yatay_dondur()
                        # self.anaLay.setDirection(QVBoxLayout.Direction.BottomToTop)

                    self.move(yeniPos)

            if self.sagClick:
                genislik = max(self.icerikScroll.minimumWidth(),
                               self.enSagX + event.x() - self.sagDragx)
                yukseklik = max(self.icerikScroll.minimumHeight(),
                                self.enAltY + event.y() - self.sagDragy)
                self.resize(genislik, yukseklik)

                # if self.dikey_mi:
                #     self.baslikEtiket.setFixedHeight(yukseklik)
                #     # self.baslikEtiket.resize(self.baslikEtiket.size().width(), yukseklik)
                # else:
                #     self.baslikEtiket.setFixedWidth(genislik)
                #     # self.baslikEtiket.resize(genislik, self.baslikEtiket.size().height())

                # self.eskiSize = QSize(genislik, yukseklik)

        else:
            if event.buttons() == Qt.MouseButton.LeftButton:
                drag = QDrag(self)
                mime = QMimeData()
                drag.setMimeData(mime)

                pixmap = QPixmap(self.size())
                self.render(pixmap)
                painter = QPainter(pixmap)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
                # painter.setOpacity(50)
                # painter.fillRect(pixmap.rect(), QColor(200, 210, 255))
                painter.setPen(QPen(QColor(0, 191, 255), 5, Qt.PenStyle.DotLine))
                painter.drawRect(pixmap.rect())
                painter.end()
                # drag.setHotSpot(QPoint(pixmap.width()/2, pixmap.height()))
                drag.setHotSpot(event.pos() - self.rect().topLeft())
                drag.setPixmap(pixmap)

                drag.exec(Qt.DropAction.MoveAction)

    # ---------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(YuzenWidget, self).mouseReleaseEvent(event)

        if not self.cubukta_mi:
            self.sagClick = False
            self.solClick = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
