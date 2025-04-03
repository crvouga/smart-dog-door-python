from abc import ABC, abstractmethod
from src.image.image import Image
from src.library.pub_sub import Sub
from .event import EventCamera


class DeviceCamera(ABC):
    @abstractmethod
    def capture(self) -> list[Image]:
        pass

    @abstractmethod
    def events(self) -> Sub[EventCamera]:
        pass
