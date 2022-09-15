import sys
import traceback
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication

from window_main import WindowMain


def main(argv):
    app = QApplication(argv)
    app.setApplicationName("EasyPrint")
    app.setApplicationDisplayName("EasyPrint")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("EasyPrint")
    app.setOrganizationDomain("https://github.com/AmirMahmood/")

    translator = QTranslator()
    print(translator.load("fa", directory=str(Path(__file__).parent / 'locales')))
    app.installTranslator(translator)

    if QtCore.QT_VERSION >= 0x50501:
        def excepthook(type_, value, traceback_):
            traceback.print_exception(type_, value, traceback_)
            QtCore.qFatal("")

        sys.excepthook = excepthook

    window = WindowMain()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main(sys.argv)
