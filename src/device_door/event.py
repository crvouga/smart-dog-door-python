from dataclasses import dataclass
from typing import Literal, Union


@dataclass
class EventDoorConnected:
    type: Literal["connected"]


@dataclass
class EventDoorDisconnected:
    type: Literal["disconnected"]


EventDeviceDoor = Union[EventDoorConnected, EventDoorDisconnected]
