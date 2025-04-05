from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject  # type: ignore
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor  # type: ignore
from src.device_camera.interface import DeviceCamera
from src.image_classifier.classification import Classification
from typing import List


class CameraWorker(QObject):
    image_ready = Signal(QImage)

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

        if not image:
            return

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
        self._thread.start()

    def _update_feed(self, q_image: QImage):
        """Update the camera feed display with the latest frame and draw bounding boxes."""
        original_pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = original_pixmap.scaled(
            self._feed_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Get original and scaled dimensions
        orig_w = original_pixmap.width()
        orig_h = original_pixmap.height()
        scaled_w = scaled_pixmap.width()
        scaled_h = scaled_pixmap.height()

        if orig_w <= 0 or orig_h <= 0 or scaled_w <= 0 or scaled_h <= 0:
            self._feed_label.setPixmap(
                scaled_pixmap
            )  # Show image even if we can't draw boxes
            return

        # Calculate scaling factors
        scale_x = scaled_w / orig_w
        scale_y = scaled_h / orig_h

        # Create a painter to draw on the scaled pixmap
        painter = QPainter(scaled_pixmap)
        pen = QPen(QColor(255, 0, 0))  # Red color for bounding boxes
        pen.setWidth(2)
        painter.setPen(pen)

        for classification in self._classifications:
            bbox = classification.bounding_box

            # Apply scaling to the absolute coordinates from the classification
            rect_x = int(bbox.x_min * scale_x)
            rect_y = int(bbox.y_min * scale_y)
            rect_w = int((bbox.x_max - bbox.x_min) * scale_x)
            rect_h = int((bbox.y_max - bbox.y_min) * scale_y)

            if rect_w > 0 and rect_h > 0:
                painter.drawRect(rect_x, rect_y, rect_w, rect_h)

                # Draw the label and confidence
                label_text = f"{classification.label} ({classification.weight:.2f})"
                # Adjust text position slightly for visibility
                text_x = rect_x
                text_y = (
                    rect_y - 5 if rect_y > 10 else rect_y + 15
                )  # Avoid drawing off-screen
                painter.drawText(text_x, text_y, label_text)

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

    def set_classifications(self, classifications: List[Classification]) -> None:
        """
        Updates the classifications to be drawn on the next frame update.
        This method should be called by the owner/consumer of this widget.
        """
        self._classifications = classifications
