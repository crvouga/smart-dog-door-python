from dataclasses import dataclass
from typing import Literal, Union


@dataclass
class EventCameraConnected:
    type: Literal["connected"] = "connected"


@dataclass
class EventCameraDisconnected:
    type: Literal["disconnected"] = "disconnected"


EventCamera = Union[EventCameraConnected, EventCameraDisconnected]
