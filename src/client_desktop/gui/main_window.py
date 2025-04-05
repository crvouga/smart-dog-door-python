from PySide6.QtWidgets import (  # type: ignore
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt  # type: ignore
from .camera_feed_widget import CameraFeedWidget
from src.device_camera.interface import DeviceCamera


class MainWindow(QMainWindow):
    def __init__(self, device_camera: DeviceCamera):
        super().__init__()

        self.setWindowTitle("Image Classifier")
        ASPECT_RATIO_H_W = 9 / 16
        WIDTH = 1000
        HEIGHT = WIDTH * ASPECT_RATIO_H_W
        self.setMinimumSize(WIDTH, HEIGHT)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.camera_feed = CameraFeedWidget(
            device_camera=device_camera, height=HEIGHT, width=WIDTH, x=0, y=0
        )
        main_layout.addWidget(self.camera_feed)
