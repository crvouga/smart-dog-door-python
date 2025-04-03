from dataclasses import dataclass
from typing import Literal, Union


@dataclass
class EventConnected:
    type: Literal["connected"]


@dataclass
class EventDisconnected:
    type: Literal["disconnected"]


EventDeviceCamera = Union[EventConnected, EventDisconnected]
