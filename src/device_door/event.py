from dataclasses import dataclass
from typing import Literal, Union


@dataclass
class EventDoorConnected:
    type: Literal["connected"] = "connected"


@dataclass
class EventDoorDisconnected:
    type: Literal["disconnected"] = "disconnected"


@dataclass
class EventDoorOpened:
    type: Literal["opened"] = "opened"


@dataclass
class EventDoorClosed:
    type: Literal["closed"] = "closed"


EventDoor = Union[
    EventDoorConnected, EventDoorDisconnected, EventDoorOpened, EventDoorClosed
]
