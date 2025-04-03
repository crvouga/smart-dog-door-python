from abc import ABC, abstractmethod
from src.image.image import Image


class DeviceCamera(ABC):
    @abstractmethod
    def capture(self) -> list[Image]:
        pass
