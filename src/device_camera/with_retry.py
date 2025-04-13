import threading
import time
from typing import TypeVar, Generic, Type, Union
from src.device_camera.interface import DeviceCamera
from src.image.image import Image
from src.library.pub_sub import PubSub, Sub
from .event import EventCamera, EventCameraConnected, EventCameraDisconnected
from logging import Logger

T = TypeVar("T", bound=DeviceCamera)


class WithRetry(DeviceCamera, Generic[T]):
    _logger: Logger
    _wrapped: T
    _running: bool
    _lock: threading.Lock
    _connected: bool
    _capture_thread: threading.Thread
    _retry_interval: float = 5.0  # seconds between retries

    def __init__(self, wrapped: T, logger: Logger):
        self._logger = logger.getChild("with_retry")
        self._wrapped = wrapped
        self._running = False
        self._lock = threading.Lock()
        self._connected = False
        self._capture_thread = None  # type: ignore

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
            self._capture_thread = None  # type: ignore

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _capture_loop(self) -> None:
        while self._running:
            try:
                if not self._wrapped.is_connected():
                    if self._wrapped._attempt_connection():
                        self._logger.info("Successfully connected to camera.")
                        with self._lock:
                            self._connected = True
                            # Get the events object and publish to it
                            events_sub = self._wrapped.events()
                            if isinstance(events_sub, PubSub):
                                events_sub.publish(EventCameraConnected())
                            else:
                                self._logger.error(
                                    "Events object is not a PubSub instance"
                                )
                    else:
                        self._logger.warning(
                            "Failed to connect to camera, will retry..."
                        )
                        time.sleep(self._retry_interval)
                        continue

                # Check if _process_frames method exists on the wrapped object
                if hasattr(self._wrapped, "_process_frames"):
                    self._wrapped._process_frames()
                else:
                    self._logger.warning(
                        "Wrapped camera does not have _process_frames method"
                    )
                    time.sleep(self._retry_interval)

            except Exception as e:
                self._logger.error(f"Error in capture loop: {e}")
                self._wrapped._handle_connection_failure()
                time.sleep(self._retry_interval)

    def capture(self) -> list[Image]:
        return self._wrapped.capture()

    def events(self) -> Sub[EventCamera]:
        return self._wrapped.events()

    def _attempt_connection(self) -> bool:
        return self._wrapped._attempt_connection()

    def _handle_connection_failure(self) -> None:
        with self._lock:
            self._connected = False
        self._wrapped._handle_connection_failure()

    def _process_frames(self) -> None:
        # Check if _process_frames method exists on the wrapped object
        if hasattr(self._wrapped, "_process_frames"):
            self._wrapped._process_frames()
        else:
            self._logger.warning("Wrapped camera does not have _process_frames method")
