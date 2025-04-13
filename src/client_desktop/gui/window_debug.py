from dataclasses import asdict
from datetime import datetime
import pprint
from typing import Any
from PySide6.QtWidgets import (  # type: ignore
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QPalette, QColor  # type: ignore
from src.library.dict_ext import recursive_map
from src.smart_door.core.msg import Msg
from src.smart_door.smart_door import SmartDoor
from src.smart_door.core.model import Model


class WindowDebug(QMainWindow):
    _smart_door: SmartDoor
    _main_layout: QVBoxLayout
    _model_label: QLabel
    _msgs_label: QLabel

    def __init__(self, smart_door: SmartDoor):
        super().__init__()
        self._smart_door = smart_door
        self._setup_window()
        self._setup_background()
        self._setup_layout()
        self._setup_msgs_label()
        self._setup_model_label()

    def _setup_window(self) -> None:
        self.setWindowTitle("Debug Window")
        WIDTH = 800
        HEIGHT = 600
        self.setMinimumSize(0, 0)
        self.resize(WIDTH, HEIGHT)

    def _setup_background(self) -> None:
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def _setup_layout(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self._main_layout = main_layout

    def _setup_model_label(self) -> None:
        self._model_label = QLabel("Model")
        self._model_label.setStyleSheet(
            "color: white; font-size: 14px; font-family: 'Courier New', monospace;"
        )
        self._model_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addWidget(self._model_label)

        def _set_model_label(model: Model):
            self._model_label.setText(format_obj(model))

        self._smart_door.models.subscribe(_set_model_label)

    def _setup_msgs_label(self):
        self._msgs_label = QLabel("Msg")
        self._msgs_label.setStyleSheet(
            "color: white; font-size: 14px; font-family: 'Courier New', monospace;"
        )
        self._msgs_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addWidget(self._msgs_label)

        def _set_msgs_label(msg: Msg):
            self._msgs_label.setText(format_obj(msg))

        self._smart_door.msgs.subscribe(_set_msgs_label)


def format_obj(obj: Any) -> str:
    return pprint.pformat(obj_to_dict(obj), indent=2, width=80, sort_dicts=True)


def obj_to_dict(obj: Any) -> Any:
    dataclass_dict = asdict(obj)
    mapped = recursive_map(dataclass_dict, _map_value)
    return mapped


def _map_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %I:%M:%S %p MST")
    return value
