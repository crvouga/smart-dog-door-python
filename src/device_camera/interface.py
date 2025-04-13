from abc import ABC, abstractmethod
from src.image.image import Image
from src.library.life_cycle import LifeCycle
from src.library.pub_sub import Sub
from .event import EventCamera


class DeviceCamera(LifeCycle, ABC):
    @abstractmethod
    def capture(self) -> list[Image]:
        """Capture the latest frame(s) from the camera."""
        pass

    @abstractmethod
    def events(self) -> Sub[EventCamera]:
        """Get the event subscriber for camera events."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the camera is currently connected."""
        pass

    @abstractmethod
    def _attempt_connection(self) -> bool:
        """
        Attempt to establish a connection to the camera.
        Returns True if connection was successful, False otherwise.
        """
        pass

    @abstractmethod
    def _handle_connection_failure(self) -> None:
        """
        Handle a connection failure, including cleanup and state management.
        This should be called when a connection attempt fails or when the connection is lost.
        """
        pass
