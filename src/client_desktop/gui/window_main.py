from PySide6.QtWidgets import (  # type: ignore
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QPalette, QColor  # type: ignore
from .widget_camera_feed.widget_camera_feed import WidgetCameraFeed
from .widget_door_state.widget_door_state import WidgetDoorState
from src.device_camera.interface import DeviceCamera
from src.smart_door.smart_door import SmartDoor
from src.smart_door.core.model import Model, ModelReady, is_camera_connected

ASPECT_RATIO_H_W = 9 / 16
WIDTH = 1000
HEIGHT = WIDTH * ASPECT_RATIO_H_W


class WindowMain(QMainWindow):
    _device_camera: DeviceCamera
    _smart_door: SmartDoor
    _layout_main: QVBoxLayout
    _widget_camera_feed: WidgetCameraFeed
    _widget_door_state: WidgetDoorState

    def __init__(self, device_camera: DeviceCamera, smart_door: SmartDoor):
        super().__init__()
        self._device_camera = device_camera
        self._smart_door = smart_door
        self._setup_window()
        self._setup_background()
        self._setup_layout()
        self._setup_camera_feed()
        self._setup_door_state()

    def _setup_window(self) -> None:
        self.setWindowTitle("Image Classifier")

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
        self._layout_main = main_layout

    def _setup_camera_feed(self) -> None:
        self._widget_camera_feed = WidgetCameraFeed(
            device_camera=self._device_camera,
            height=self.height(),
            width=self.width(),
            x=0,
            y=0,
            fps=60,
        )
        self._layout_main.addWidget(self._widget_camera_feed)

        def _set_classifications(model: Model):
            if not isinstance(model, ModelReady):
                return

            self._widget_camera_feed.set_classifications(
                classifications=model.camera.latest_classification
            )

        self._smart_door.models().sub(_set_classifications)

        def _set_is_connected(model: Model):
            self._widget_camera_feed.set_is_connected(is_camera_connected(model))

        self._smart_door.models().sub(_set_is_connected)

    def _setup_door_state(self) -> None:
        self._widget_door_state = WidgetDoorState()
        self._layout_main.addWidget(self._widget_door_state)

        def _update_door_state(model: Model):
            self._widget_door_state.update_state(model)

        self._smart_door.models().sub(_update_door_state)
