from abc import ABC, abstractmethod
from src.library.pub_sub import Sub
from .event import EventDoor


class DeviceDoor(ABC):
    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def events(self) -> Sub[EventDoor]:
        pass
