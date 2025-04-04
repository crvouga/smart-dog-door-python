from src.image.image import Image
from .interface import DeviceCamera
from .event import EventCamera
from src.library.pub_sub import PubSub, Sub


class FakeDeviceCamera(DeviceCamera):

    def __init__(self):
        pass

    def capture(self) -> list[Image]:
        return []

    def events(self) -> Sub[EventCamera]:
        pub_sub = PubSub[EventCamera]()

        return pub_sub

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
