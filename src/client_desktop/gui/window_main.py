from PySide6.QtWidgets import (  # type: ignore
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QPalette, QColor  # type: ignore
from .widget_camera_feed.widget_camera_feed import WidgetCameraFeed
from .widget_door_status.widget_door_status import WidgetDoorStatus
from src.device_camera.interface import DeviceCamera
from src.smart_door.smart_door import SmartDoor
from src.smart_door.core.model import (
    Model,
    is_camera_connected,
    to_latest_classifications,
)

ASPECT_RATIO_H_W = 9 / 16
MIN_WIDTH = 500
MIN_HEIGHT = int(MIN_WIDTH * ASPECT_RATIO_H_W)


class WindowMain(QMainWindow):
    _device_camera: DeviceCamera
    _smart_door: SmartDoor
    _layout_main: QVBoxLayout
    _widget_camera_feed: WidgetCameraFeed
    _widget_door_status: WidgetDoorStatus

    def __init__(self, device_camera: DeviceCamera, smart_door: SmartDoor):
        super().__init__()
        self._device_camera = device_camera
        self._smart_door = smart_door
        self._setup_window()
        self._setup_window_background()
        self._setup_layout_main()
        self._setup_widget_camera_feed()
        self._setup_widget_door_status()

    def _setup_window(self) -> None:
        self.setWindowTitle("Smart Dog Door")
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)

    def _setup_window_background(self) -> None:
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def _setup_layout_main(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_main = QVBoxLayout(central_widget)
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.setSpacing(0)
        self._layout_main = layout_main

    def _setup_widget_camera_feed(self) -> None:
        self._widget_camera_feed = WidgetCameraFeed(
            device_camera=self._device_camera,
            height=self.height(),
            width=self.width(),
            x=0,
            y=0,
            fps=60,
        )
        self._layout_main.addWidget(self._widget_camera_feed, stretch=1)

        def _set_classifications(model: Model):
            self._widget_camera_feed.set_classifications(
                classifications=to_latest_classifications(model)
            )

        self._smart_door.models.subscribe(_set_classifications)

        def _set_is_connected(model: Model):
            self._widget_camera_feed.set_is_connected(is_camera_connected(model))

        self._smart_door.models.subscribe(_set_is_connected)

    def _setup_widget_door_status(self) -> None:
        self._widget_door_status = WidgetDoorStatus()
        self._layout_main.addWidget(self._widget_door_status)

        def _update_door_status(model: Model):
            self._widget_door_status.update_status(model)

        self._smart_door.models.subscribe(_update_door_status)
