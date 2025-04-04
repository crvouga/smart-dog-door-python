from logging import Logger
from src.assets import assets_dir
from src.image.image import Image
from .interface import DeviceCamera
from .event import EventCamera, EventCameraConnected
from src.library.pub_sub import PubSub, Sub
from itertools import cycle
import time
from datetime import timedelta

IMAGES = [
    Image.from_file(assets_dir("images/empty_security_footage/1.jpeg")),
    Image.from_file(assets_dir("images/empty_security_footage/2.jpeg")),
    Image.from_file(assets_dir("images/empty_security_footage/3.jpeg")),
    #
    Image.from_file(assets_dir("images/dog_security_footage/1.jpeg")),
    Image.from_file(assets_dir("images/dog_security_footage/2.jpeg")),
    Image.from_file(assets_dir("images/dog_security_footage/3.jpeg")),
    #
    Image.from_file(assets_dir("images/cat_security_footage/1.jpeg")),
    Image.from_file(assets_dir("images/cat_security_footage/2.jpeg")),
    Image.from_file(assets_dir("images/cat_security_footage/3.jpeg")),
]


image_cycle = cycle(IMAGES)


class FakeDeviceCamera(DeviceCamera):

    def __init__(
        self,
        logger: Logger,
        latency_capture: timedelta = timedelta(seconds=0.3),
        latency_start: timedelta = timedelta(seconds=0.3),
        latency_stop: timedelta = timedelta(seconds=0.3),
    ):
        self._latency_capture = latency_capture
        self._latency_start = latency_start
        self._latency_stop = latency_stop
        self._logger = logger.getChild("fake_device_camera")

    def capture(self) -> list[Image]:
        self._logger.debug("Capturing")

        time.sleep(self._latency_capture.total_seconds())

        image = next(image_cycle)

        self._logger.debug(f"Captured {image.filename}")

        return [image]

    def events(self) -> Sub[EventCamera]:
        pub_sub = PubSub[EventCamera]()

        pub_sub.pub(EventCameraConnected())

        return pub_sub

    def start(self) -> None:
        self._logger.info("Starting")
        time.sleep(self._latency_start.total_seconds())
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        time.sleep(self._latency_stop.total_seconds())
        self._logger.info("Stopped")
