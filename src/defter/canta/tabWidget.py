# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '3/28/16'

from PySide6.QtWidgets import QTabWidget
from PySide6.QtCore import Slot
from .treeModel import DokumanAgacModel


#######################################################################
class TabWidget(QTabWidget):

    # tabWidgetFocusedIn = Signal()

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):

        super(TabWidget, self).__init__(parent)
        self.modeller = []
        self.cModel = None

        self.setContentsMargins(0, 0, 0, 0)

    # # ---------------------------------------------------------------------
    # def mousePressEvent(self, a0):
    #     super(TabWidget, self).mousePressEvent(a0)
    #     print(self.cDokuman.sayfalar)
    #

    # ---------------------------------------------------------------------
    def model_ekle(self, tempDirPath):
        model = DokumanAgacModel(tempDirPath, self)
        # currentIndex yoksa -1 donduruyor o da ilk eklerken 0 yapar
        self.modeller.insert(self.currentIndex() + 1, model)
        self.cModel = model
        return model

    # ---------------------------------------------------------------------
    def model_sil(self, model):
        # idx = self.dokumanlar.index(dokuman)
        # for sayfa in dokuman.sayfalar:
        #     dokuman.sayfa_sil(sayfa)
        self.modeller.remove(model)
        model.sifirla()
        model.setParent(None)
        model.deleteLater()
        # TODO: ??
        # self.cDokuman = self.dokumanlar[idx]
        # self.cDokuman daha sonra set ediliyor, close_selected_tab tan _remove_tab cagriliyor
        # burasi _remove_tabtan cagriliyor, burdan cikinca ve _remove_tabtab cikinca
        # focus_current_tab_and_change_window_name cagriliyor orda tabWidget.cDokuman set ediliyor

    # ---------------------------------------------------------------------
    @Slot(int, int)
    def model_sira_degistir(self, frm, to):
        # tab order in tabWidget.tablar is important
        self.modeller[frm], self.modeller[to] = self.modeller[to], self.modeller[frm]

    # # ---------------------------------------------------------------------
    # def dokumana_sayfa_ekle(self, dokuman, sayfa):
    #     dokuman.sayfa_ekle(sayfa)
    #
    # # ---------------------------------------------------------------------
    # def dokumandan_sayfa_sil(self,dokuman, sayfa):
    #     dokuman.sayfa_sil(sayfa)

    # ---------------------------------------------------------------------
    def sayfalari_getir(self, widget):
        pass

    # ---------------------------------------------------------------------
    def current_sayfa(self):
        pass

    # # ---------------------------------------------------------------------
    # def tabInserted(self, p_int):
    #     print("eklendi ", p_int)
    #     super(TabWidget, self).tabInserted(p_int)
    #
    # # ---------------------------------------------------------------------
    # def tabRemoved(self, p_int):
    #     print("silindi", p_int)
    #     super(TabWidget, self).tabRemoved(p_int)

    # ---------------------------------------------------------------------
    def tab_olustur(self, view_widget, dosya_adi, sayfa_adi):

        idx = self.currentIndex()
        # self.insertTab((idx + 1), view, scene.fileName)

        self.insertTab((idx + 1), view_widget, "{} - {}".format(dosya_adi, sayfa_adi))
        self.setCurrentIndex(idx + 1)

        self.setTabToolTip(self.currentIndex(), self.tr("Unsaved File"))

    # ---------------------------------------------------------------------
    def get_all_widgets_temp_dir_paths(self):
        temp_dir_paths = []
        for i in range(self.count()):
            temp_dir_paths.append(self.widget(i).scene().tempDirPath)
        return temp_dir_paths

    # # ---------------------------------------------------------------------
    # def get_index_of_tab_from_path__(self, path):
    #     index = None
    #     for i in range(self.count()):
    #         tab = self.widget(i)
    #         if tab.scene().saveFilePath == path:
    #             index = self.indexOf(tab)
    #             break
    #     return index

    # ---------------------------------------------------------------------
    def get_index_of_tab_from_path(self, path):
        index = None
        for model in self.modeller:
            if model.saveFilePath == path:
                index = self.modeller.index(model)
                break
        return index

    # # ---------------------------------------------------------------------
    # def get_all_paths_of_tabs(self):
    #     paths = []
    #     for i in range(self.count()):
    #         paths.append(self.widget(i).path)
    #     return paths

    # ---------------------------------------------------------------------
    def get_current_widget_with_path(self, path):

        index = self.get_index_of_tab_from_path(path)
        # if index and index > -1:  # index 0 olabiliyor o da if 0 olunca problem oluyor :)
        if index is not None and index > -1:  # if index or index==0 : if index > -1 gibi bir sey de belki olurdu:
            return self.widget(index)
        else:
            return None

    # ---------------------------------------------------------------------
    def set_current_widget_with_path(self, path):

        currentWidget = self.get_current_widget_with_path(path)
        if currentWidget:
            self.setCurrentWidget(currentWidget)
            return True
        else:
            return False
