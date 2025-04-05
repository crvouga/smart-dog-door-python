from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore
from PySide6.QtCore import Qt, QTimer  # type: ignore
from PySide6.QtGui import QImage, QPixmap  # type: ignore
from src.device_camera.interface import DeviceCamera


class CameraFeedWidget(QWidget):
    def __init__(
        self,
        device_camera: DeviceCamera,
        x: int = 0,
        y: int = 0,
        width: int = 640,
        height: int = 480,
    ):
        super().__init__()
        self._device_camera = device_camera
        self.setGeometry(x, y, width, height)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self._feed_label = QLabel()
        self._feed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._feed_label)

        self._timer = QTimer()
        self._timer.timeout.connect(self._update_feed)
        self._timer.start(30)

    def _update_feed(self):
        """Update the camera feed display with the latest frame."""
        frame = self._device_camera.get_frame()
        if frame is not None:

            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            )

            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self._feed_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._feed_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Handle widget resize to maintain aspect ratio."""
        super().resizeEvent(event)
        self._update_feed()
