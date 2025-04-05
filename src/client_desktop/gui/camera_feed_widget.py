from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject  # type: ignore
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor  # type: ignore
from src.device_camera.interface import DeviceCamera
from src.image_classifier.classification import Classification
from typing import List


class CameraWorker(QObject):
    image_ready = Signal(QImage)
    classifications_ready = Signal(List[Classification])

    def __init__(self, device_camera: DeviceCamera, fps: int):
        super().__init__()
        self._device_camera = device_camera
        self._running = True
        self._timer = QTimer()
        self._timer.timeout.connect(self._capture_frame)
        interval = int(1000 / fps)
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
        pass

    def stop(self):
        self._running = False
        self._timer.stop()


class CameraFeedWidget(QWidget):
    _device_camera: DeviceCamera
    _feed_label: QLabel
    _worker: CameraWorker
    _thread: QThread
    _classifications: List[Classification]

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
        self._worker = CameraWorker(self._device_camera, fps)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.process)
        self._worker.image_ready.connect(self._update_feed)
        self._worker.classifications_ready.connect(self._update_classifications)
        self._thread.start()

    def _update_classifications(self, classifications: List[Classification]) -> None:
        """Update the stored classifications."""
        self._classifications = classifications

    def _update_feed(self, q_image: QImage):
        """Update the camera feed display with the latest frame and draw bounding boxes."""
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self._feed_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Create a painter to draw on the pixmap
        painter = QPainter(scaled_pixmap)
        pen = QPen(QColor(255, 0, 0))  # Red color for bounding boxes
        pen.setWidth(2)
        painter.setPen(pen)

        for classification in self._classifications:
            bbox = classification.bounding_box
            x_min = bbox.x_min * scaled_pixmap.width()
            y_min = bbox.y_min * scaled_pixmap.height()
            x_max = bbox.x_max * scaled_pixmap.width()
            y_max = bbox.y_max * scaled_pixmap.height()

            painter.drawRect(
                int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)
            )

            # Draw the label and confidence
            label_text = f"{classification.label} ({classification.weight:.2f})"
            painter.drawText(int(x_min), int(y_min) - 5, label_text)

        painter.end()
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
