from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Union
from src.library.pub_sub import Sub


@dataclass
class DoorOpenedEvent:
    type: Literal["opened"]


@dataclass
class DoorClosedEvent:
    type: Literal["closed"]


DoorEvent = Union[DoorOpenedEvent, DoorClosedEvent]


class DeviceDoor(ABC):
    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def events(self) -> Sub[DoorEvent]:
        pass
