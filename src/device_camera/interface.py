from abc import ABC, abstractmethod
from src.image.image import Image
from src.library.life_cycle import LifeCycle
from src.library.pub_sub import Sub
from .event import EventCamera


class DeviceCamera(LifeCycle, ABC):
    @abstractmethod
    def capture(self) -> list[Image]:
        pass

    @abstractmethod
    def events(self) -> Sub[EventCamera]:
        pass
