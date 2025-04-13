from logging import Logger
from typing import List, Optional, Callable
import threading
import time
from datetime import timedelta
from itertools import cycle
import numpy as np

from src.assets import assets_dir
from src.image.image import Image
from src.library.pub_sub import PubSub, Sub
from .interface import DeviceCamera
from .event import EventCamera, EventCameraConnected, EventCameraDisconnected

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


class FakeDeviceCamera(DeviceCamera):
    _logger: Logger
    _pub_sub: PubSub[EventCamera]
    _latest_frame: Optional[Image]
    _connected: bool
    _lock: threading.Lock
    _image_cycle: cycle
    _should_fail_connection: bool
    _should_fail_frames: bool
    _frame_generator: Optional[Callable[[], Image]]

    def __init__(
        self,
        logger: Logger,
        latency_capture: timedelta = timedelta(seconds=0.3),
        latency_start: timedelta = timedelta(seconds=0.3),
        latency_stop: timedelta = timedelta(seconds=0.3),
        should_fail_connection: bool = False,
        should_fail_frames: bool = False,
        frame_generator: Optional[Callable[[], Image]] = None,
    ):
        self._latency_capture = latency_capture
        self._latency_start = latency_start
        self._latency_stop = latency_stop
        self._logger = logger.getChild("fake_device_camera")
        self._pub_sub = PubSub[EventCamera]()
        self._latest_frame = None
        self._connected = False
        self._lock = threading.Lock()
        self._image_cycle = cycle(IMAGES)
        self._should_fail_connection = should_fail_connection
        self._should_fail_frames = should_fail_frames
        self._frame_generator = frame_generator

    def start(self) -> None:
        self._logger.info("Starting FakeDeviceCamera...")
        self._attempt_connection()

    def stop(self) -> None:
        self._logger.info("Stopping FakeDeviceCamera...")
        with self._lock:
            self._connected = False
            self._latest_frame = None

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _attempt_connection(self) -> bool:
        if self._should_fail_connection:
            self._logger.warning("Simulating connection failure")
            return False

        with self._lock:
            self._connected = True
            self._pub_sub.publish(EventCameraConnected())
            return True

    def _handle_connection_failure(self) -> None:
        with self._lock:
            if self._connected:
                self._connected = False
                self._pub_sub.publish(EventCameraDisconnected())
            self._latest_frame = None

    def _process_frames(self) -> None:
        if self._should_fail_frames:
            self._logger.warning("Simulating frame capture failure")
            self._handle_connection_failure()
            return

        if self._frame_generator:
            frame = self._frame_generator()
        else:
            frame = next(self._image_cycle)

        with self._lock:
            self._latest_frame = frame

    def capture(self) -> List[Image]:
        with self._lock:
            if self._latest_frame is None:
                return []
            return [self._latest_frame]

    def events(self) -> PubSub[EventCamera]:
        return self._pub_sub
