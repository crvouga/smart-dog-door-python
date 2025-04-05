import pprint
from PySide6.QtWidgets import (  # type: ignore
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QPalette, QColor  # type: ignore
from .camera_feed_widget import CameraFeedWidget
from src.device_camera.interface import DeviceCamera
from src.smart_door.smart_door import SmartDoor
from src.smart_door.core.model import Model


class MainWindow(QMainWindow):
    _device_camera: DeviceCamera
    _smart_door: SmartDoor
    _main_layout: QVBoxLayout
    _camera_feed: CameraFeedWidget
    _model_label: QLabel

    def __init__(self, device_camera: DeviceCamera, smart_door: SmartDoor):
        super().__init__()
        self._device_camera = device_camera
        self._smart_door = smart_door
        self._setup_window()
        self._setup_background()
        self._setup_layout()
        self._setup_camera_feed()
        self._setup_model()

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
        self._camera_feed = CameraFeedWidget(
            device_camera=self._device_camera,
            height=self.height(),
            width=self.width(),
            x=0,
            y=0,
            fps=30,
        )
        self._main_layout.addWidget(self._camera_feed)

    def _setup_model(self) -> None:
        self._model_label = QLabel("Model")
        self._model_label.setStyleSheet("color: white; font-size: 16px;")
        self._model_label.setAlignment(Qt.AlignLeft)
        self._main_layout.addWidget(self._model_label)
        self._smart_door.models().sub(lambda model: self._update_model(model))

    def _update_model(self, model: Model) -> None:
        self._model_label.setText(pprint.pformat(model.__dict__, indent=2, width=80))
