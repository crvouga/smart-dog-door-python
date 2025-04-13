from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore
from PySide6.QtCore import Qt  # type: ignore
from src.smart_door.core.door_status import to_door_status
from src.smart_door.core.model import Model
from typing import Optional
from typing_extensions import override


class WidgetDoorStatus(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._label = QLabel("Door State: Unknown")
        self._label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        self._label.setStyleSheet(
            """
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: Arial, sans-serif;
        """
        )
        self._layout.addWidget(self._label)

    def update_status(self, model: Model) -> None:
        now = datetime.now()
        door_status = to_door_status(model=model, now=now)
        self._label.setText(door_status)
