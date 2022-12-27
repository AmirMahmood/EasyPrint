# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QSettings

from ui.ui_dialog_favfont import Ui_FavFontDialog


class DialogFavFont(Ui_FavFontDialog, QDialog):
    def __init__(self, parent=None):
        Ui_FavFontDialog.__init__(self)
        QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.addToolButton.clicked.connect(self.add_font)
        settings = QSettings()
        for fontn in settings.value('favfonts', []):
            self.plainTextEdit.appendPlainText(fontn)

    def add_font(self):
        fname = self.fontComboBox.currentFont().family()
        self.plainTextEdit.appendPlainText(fname)

    def closeEvent(self, event):
        fonts_set = set()
        for l in self.plainTextEdit.toPlainText().splitlines():
            fonts_set.add(l.strip())
        
        settings = QSettings()
        settings.setValue('favfonts', fonts_set)
