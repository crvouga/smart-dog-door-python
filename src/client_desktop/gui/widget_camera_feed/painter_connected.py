from PySide6.QtWidgets import QLabel  # type: ignore
from PySide6.QtGui import QImage, QPixmap, QPainter  # type: ignore
from PySide6.QtCore import Qt  # type: ignore
from src.image_classifier.classification import Classification
from typing import List
from .painter_classifications import PainterClassifications


class PainterConnected:
    _feed_label: QLabel
    _classifications: List[Classification]

    def __init__(self, feed_label: QLabel):
        self._feed_label = feed_label
        self._classifications = []

    def draw(self, q_image: QImage) -> None:
        original_pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = original_pixmap.scaled(
            self._feed_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        orig_w = original_pixmap.width()
        orig_h = original_pixmap.height()
        scaled_w = scaled_pixmap.width()
        scaled_h = scaled_pixmap.height()

        if orig_w <= 0 or orig_h <= 0 or scaled_w <= 0 or scaled_h <= 0:
            self._feed_label.setPixmap(scaled_pixmap)
            return

        scale_x = scaled_w / orig_w
        scale_y = scaled_h / orig_h

        painter = QPainter(scaled_pixmap)
        painter_classification = PainterClassifications(painter)

        for classification in self._classifications:
            painter_classification.draw(classification, scale_x, scale_y)

        painter.end()
        self._feed_label.setPixmap(scaled_pixmap)

    def set_classifications(self, classifications: List[Classification]) -> None:
        self._classifications = classifications
