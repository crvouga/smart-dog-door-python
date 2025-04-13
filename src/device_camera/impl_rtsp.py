import cv2  # type: ignore
import threading
import time
from logging import Logger
from typing import List, Optional, cast

from src.image.image import Image
from src.library.life_cycle import LifeCycle
from src.library.pub_sub import PubSub, Sub
from .interface import DeviceCamera
from .event import (
    EventCamera,
    EventCameraConnected,
    EventCameraDisconnected,
)


class RtspDeviceCamera(DeviceCamera):
    _logger: Logger
    _rtsp_url: str
    _cap: Optional[cv2.VideoCapture]
    _latest_frame: Optional[cv2.typing.MatLike]
    _pub_sub: PubSub[EventCamera]
    _connected: bool
    _lock: threading.Lock

    def __init__(self, logger: Logger, rtsp_url: str):
        """
        Initializes the RtspDeviceCamera.

        Args:
            logger: Logger instance.
            rtsp_url: The full RTSP URL for the camera stream
                      (e.g., "rtsp://user:pass@192.168.1.100/live").
        """
        if not rtsp_url:
            raise ValueError("RTSP URL cannot be empty.")

        self._logger = logger.getChild("rtsp_device_camera")
        self._rtsp_url = rtsp_url
        self._cap = None
        self._latest_frame = None
        self._pub_sub = PubSub[EventCamera]()
        self._connected = False
        self._lock = threading.Lock()
        self._logger.info(f"Initialized for RTSP URL: {rtsp_url}")

    def start(self) -> None:
        self._logger.info("Starting RtspDeviceCamera...")
        self._attempt_connection()

    def stop(self) -> None:
        self._logger.info("Stopping RtspDeviceCamera...")
        with self._lock:
            if self._cap:
                try:
                    self._cap.release()
                except Exception as e:
                    self._logger.error(f"Error releasing capture: {e}")
                self._cap = None
            self._connected = False
            self._latest_frame = None

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _attempt_connection(self) -> bool:
        with self._lock:
            if self._cap is not None:
                return True

            self._logger.info(f"Attempting to connect to RTSP stream: {self._rtsp_url}")
            cap = cv2.VideoCapture(self._rtsp_url)

            if not cap.isOpened():
                self._logger.warning("Failed to open stream immediately, will retry...")
                cap.release()
                return False

            self._logger.info("RTSP stream opened successfully.")
            self._cap = cap
            self._connected = True
            return True

    def _handle_connection_failure(self) -> None:
        with self._lock:
            if self._cap:
                try:
                    self._cap.release()
                except Exception as release_err:
                    self._logger.error(f"Error releasing capture: {release_err}")

            self._cap = None
            self._latest_frame = None
            self._connected = False

    def _process_frames(self) -> None:
        with self._lock:
            if self._cap is None:
                return

            ret, frame = self._cap.read()

        if not ret or frame is None:
            self._handle_connection_failure()
            return

        with self._lock:
            self._latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def capture(self) -> List[Image]:
        """Captures the latest frame from the camera stream."""
        frame_data = None
        with self._lock:
            if self._latest_frame is not None:
                # Create a copy to avoid issues if the background thread updates it
                frame_data = self._latest_frame.copy()

        if frame_data is not None:
            return [Image.from_np_array(frame_data)]
        else:
            return []

    def events(self) -> PubSub[EventCamera]:
        return self._pub_sub
