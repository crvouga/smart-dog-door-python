from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal
from library.pub_sub import Sub


@dataclass
class DoorOpenedEvent:
    type: Literal["opened"]


@dataclass
class DoorClosedEvent:
    type: Literal["closed"]


DoorEvent = DoorOpenedEvent | DoorClosedEvent


class DeviceDoor(ABC):
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def events(self) -> Sub[DoorEvent]:
        pass
