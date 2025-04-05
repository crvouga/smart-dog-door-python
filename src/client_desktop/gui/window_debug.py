from dataclasses import asdict
import pprint
from PySide6.QtWidgets import (  # type: ignore
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QPalette, QColor  # type: ignore
from src.smart_door.smart_door import SmartDoor
from src.smart_door.core.model import Model


class WindowDebug(QMainWindow):
    _smart_door: SmartDoor
    _main_layout: QVBoxLayout
    _model_label: QLabel

    def __init__(self, smart_door: SmartDoor):
        super().__init__()
        self._smart_door = smart_door
        self._setup_window()
        self._setup_background()
        self._setup_layout()
        self._setup_model()

    def _setup_window(self) -> None:
        self.setWindowTitle("Debug Window")
        WIDTH = 800
        HEIGHT = 600
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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self._main_layout = main_layout

    def _setup_model(self) -> None:
        self._model_label = QLabel("Model State")
        self._model_label.setStyleSheet(
            "color: white; font-size: 14px; font-family: monospace;"
        )
        self._model_label.setAlignment(Qt.AlignLeft)
        self._main_layout.addWidget(self._model_label)

        def _set_model_label(model: Model):
            self._model_label.setText(pprint.pformat(asdict(model), indent=2, width=80))

        self._smart_door.models().sub(_set_model_label)
