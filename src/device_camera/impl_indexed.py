import cv2  # type: ignore
import threading
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
    _lock: threading.Lock
    _cap: Optional[cv2.VideoCapture]
    _latest_frame: Optional[cv2.typing.MatLike]
    _connected: bool

    def __init__(self, logger: Logger, device_ids: List[int]):
        self._logger = logger.getChild("indexed_device_camera")
        self._device_ids = device_ids
        self._device_id_cycle = cycle(device_ids)
        self._pub_sub = PubSub[EventCamera]()
        self._lock = threading.Lock()
        self._cap = None
        self._latest_frame = None
        self._connected = False
        self._logger.info(f"Initialized for camera IDs: {device_ids}")

    def start(self) -> None:
        self._logger.info("Starting IndexedDeviceCamera...")
        self._attempt_connection()

    def stop(self) -> None:
        self._logger.info("Stopping IndexedDeviceCamera...")
        self._cleanup_camera()
        self._logger.info("IndexedDeviceCamera stopped.")

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

    def events(self) -> PubSub[EventCamera]:
        return self._pub_sub

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _attempt_connection(self) -> bool:
        device_id = self._get_next_device_id()
        self._logger.info(f"Attempting to connect to camera: {device_id}")
        try:
            cap = cv2.VideoCapture(device_id)
            if not cap.isOpened():
                self._logger.warning(
                    f"Failed to open camera {device_id}, will try next..."
                )
                return False

            with self._lock:
                self._cap = cap
                self._connected = True
                self._publish_event(EventCameraConnected())
            return True
        except Exception as e:
            self._logger.error(f"Error connecting to camera {device_id}: {e}")
            return False

    def _handle_connection_failure(self) -> None:
        with self._lock:
            if self._cap:
                try:
                    self._cap.release()
                except Exception as e:
                    self._logger.error(f"Error releasing capture: {e}")
                self._cap = None

            if self._connected:
                self._connected = False
                self._publish_event(EventCameraDisconnected())
            self._latest_frame = None

    def _publish_event(self, event: EventCamera) -> None:
        try:
            self._pub_sub.publish(event)
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")

    def _get_next_device_id(self) -> int:
        return next(self._device_id_cycle)

    def _process_frames(self) -> None:
        with self._lock:
            if not self._cap:
                return

            try:
                ret, frame = self._cap.read()
                if not ret or frame is None:
                    self._logger.warning("Failed to read frame from camera")
                    self._handle_connection_failure()
                    return

                self._latest_frame = frame
            except Exception as e:
                self._logger.error(f"Error reading frame: {e}")
                self._handle_connection_failure()
