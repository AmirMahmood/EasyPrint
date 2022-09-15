# -*- coding: utf-8 -*-
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QDialog

from ui.ui_dialog_about import Ui_AboutDialog


class DialogAbout(Ui_AboutDialog, QDialog):
    def __init__(self, parent=None):
        Ui_AboutDialog.__init__(self)
        QDialog.__init__(self, parent=parent)
        self.setupUi(self)

        self.textBrowser.anchorClicked.connect(QDesktopServices.openUrl)
