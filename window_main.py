# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt, QStandardPaths, QTranslator, QEvent, QSettings
from PyQt5.QtWidgets import QMainWindow, QActionGroup, QAction, QApplication

from dialog_about import DialogAbout
from graphics_scene import CustomQGraphicsScene, CropType
from ui.ui_window_main import Ui_MainWindow


class WindowMain(Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        Ui_MainWindow.__init__(self)
        QMainWindow.__init__(self, parent=parent)
        self.translator = QTranslator()
        self.setupUi(self)

        self.crop_type = CropType.CIRCLE
        self.zoom_factor = 1.2
        self.item_scale_factor = 0.98
        self.currentPage = 'A4'
        self.page_size_dict = {
            'A4': (2480, 3508),
            'A5': (1748, 2480),
        }

        self.scene = CustomQGraphicsScene(self)

        self.duplicateButton.clicked.connect(self.scene.duplicate_item)

        page_action_group = QActionGroup(self)
        page_action_group.setExclusive(True)
        page_action_group.addAction(self.actionA4)
        page_action_group.addAction(self.actionA5)
        page_action_group.triggered.connect(self.change_page)

        self.init_langs()

        self.actionAbout.triggered.connect(self.show_about_dialog)

        self.cirCropCheckBox.stateChanged.connect(self.crop_type_change)
        self.sqrCropCheckBox.stateChanged.connect(self.crop_type_change)
        self.rectCropCheckBox.stateChanged.connect(self.crop_type_change)

        self.actionSave.triggered.connect(self.save_png)
        self.actionRulers.triggered.connect(self.scene.change_ruler)

        self.cropCheckBox.stateChanged.connect(self.crop_mode_change)
        self.cropButton.clicked.connect(self.scene.crop)

        self.zoomInButton.clicked.connect(lambda x: self.graphicsView.scale(self.zoom_factor, self.zoom_factor))
        self.zoomOutButton.clicked.connect(
            lambda x: self.graphicsView.scale(1 / self.zoom_factor, 1 / self.zoom_factor))

        self.graphicsView.setBackgroundBrush(Qt.GlobalColor.black)
        self.scene.selectionChanged.connect(self.item_selection_changed)
        self.graphicsView.setScene(self.scene)

        self.reconstruct_page(*self.page_size_dict['A4'])
        self.graphicsView.scale(1 / (self.zoom_factor * 5), 1 / (self.zoom_factor * 5))

    def init_langs(self):
        langs = [
            ('English', ''),
            ('فارسی', 'fa')
        ]
        lang_action_g = QActionGroup(self)
        lang_action_g.setExclusive(True)
        curr_lang = QSettings().value('lang', '')
        for i, (name, code) in enumerate(langs):
            q = QAction(self)
            q.setCheckable(True)
            q.setData(code)
            q.setText(name)
            lang_action_g.addAction(q)
            self.menulang.addAction(q)
            if code == curr_lang:
                q.setChecked(True)
                self.change_lang(q)
        lang_action_g.triggered.connect(self.change_lang)

    def change_lang(self, action):
        code = action.data()
        QSettings().setValue('lang', code)
        if code:
            self.translator.load(code, directory=str(Path(__file__).parent / 'locales'))
            QApplication.instance().installTranslator(self.translator)
        else:
            QApplication.instance().removeTranslator(self.translator)

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi(self)
        super().changeEvent(event)

    def crop_type_change(self, checked):
        if checked == Qt.CheckState.Checked:
            sender = self.sender()
            if sender == self.sqrCropCheckBox:
                self.crop_type = CropType.SQUARE
            elif sender == self.cirCropCheckBox:
                self.crop_type = CropType.CIRCLE
            elif sender == self.rectCropCheckBox:
                self.crop_type = CropType.RECTANGLE
            self.crop_mode_change(self.cropCheckBox.checkState())

    def crop_mode_change(self, state):
        if state == Qt.CheckState.Checked:
            self.scene.set_crop(True, self.crop_type)
        elif state == Qt.CheckState.Unchecked:
            self.scene.set_crop(False, self.crop_type)
        self.toolbox_enable_update()

    def reconstruct_page(self, w, h):
        self.graphicsView.setSceneRect(0, 0, w, h)
        self.scene.reconstruct_page(w, h)

    def change_page(self, action):
        if action == self.actionA4:
            if self.currentPage != 'A4':
                self.currentPage = 'A4'
                self.reconstruct_page(*self.page_size_dict[self.currentPage])
        elif action == self.actionA5:
            if self.currentPage != 'A5':
                self.currentPage = 'A5'
                self.reconstruct_page(*self.page_size_dict[self.currentPage])

        self.pageSizeLabel.setText(self.currentPage)

    def item_selection_changed(self):
        try:
            self.rotationSlider.valueChanged.disconnect()
            self.scaleUpButton.clicked.disconnect()
            self.vscaleUpButton.clicked.disconnect()
            self.hscaleUpButton.clicked.disconnect()
            self.scaleDownButton.clicked.disconnect()
            self.vscaleDownButton.clicked.disconnect()
            self.hscaleDownButton.clicked.disconnect()
            self.itemUpButton.clicked.disconnect()
            self.itemDownButton.clicked.disconnect()
        except TypeError:
            pass
        self.rotationSlider.setValue(0)

        if len(self.scene.selectedItems()) == 1:
            item = self.scene.selectedItems()[0]

            self.rotationSlider.setValue(int(item.rotation()))
            self.rotationSlider.valueChanged.connect(item.setRotation)

            self.scaleUpButton.clicked.connect(lambda x: item.setScale(item.scale() * 1 / self.item_scale_factor))
            self.scaleDownButton.clicked.connect(lambda x: item.setScale(item.scale() * self.item_scale_factor))
            self.hscaleDownButton.clicked.connect(
                lambda x: item.setTransform(item.transform().scale(self.item_scale_factor, 1))
            )
            self.hscaleUpButton.clicked.connect(
                lambda x: item.setTransform(item.transform().scale(1 / self.item_scale_factor, 1))
            )
            self.vscaleDownButton.clicked.connect(
                lambda x: item.setTransform(item.transform().scale(1, self.item_scale_factor))
            )
            self.vscaleUpButton.clicked.connect(
                lambda x: item.setTransform(item.transform().scale(1, 1 / self.item_scale_factor))
            )

            self.itemUpButton.clicked.connect(lambda x: item.setZValue(item.zValue() + 1))
            self.itemDownButton.clicked.connect(lambda x: item.setZValue(item.zValue() - 1))

        self.toolbox_enable_update()

    def toolbox_enable_update(self):
        one_selection = len(self.scene.selectedItems()) == 1
        on_crop = self.cropCheckBox.isChecked()
        one_selection_without_crop = one_selection and not on_crop

        self.duplicateButton.setEnabled(one_selection_without_crop)
        self.scaleUpButton.setEnabled(one_selection_without_crop)
        self.scaleDownButton.setEnabled(one_selection_without_crop)
        self.vscaleUpButton.setEnabled(one_selection_without_crop)
        self.vscaleDownButton.setEnabled(one_selection_without_crop)
        self.hscaleUpButton.setEnabled(one_selection_without_crop)
        self.hscaleDownButton.setEnabled(one_selection_without_crop)

        self.itemUpButton.setEnabled(one_selection_without_crop)
        self.itemDownButton.setEnabled(one_selection_without_crop)

        self.rotationSlider.setEnabled(one_selection_without_crop)

        self.cirCropCheckBox.setEnabled(on_crop)
        self.sqrCropCheckBox.setEnabled(on_crop)
        self.rectCropCheckBox.setEnabled(on_crop)
        self.cropButton.setEnabled(on_crop)

        if not on_crop:
            self.cropCheckBox.setEnabled(one_selection)

    def save_png(self, clicked):
        desktop_path = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation))
        fname = datetime.now().strftime("%Y%m%d-%H%M%S")
        dist_path = str(desktop_path / f"{fname}.png")
        self.scene.save_png(dist_path)

    def show_about_dialog(self, clicked):
        di = DialogAbout(self)
        di.show()
