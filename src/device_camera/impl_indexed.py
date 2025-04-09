import cv2  # type: ignore
import threading
import time
from logging import Logger
from typing import List, Optional, Iterator
from itertools import cycle
from src.image.image import Image
from src.library.pub_sub import PubSub, Sub
from .interface import DeviceCamera
from .event import (
    EventCamera,
    EventCameraConnected,
    EventCameraDisconnected,
)


class IndexedDeviceCamera(DeviceCamera):
    _logger: Logger
    _device_ids: List[int]
    _device_id_cycle: Iterator[int]
    _pub_sub: PubSub[EventCamera]
    _capture_thread: Optional[threading.Thread]
    _running: bool
    _lock: threading.Lock
    _cap: Optional[cv2.VideoCapture]
    _latest_frame: Optional[cv2.typing.MatLike]
    _connected: bool

    def __init__(self, logger: Logger, device_ids: List[int]):
        self._logger = logger.getChild("indexed_device_camera")
        self._device_ids = device_ids
        self._device_id_cycle = cycle(device_ids)
        self._pub_sub = PubSub[EventCamera]()
        self._capture_thread = None
        self._running = False
        self._lock = threading.Lock()
        self._cap = None
        self._latest_frame = None
        self._connected = False
        self._logger.info(f"Initialized for camera IDs: {device_ids}")

    def start(self) -> None:
        if self._running:
            self._logger.warning("Already running.")
            return

        self._logger.info("Starting IndexedDeviceCamera...")
        self._running = True
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        self._logger.info("Capture thread started.")

    def stop(self) -> None:
        if not self._running:
            self._logger.warning("Already stopped.")
            return

        self._logger.info("Stopping IndexedDeviceCamera...")
        self._running = False
        self._cleanup_capture_thread()
        self._cleanup_camera()
        self._logger.info("IndexedDeviceCamera stopped.")

    def _cleanup_capture_thread(self) -> None:
        if not self._capture_thread:
            return

        self._capture_thread.join(timeout=5.0)
        if self._capture_thread.is_alive():
            self._logger.warning("Capture thread did not exit cleanly.")
        self._capture_thread = None

    def _cleanup_camera(self) -> None:
        with self._lock:
            self._release_capture()
            self._reset_frame()
            self._handle_disconnection()

    def _release_capture(self) -> None:
        if not self._cap:
            return

        try:
            self._cap.release()
            self._logger.info("OpenCV capture released.")
        except Exception as e:
            self._logger.error(f"Error releasing OpenCV capture: {e}")
        self._cap = None

    def _reset_frame(self) -> None:
        self._latest_frame = None

    def _handle_disconnection(self) -> None:
        if not self._connected:
            return

        self._connected = False
        self._publish_event(EventCameraDisconnected())

    def capture(self) -> List[Image]:
        with self._lock:
            if not self._connected or self._latest_frame is None:
                return []
            # Convert color space BGR (OpenCV default) to RGB
            frame_rgb = cv2.cvtColor(self._latest_frame, cv2.COLOR_BGR2RGB)
            return [Image.from_np_array(frame_rgb)]

    def events(self) -> Sub[EventCamera]:
        return self._pub_sub

    def _publish_event(self, event: EventCamera) -> None:
        try:
            self._pub_sub.publish(event)
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")

    def _get_next_device_id(self) -> int:
        return next(self._device_id_cycle)

    def _connect_camera(self) -> bool:
        if self._cap is not None:
            return True

        device_id = self._get_next_device_id()
        self._logger.info(f"Attempting to connect to camera: {device_id}")
        try:
            cap = cv2.VideoCapture(device_id)
            if not cap.isOpened():
                self._logger.warning(
                    f"Failed to open camera {device_id}, will try next..."
                )
                return False

            self._cap = cap
            self._connected = True
            self._publish_event(EventCameraConnected())
            return True
        except Exception as e:
            self._logger.error(f"Error connecting to camera {device_id}: {e}")
            return False

    def _handle_frame_read_failure(self) -> None:
        with self._lock:
            if self._cap:
                self._cap.release()
                self._cap = None
            if self._connected:
                self._connected = False
                self._publish_event(EventCameraDisconnected())

    def _capture_loop(self) -> None:
        reconnect_delay_seconds = 1
        while self._running:
            try:
                self._attempt_capture()
            except Exception as e:
                self._logger.error(f"Error in capture loop: {e}")
                self._handle_frame_read_failure()
                time.sleep(reconnect_delay_seconds)

    def _attempt_capture(self) -> None:
        reconnect_delay_seconds = 1

        if not self._try_connect_camera():
            time.sleep(reconnect_delay_seconds)
            return

        if not self._cap:
            time.sleep(reconnect_delay_seconds)
            return

        if not self._read_and_store_frame():
            time.sleep(reconnect_delay_seconds)
            return

    def _try_connect_camera(self) -> bool:
        with self._lock:
            return self._connect_camera()

    def _read_and_store_frame(self) -> bool:
        if not self._cap:
            return False

        try:
            ret, frame = self._cap.read()
            if not ret or frame is None:
                self._logger.warning("Failed to read frame from camera")
                self._handle_frame_read_failure()
                return False

            with self._lock:
                self._latest_frame = frame
            return True
        except Exception as e:
            self._logger.error(f"Error reading frame: {e}")
            self._handle_frame_read_failure()
            return False
