# -*- coding: utf-8 -*-

__project_name__ = 'defter'
__date__ = '10/6/23'
__author__ = 'E. Y.'

from PySide6.QtWidgets import QToolBar


#######################################################################
class ToolBar(QToolBar):

    def __init__(self, title, parent=None):
        super(ToolBar, self).__init__(title, parent)

        stil2 = """

         QToolBar {
                background: #eee;
                padding: 0px;
                border: 0px;
                border-radius: 5px;
            }
        QToolBar QToolButton{
            background-color: #eee;
            border: 0px;
            padding: 5px;
            border-radius: 5px;
        }
                QToolBar QToolButton:hover{
            background-color: #def;
        }
        QToolBarExtension {
            background-color: black;
        }
        QPushButton QMenu
        {
            height: 1px;
            border-bottom: 1px solid lightGray;
            background: #5A5A5A;
            margin-left: 2px;
            margin-right: 0px;
            margin-top: 2px;
            margin-bottom: 2px;
         }
        QPushButton QMenu::separator
        {
            height: 1px;
            border-bottom: 1px solid lightGray;
            background: #5A5A5A;
            margin-left: 2px;
            margin-right: 0px;
            margin-top: 2px;
            margin-bottom: 2px;
         }
        
         QToolButton { /* all types of tool button */
            border: 2px solid #8f8f91;
            border-radius: 6px;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #f6f7fa, stop: 1 #dadbde);
        }
        
        QToolButton[popupMode="1"] { /* only for MenuButtonPopup */
            padding-right: 20px; /* make way for the popup button */
        }
        
        QToolButton:pressed {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #dadbde, stop: 1 #f6f7fa);
        }
        
        /* the subcontrols below are used only in the MenuButtonPopup mode */
        QToolButton::menu-button {
            border: 2px solid gray;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            /* 16px width + 4px for border = 20px allocated above */
            width: 16px;
        }
        
        QToolButton::menu-arrow {
            image: url(downarrow.png);
        }
        
        QToolButton::menu-arrow:open {
            top: 1px; left: 1px; /* shift it a bit */
        }

                """

        # border-radius: 5px;

        stil = """
         QToolBar {
                background: #eee;
                padding: 3px;
                border: 0px;
                border-radius: 3px;

            }
        QToolBar QToolButton{
            background-color: #eee;
            border: 0;
            padding: 3px;
            border-radius: 3px;
        }
        QToolBar QToolButton:hover{
            background-color: #def;
        }
        QToolBar QToolButton:pressed{
            background-color: #cde;
        }
        QToolBar QToolButton:checked{
            background-color: #ced5e1;
        }
        QToolButton[popupMode="1"] { /* only for MenuButtonPopup */
            padding-right: 20px; /* make way for the popup button */
        }
        
        /* the subcontrols below are used only in the MenuButtonPopup mode */
        QToolButton::menu-button {
            border: 0px;
            border-top-right-radius: 5px;
            border-bottom-right-radius: 5px;
            /* 16px width + 4px for border = 20px allocated above */
            width: 16px;
        }


        QToolButton::menu-arrow:open {
            top: 1px; left: 1px; /* shift it a bit */
        }
        """

        # QToolButton:pressed {
        #     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        #                                       stop: 0 #dadbde, stop: 1 #f6f7fa);
        # }

        self.setStyleSheet(stil)
