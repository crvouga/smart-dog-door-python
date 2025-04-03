from .interface import DeviceDoor
from .event import EventDoor
from src.library.pub_sub import PubSub, Sub


class FakeDeviceDoor(DeviceDoor):
    _is_open: bool

    def __init__(self):
        self._is_open = False

    def open(self) -> None:
        self._is_open = True

    def close(self) -> None:
        self._is_open = False

    def events(self) -> Sub[EventDoor]:
        pub_sub = PubSub()

        return pub_sub
