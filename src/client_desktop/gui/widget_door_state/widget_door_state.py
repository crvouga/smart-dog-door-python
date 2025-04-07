from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QPalette, QColor  # type: ignore
from src.smart_door.core.model import DoorState, Model, ModelReady
from typing import Optional


class WidgetDoorState(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._label = QLabel("Door State: Unknown")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("color: white;")
        self._layout.addWidget(self._label)

    def update_state(self, model: Model) -> None:
        if not isinstance(model, ModelReady):
            self._label.setText("Door State: Unknown")
            return

        state_text = f"Door State: {model.door.state.name}"
        self._label.setText(state_text)
