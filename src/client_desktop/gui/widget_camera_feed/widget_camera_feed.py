from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore
from PySide6.QtCore import Qt, QThread  # type: ignore
from PySide6.QtGui import QImage  # type: ignore
from src.device_camera.interface import DeviceCamera
from src.image_classifier.classification import Classification
from typing import List
from .painter_disconnected import PainterDisconnected
from .painter_connected import PainterConnected
from .object_camera_worker import ObjectCameraWorker


class WidgetCameraFeed(QWidget):
    _device_camera: DeviceCamera
    _feed_label: QLabel
    _worker: ObjectCameraWorker
    _thread: QThread
    _is_connected: bool
    _painter_disconnected: PainterDisconnected
    _painter_connected: PainterConnected

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
        self._painter_disconnected = PainterDisconnected(self._feed_label)
        self._painter_connected = PainterConnected(self._feed_label)

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

        self._painter_connected.draw(q_image)

    def _show_disconnected_ui(self) -> None:
        self._painter_disconnected.draw()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, event):
        self._worker.stop()
        self._thread.quit()
        self._thread.wait()
        super().closeEvent(event)

    def set_classifications(self, classifications: List[Classification]) -> None:
        self._painter_connected.set_classifications(classifications)

    def set_is_connected(self, is_connected: bool) -> None:
        self._is_connected = is_connected
        if not is_connected:
            self._show_disconnected_ui()
