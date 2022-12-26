# -*- coding: utf-8 -*-
from enum import Enum

from PyQt5.QtCore import Qt, QRectF, QRect
from PyQt5.QtGui import QPixmap, QPainter, QImage, QBrush, QPen, QPainterPath
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem, QGraphicsRectItem, \
    QGraphicsSimpleTextItem


class CropType(Enum):
    RECTANGLE = 1
    SQUARE = 2
    CIRCLE = 3


class CustomQGraphicsScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crop_item = None
        self.item_to_crop = None
        self.crop_start_point = None
        self.crop_mode = False
        self.crop_type = None

        self.page_rect_item = None
        self.page_rect_border_item = None

        self.show_rulers = False
        self.ruler_items = None

        self.setBackgroundBrush(Qt.GlobalColor.white)

    def set_crop(self, enable, crop_type):
        print(enable, crop_type)
        if enable:
            if not self.crop_mode:
                self.item_to_crop = self.selectedItems()[0]
            self.crop_mode = True
            self.crop_type = crop_type
            self.clearSelection()
            for i in self.items():
                i.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        else:
            self.item_to_crop = None
            self.crop_mode = False
            self.crop_type = None
            self.removeItem(self.crop_item)
            self.crop_item = None
            self.crop_start_point = None
            for i in self.items():
                i.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            self.page_rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            self.page_rect_border_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            self.ruler_items.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def change_ruler(self, show_rulers):
        self.show_rulers = show_rulers
        if show_rulers:
            self.ruler_items.show()
        else:
            self.ruler_items.hide()

    def reconstruct_page(self, w, h):
        self.removeItem(self.page_rect_item)
        self.removeItem(self.page_rect_border_item)
        self.removeItem(self.ruler_items)

        self.page_rect_item = QGraphicsRectItem(0, 0, w, h)
        self.page_rect_item.setBrush(QBrush(Qt.GlobalColor.white, Qt.BrushStyle.SolidPattern))
        self.page_rect_item.setZValue(-999999)
        self.addItem(self.page_rect_item)
        self.page_rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.page_rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

        self.page_rect_border_item = QGraphicsRectItem(0, 0, w, h)
        self.page_rect_border_item.setBrush(QBrush(Qt.GlobalColor.transparent, Qt.BrushStyle.NoBrush))
        self.page_rect_border_item.setPen(QPen(Qt.GlobalColor.red, 9, Qt.DashDotLine, Qt.RoundCap, Qt.RoundJoin))
        self.page_rect_border_item.setZValue(999999)
        self.addItem(self.page_rect_border_item)
        self.page_rect_border_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.page_rect_border_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

        self.ruler_items = self.createItemGroup([
            self.addLine(int(w / 2), 0, int(w / 2), h, Qt.GlobalColor.blue),
            self.addLine(0, int(h / 2), w, int(h / 2), Qt.GlobalColor.blue)
        ])
        self.ruler_items.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.ruler_items.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.ruler_items.setZValue(999999)
        self.change_ruler(self.show_rulers)

    def save_png(self, dist_path):
        self.toggle_util_items()
        pixmap = QImage(self.page_rect_item.rect().size().toSize(), QImage.Format.Format_RGB16)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.render(painter, source=self.page_rect_item.rect())
        painter.end()
        print("Image saved:", pixmap.save(dist_path, quality=100))
        self.toggle_util_items()

    def crop(self, clicked):
        if not self.crop_item:
            return
        self.toggle_util_items()

        size_w, size_h = self.crop_item.rect().toAlignedRect().width(), self.crop_item.rect().toAlignedRect().height()

        target = QPixmap(size_w, size_h)
        target.fill(Qt.GlobalColor.transparent)

        qp = QPainter(target)
        qp.setRenderHints(QPainter.RenderHint.Antialiasing)
        sourceRect = QRectF(0, 0, size_w, size_h)
        sourceRect.moveCenter(self.crop_item.rect().center())
        self.crop_item.hide()
        self.render(qp, source=sourceRect)
        qp.end()
        self.crop_item.show()

        if self.crop_type == CropType.CIRCLE:
            target1 = QPixmap(size_w, size_h)
            target1.fill(Qt.GlobalColor.transparent)
            qp1 = QPainter(target1)
            qp1.setRenderHints(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size_w, size_h)
            qp1.setClipping(True)
            qp1.setClipPath(path)
            sourceRect = QRect(0, 0, size_w, size_h)
            sourceRect.moveCenter(target.rect().center())
            qp1.drawPixmap(target.rect(), target, sourceRect)
            qp1.end()
            target = target1

        self.removeItem(self.item_to_crop)
        i = self.add_image(target)
        i.setPos(self.crop_item.boundingRect().topLeft())
        self.toggle_util_items()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.crop_mode:
            if self.crop_item:
                self.removeItem(self.crop_item)
                self.crop_item = None
            self.crop_start_point = event.scenePos()
            if self.crop_type in [CropType.RECTANGLE, CropType.SQUARE]:
                self.crop_item = self.addRect(
                    self.crop_start_point.x(),
                    self.crop_start_point.y(),
                    0, 0,
                    QPen(Qt.GlobalColor.black, 7, Qt.PenStyle.DashLine)
                )
            elif self.crop_type == CropType.CIRCLE:
                self.crop_item = self.addEllipse(
                    self.crop_start_point.x(),
                    self.crop_start_point.y(),
                    0, 0,
                    QPen(Qt.GlobalColor.black, 7, Qt.PenStyle.DashLine)
                )
            self.crop_item.setZValue(999998)
            self.crop_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            self.crop_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.crop_item:
            end_point = event.scenePos()
            start_point = self.crop_start_point
            startx = min(start_point.x(), end_point.x())
            starty = min(start_point.y(), end_point.y())
            if self.crop_type == CropType.CIRCLE:
                self.crop_item.setRect(
                    start_point.x(),
                    start_point.y(),
                    end_point.x() - start_point.x(),
                    end_point.x() - start_point.x()
                )
            elif self.crop_type == CropType.RECTANGLE:
                self.crop_item.setRect(
                    startx,
                    starty,
                    abs(end_point.x() - start_point.x()),
                    abs(end_point.y() - start_point.y())
                )
            elif self.crop_type == CropType.SQUARE:
                self.crop_item.setRect(
                    startx,
                    starty,
                    abs(end_point.x() - start_point.x()),
                    abs(end_point.x() - start_point.x())
                )
        return super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for item in self.selectedItems():
                self.removeItem(item)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.DropAction.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.add_image(file_path)
            event.accept()
        else:
            event.ignore()

    def duplicate_item(self):
        if len(self.selectedItems()) == 1:
            i = self.selectedItems()[0]
            if isinstance(i, QGraphicsSimpleTextItem):
                item = self.add_text_item(i)
            else:
                item = self.add_image(i)
            self.clearSelection()
            return item

    def add_image(self, file_path):
        if isinstance(file_path, QGraphicsPixmapItem):
            item = QGraphicsPixmapItem(file_path.pixmap())
            item.setTransform(file_path.sceneTransform())
        else:
            px = QPixmap(file_path)
            # px = px.scaled(self.scene.sceneRect().size().toSize() * 0.8, Qt.AspectRatioMode.KeepAspectRatio)
            item = QGraphicsPixmapItem(px)

        self.addItem(item)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not self.crop_mode)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)
        item.setTransformOriginPoint(item.sceneBoundingRect().center())
        return item

    def add_text_item(self, text_item=None):
        item = QGraphicsSimpleTextItem()
        item.setText("new text")
        font = item.font()
        font.setPointSize(100)
        if text_item:
            item.setText(text_item.text())
            font = text_item.font()
        item.setFont(font)
        self.addItem(item)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not self.crop_mode)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)
        item.setTransformOriginPoint(item.sceneBoundingRect().center())
        return item

    def toggle_util_items(self):
        self.clearSelection()
        if self.show_rulers and self.ruler_items.isVisible():
            self.ruler_items.hide()
        elif self.show_rulers and not self.ruler_items.isVisible():
            self.ruler_items.show()
        self.page_rect_border_item.setVisible(not self.page_rect_border_item.isVisible())
