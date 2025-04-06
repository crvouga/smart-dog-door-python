from logging import Logger
import time
from datetime import timedelta
from .interface import DeviceDoor
from .event import EventDoor, EventDoorConnected, EventDoorDisconnected
from src.library.pub_sub import PubSub, Sub


class FakeDeviceDoor(DeviceDoor):
    _is_open: bool

    def __init__(
        self,
        logger: Logger,
        latency_start: timedelta = timedelta(seconds=0.2),
        latency_stop: timedelta = timedelta(seconds=0.2),
    ):
        self._is_open = False
        self._logger = logger.getChild("fake_device_door")
        self._latency_start = latency_start
        self._latency_stop = latency_stop

    def open(self) -> None:
        self._is_open = True

    def close(self) -> None:
        self._is_open = False

    def events(self) -> Sub[EventDoor]:
        pub_sub = PubSub[EventDoor]()

        pub_sub.pub(EventDoorConnected())

        return pub_sub

    def start(self) -> None:
        self._logger.info("Starting")
        time.sleep(self._latency_start.total_seconds())
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        time.sleep(self._latency_stop.total_seconds())
        self._logger.info("Stopped")
