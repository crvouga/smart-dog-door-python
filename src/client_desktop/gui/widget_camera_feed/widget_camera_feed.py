from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject  # type: ignore
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor  # type: ignore
from src.device_camera.interface import DeviceCamera
from src.image_classifier.classification import Classification
from typing import List
from .painter_classification import PainterClassification
from .object_camera_worker import ObjectCameraWorker


class WidgetCameraFeed(QWidget):
    _device_camera: DeviceCamera
    _feed_label: QLabel
    _worker: ObjectCameraWorker
    _thread: QThread
    _classifications: List[Classification]
    _is_connected: bool

    def __init__(
        self,
        device_camera: DeviceCamera,
        x: int,
        y: int,
        width: int,
        height: int,
        fps: int,
    ):
        super().__init__()
        self._device_camera = device_camera
        self._classifications = []
        self._is_connected = True
        self._setup_geometry(x=x, y=y, width=width, height=height)
        self._setup_layout()
        self._setup_camera_worker(fps=fps)

    def _setup_geometry(self, x: int, y: int, width: int, height: int) -> None:
        self.setGeometry(x, y, width, height)

    def _setup_layout(self) -> None:
        layout = QVBoxLayout()
        self.setLayout(layout)

        self._feed_label = QLabel()
        self._feed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._feed_label)

    def _setup_camera_worker(self, fps: int) -> None:
        self._thread = QThread()
        self._worker = ObjectCameraWorker(self._device_camera, fps)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.process)
        self._worker.image_ready.connect(self._update_feed)
        self._thread.start()

    def _update_feed(self, q_image: QImage):
        if not self._is_connected:
            self._show_disconnected_ui()
            return

        original_pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = original_pixmap.scaled(
            self._feed_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
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
        painter_classification = PainterClassification(painter)

        for classification in self._classifications:
            painter_classification.draw(classification, scale_x, scale_y)

        painter.end()
        self._feed_label.setPixmap(scaled_pixmap)

    def _show_disconnected_ui(self) -> None:
        # Create a red background with "Camera Disconnected" text
        pixmap = QPixmap(self._feed_label.size())
        pixmap.fill(QColor(255, 0, 0, 50))  # Semi-transparent red

        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self._feed_label.font())

        text = "Camera Disconnected"
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()

        x = (pixmap.width() - text_width) // 2
        y = (pixmap.height() + text_height) // 2

        painter.drawText(x, y, text)
        painter.end()

        self._feed_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, event):
        self._worker.stop()
        self._thread.quit()
        self._thread.wait()
        super().closeEvent(event)

    def set_classifications(self, classifications: List[Classification]) -> None:
        self._classifications = classifications

    def set_is_connected(self, is_connected: bool) -> None:
        self._is_connected = is_connected
        if not is_connected:
            self._show_disconnected_ui()
