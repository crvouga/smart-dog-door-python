from dataclasses import dataclass
from typing import Literal, Union


@dataclass
class EventDoorConnected:
    type: Literal["connected"] = "connected"


@dataclass
class EventDoorDisconnected:
    type: Literal["disconnected"] = "disconnected"


EventDoor = Union[EventDoorConnected, EventDoorDisconnected]
