from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject  # type: ignore
from PySide6.QtGui import QImage, QPixmap  # type: ignore
from src.device_camera.interface import DeviceCamera


class CameraWorker(QObject):
    image_ready = Signal(QImage)

    def __init__(self, device_camera: DeviceCamera, fps: int):
        super().__init__()
        self._device_camera = device_camera
        self._running = True
        self._timer = QTimer()
        self._timer.timeout.connect(self._capture_frame)
        interval = int(1000 / fps)  # Convert fps to milliseconds
        self._timer.start(interval)

    def _capture_frame(self):
        if not self._running:
            return
        image = self._device_camera.capture()
        if image:
            image = image[0]
            image = image.np_array
            height, width, _ = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                image.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            self.image_ready.emit(q_image)

    def process(self):
        pass  # Timer handles the frame capture

    def stop(self):
        self._running = False
        self._timer.stop()


class CameraFeedWidget(QWidget):
    _device_camera: DeviceCamera
    _feed_label: QLabel
    _worker: CameraWorker
    _thread: QThread

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
        self.setGeometry(x, y, width, height)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self._feed_label = QLabel()
        self._feed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._feed_label)

        self._thread = QThread()
        self._worker = CameraWorker(device_camera, fps)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.process)
        self._worker.image_ready.connect(self._update_feed)
        self._thread.start()

    def _update_feed(self, q_image: QImage):
        """Update the camera feed display with the latest frame."""
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self._feed_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._feed_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Handle widget resize to maintain aspect ratio."""
        super().resizeEvent(event)

    def closeEvent(self, event):
        """Clean up thread when widget is closed."""
        self._worker.stop()
        self._thread.quit()
        self._thread.wait()
        super().closeEvent(event)
