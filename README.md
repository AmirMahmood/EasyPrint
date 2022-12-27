# EasyPrint

## Installation
Standalone executables can be downloaded from [release page](https://github.com/AmirMahmood/EasyPrint/releases).

### Install from git
```
git clone https://github.com/AmirMahmood/EasyPrint.git
pip install -r requirements\base.txt
pyuic5 .\ui\window_main.ui -o .\ui\ui_window_main.py
pyuic5 .\ui\dialog_about.ui -o .\ui\ui_dialog_about.py
pyuic5 .\ui\dialog_favfont.ui -o .\ui\ui_dialog_favfont.py
pyrcc5 .\resources.qrc -o .\resources_rc.py
python main.py
```

### Create standalone executable
```
pip install -r requirements\dev.txt
pyinstaller.exe --clean --onefile --windowed -n EasyPrint main.py
```

## Update translation files
```
pylupdate5 ui\window_main.ui -ts locales\fa.ts
```
then use Qt linguist to compile ts files
