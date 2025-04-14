from src.device_camera.interface import DeviceCamera
from src.image.image import Image
from src.library.pub_sub import PubSub
from .event import EventCamera, EventCameraConnected
from logging import Logger
from itertools import cycle
import threading
import time
from typing import Iterator, Callable, Optional
from datetime import timedelta


class WithFallbacks(DeviceCamera):
    _logger: Logger
    _devices: Iterator[DeviceCamera]
    _current_device: DeviceCamera
    _lock: threading.Lock
    _connected: bool
    _events: PubSub[EventCamera]
    _max_retry_attempts: int
    _current_retry_count: int
    _retry_interval: timedelta
    _time_sleep: Callable[[float], None]

    def __init__(
        self,
        devices: list[Optional[DeviceCamera]],
        logger: Logger,
        max_retry_attempts: int = 3,
        retry_interval: timedelta = timedelta(seconds=1.0),
        time_sleep: Callable[[float], None] = time.sleep,
    ):
        devices_cleaned: list[DeviceCamera] = [d for d in devices if d is not None]
        if not devices_cleaned:
            raise ValueError("At least one device must be provided")

        self._logger = logger.getChild("with_fallbacks")
        self._logger.info(
            f"Initializing WithFallbacks with {len(devices_cleaned)} devices"
        )
        self._devices = cycle(devices_cleaned)
        self._current_device = next(self._devices)
        self._log_device_info("Initial device selected")
        self._lock = threading.Lock()
        self._connected = False
        self._events = PubSub[EventCamera]()
        self._max_retry_attempts = max_retry_attempts
        self._current_retry_count = 0
        self._retry_interval = retry_interval
        self._time_sleep = time_sleep
        self._logger.info(
            f"WithFallbacks initialized successfully with {max_retry_attempts} retry attempts per device"
        )

    def start(self) -> None:
        """Start the current camera device."""
        self._logger.info("Starting WithFallbacks camera")
        self._current_device.start()
        self._attempt_connection()

    def stop(self) -> None:
        """Stop the current camera device."""
        self._logger.info("Stopping WithFallbacks camera")
        with self._lock:
            self._connected = False
            self._current_device.stop()
        self._logger.info("WithFallbacks camera stopped")

    def capture(self) -> list[Image]:
        """Capture frames from the current device with connection handling."""
        self._logger.debug("Attempting to capture frames")

        if not self._ensure_device_connected():
            return []

        return self._try_capture_frames()

    def _ensure_device_connected(self) -> bool:
        """Ensure device is connected, attempt connection if needed."""
        if self.is_connected():
            return True

        self._logger.warning("Device not connected, attempting connection")
        return self._attempt_connection()

    def _try_capture_frames(self) -> list[Image]:
        """Try to capture frames and handle any failures."""
        try:
            frames = self._current_device.capture()

            if not frames:
                self._logger.warning("Device returned empty frame list")
                self._handle_connection_failure()
                return []

            # Reset retry count on successful capture
            self._current_retry_count = 0
            return frames

        except Exception as e:
            self._logger.error(f"Error capturing frames: {e}", exc_info=True)
            self._handle_connection_failure()
            return []

    def _ensure_connected(self) -> bool:
        if self.is_connected():
            return True

        self._logger.info("Device not connected, attempting connection")
        self._attempt_connection()

        if not self.is_connected():
            self._logger.warning(
                "Failed to connect any device, returning empty frame list"
            )
            return False

        return True

    def _capture_frames(self) -> list[Image]:
        self._log_device_info("Capturing frames from")
        frames = self._current_device.capture()

        if not frames:
            self._logger.debug("Device returned empty frame list")
            return []

        self._logger.debug(f"Successfully captured {len(frames)} frames")
        return frames

    def events(self) -> PubSub[EventCamera]:
        return self._events

    def is_connected(self) -> bool:
        with self._lock:
            connected = self._connected and self._current_device.is_connected()
            self._logger.debug(f"Connection status: {connected}")
            return connected

    def _attempt_connection(self) -> bool:
        self._logger.info("Attempting to connect to a device")
        with self._lock:
            start_device = self._current_device
            result = self._try_connect_devices(start_device)
            self._logger.info(f"Connection attempt result: {result}")
            return result

    def _try_connect_devices(self, start_device: DeviceCamera) -> bool:
        self._logger.debug(
            f"Starting device rotation from {start_device.__class__.__name__}"
        )
        self._current_retry_count = 0

        while True:
            if self._try_connect_with_retries():
                return True

            # Move to next device after max retries
            self._current_retry_count = 0
            self._switch_to_next_device()

            # Check if we've tried all devices
            if self._current_device == start_device:
                return self._handle_all_devices_failed()

    def _try_connect_with_retries(self) -> bool:
        self._log_device_info("Trying to connect to")

        # Try to connect to current device
        if self._try_connect_current_device():
            self._log_device_info("Successfully connected to", level="info")
            self._current_retry_count = 0
            return True

        # Handle retry logic
        self._current_retry_count += 1
        if self._current_retry_count < self._max_retry_attempts:
            self._log_retry_attempt()
            return False

        return False

    def _log_retry_attempt(self) -> None:
        self._logger.info(
            f"Retry attempt {self._current_retry_count}/{self._max_retry_attempts} for current device"
        )
        self._logger.info(
            f"Sleeping for {self._retry_interval.total_seconds()} seconds before retry"
        )
        self._time_sleep(self._retry_interval.total_seconds())

    def _handle_all_devices_failed(self) -> bool:
        self._logger.error("Tried all devices with maximum retries, none could connect")
        self._connected = False
        return False

    def _try_connect_current_device(self) -> bool:
        self._log_device_info(
            f"Attempting to connect to device (attempt {self._current_retry_count + 1}/{self._max_retry_attempts})",
            level="info",
        )
        if not self._current_device._attempt_connection():
            self._log_device_info("Failed to connect to", level="warning")
            if self._current_retry_count + 1 >= self._max_retry_attempts:
                self._logger.warning(
                    "Maximum retry attempts reached, trying next fallback..."
                )
            return False

        self._connected = True
        self._log_device_info("Successfully connected to device", level="info")
        self._events.publish(EventCameraConnected())
        return True

    def _handle_connection_failure(self) -> None:
        with self._lock:
            self._connected = False
            current_device_name = self._current_device.__class__.__name__

            self._current_retry_count += 1
            if self._current_retry_count < self._max_retry_attempts:
                self._logger.warning(
                    f"Connection to current device {current_device_name} failed, retry attempt {self._current_retry_count}/{self._max_retry_attempts}"
                )
                self._current_device._handle_connection_failure()
                self._logger.info(
                    f"Sleeping for {self._retry_interval.total_seconds()} seconds before retry"
                )
                self._time_sleep(self._retry_interval.total_seconds())
                return

            # Reset retry count and move to next device
            self._current_retry_count = 0
            self._logger.warning(
                f"Connection to current device {current_device_name} failed after {self._max_retry_attempts} attempts, switching to next fallback..."
            )
            self._current_device._handle_connection_failure()
            self._current_device.stop()
            self._switch_to_next_device()
            self._current_device.start()

    def _switch_to_next_device(self) -> None:
        self._current_device = next(self._devices)
        self._log_device_info("Switched to next device", level="info")

    def _log_device_info(self, message: str, level: str = "debug") -> None:
        device_name = self._current_device.__class__.__name__
        log_message = f"{message}: {device_name}"

        if level == "debug":
            self._logger.debug(log_message)
        elif level == "info":
            self._logger.info(log_message)
        elif level == "warning":
            self._logger.warning(log_message)
        elif level == "error":
            self._logger.error(log_message)
