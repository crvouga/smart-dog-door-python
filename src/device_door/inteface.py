from abc import ABC, abstractmethod
from src.library.pub_sub import Sub
from .event import EventDeviceDoor


class DeviceDoor(ABC):
    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def events(self) -> Sub[EventDeviceDoor]:
        pass
