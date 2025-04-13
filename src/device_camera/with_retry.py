import threading
import time
from typing import Optional, Callable
from src.device_camera.interface import DeviceCamera
from src.image.image import Image
from src.library.pub_sub import PubSub
from .event import EventCamera, EventCameraConnected
from logging import Logger


class WithRetry(DeviceCamera):
    _logger: Logger
    _wrapped: DeviceCamera
    _running: bool
    _lock: threading.Lock
    _connected: bool
    _capture_thread: Optional[threading.Thread]
    _retry_interval: float
    _time_sleep: Callable[[float], None]

    def __init__(
        self,
        wrapped: DeviceCamera,
        logger: Logger,
        retry_interval: float = 5.0,
        time_sleep: Callable[[float], None] = time.sleep,
    ):
        self._logger = logger.getChild("with_retry")
        self._wrapped = wrapped
        self._running = False
        self._lock = threading.Lock()
        self._connected = False
        self._capture_thread = None
        self._retry_interval = retry_interval
        self._time_sleep = time_sleep

    def start(self) -> None:
        self._logger.info("Starting camera with retry...")
        if self._running:
            self._logger.warning("Already running.")
            return

        self._running = True
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        self._logger.info("Capture thread started.")

    def stop(self) -> None:
        self._logger.info("Stopping camera with retry...")
        if not self._running:
            self._logger.warning("Already stopped.")
            return

        self._running = False
        if self._capture_thread:
            self._capture_thread.join(timeout=5.0)
            if self._capture_thread.is_alive():
                self._logger.warning("Capture thread did not exit cleanly.")
            self._capture_thread = None

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _capture_loop(self) -> None:
        while self._running:
            if not self._wrapped.is_connected():
                self._handle_disconnected_state()
                continue

            self._process_frames()

    def _handle_disconnected_state(self) -> None:
        if self._attempt_connection():
            self._logger.info("Successfully connected to camera.")
            self._mark_as_connected()
        else:
            self._logger.warning("Failed to connect to camera, will retry...")
            self._time_sleep(self._retry_interval)

    def _mark_as_connected(self) -> None:
        with self._lock:
            self._connected = True
            self._wrapped.events().publish(EventCameraConnected())

    def _process_frames(self) -> None:
        try:
            frames = self._wrapped.capture()
            if not frames:
                self._handle_connection_failure()
        except Exception as e:
            self._logger.error(f"Error processing frames: {e}")
            self._handle_connection_failure()
            self._time_sleep(self._retry_interval)

    def capture(self) -> list[Image]:
        return self._wrapped.capture()

    def events(self) -> PubSub[EventCamera]:
        return self._wrapped.events()

    def _attempt_connection(self) -> bool:
        return self._wrapped._attempt_connection()

    def _handle_connection_failure(self) -> None:
        with self._lock:
            self._connected = False
        self._wrapped._handle_connection_failure()
