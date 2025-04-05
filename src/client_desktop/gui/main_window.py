from PySide6.QtWidgets import (  # type: ignore
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QPalette, QColor  # type: ignore
from .camera_feed_widget import CameraFeedWidget
from src.device_camera.interface import DeviceCamera


class MainWindow(QMainWindow):
    def __init__(self, device_camera: DeviceCamera):
        super().__init__()
        self._device_camera = device_camera
        self._setup_window()
        self._setup_background()
        self._setup_layout()
        self._setup_camera_feed()

    def _setup_window(self) -> None:
        self.setWindowTitle("Image Classifier")
        ASPECT_RATIO_H_W = 9 / 16
        WIDTH = 1000
        HEIGHT = WIDTH * ASPECT_RATIO_H_W
        self.setMinimumSize(WIDTH, HEIGHT)

    def _setup_background(self) -> None:
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def _setup_layout(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self._main_layout = main_layout

    def _setup_camera_feed(self) -> None:
        self.camera_feed = CameraFeedWidget(
            device_camera=self._device_camera,
            height=self.height(),
            width=self.width(),
            x=0,
            y=0,
            fps=30,
        )
        self._main_layout.addWidget(self.camera_feed)
