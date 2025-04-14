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
    _frame_polling_thread: Optional[threading.Thread]
    _stop_polling: threading.Event

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
        self._frame_polling_thread = None
        self._stop_polling = threading.Event()
        self._logger.info(f"Initialized for RTSP URL: {rtsp_url}")

    def start(self) -> None:
        self._logger.info("Starting RtspDeviceCamera...")
        self._stop_polling.clear()
        if self._attempt_connection():
            self._start_frame_polling()
            self._pub_sub.publish(EventCameraConnected())

    def _start_frame_polling(self) -> None:
        if (
            self._frame_polling_thread is not None
            and self._frame_polling_thread.is_alive()
        ):
            return

        self._frame_polling_thread = threading.Thread(
            target=self._polling_loop, daemon=True, name="RtspFramePolling"
        )
        self._frame_polling_thread.start()
        self._logger.debug("Frame polling thread started")

    def _polling_loop(self) -> None:
        self._logger.debug("Frame polling loop started")
        while not self._stop_polling.is_set():
            self._process_frames()
            time.sleep(0.03)  # ~30 FPS

    def stop(self) -> None:
        self._logger.info("Stopping RtspDeviceCamera...")
        self._stop_polling.set()

        # Set a timeout for the thread join to prevent hanging
        if self._frame_polling_thread and self._frame_polling_thread.is_alive():
            try:
                self._frame_polling_thread.join(timeout=1.0)
                if self._frame_polling_thread.is_alive():
                    self._logger.warning(
                        "Frame polling thread did not terminate within timeout"
                    )
            except Exception as e:
                self._logger.error(f"Error joining frame polling thread: {e}")

        with self._lock:
            if self._cap:
                try:
                    self._cap.release()
                except Exception as e:
                    self._logger.error(f"Error releasing capture: {e}")
                finally:
                    self._cap = None

            if self._connected:
                self._connected = False
                self._pub_sub.publish(EventCameraDisconnected())

            self._latest_frame = None

        self._logger.info("RtspDeviceCamera stopped")

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _attempt_connection(self) -> bool:
        with self._lock:
            if self._cap is not None and self._connected:
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
        was_connected = False
        with self._lock:
            was_connected = self._connected
            if self._cap:
                try:
                    self._cap.release()
                except Exception as release_err:
                    self._logger.error(f"Error releasing capture: {release_err}")

            self._cap = None
            self._latest_frame = None
            self._connected = False

        if was_connected:
            self._logger.warning("Connection to RTSP stream lost")
            self._pub_sub.publish(EventCameraDisconnected())

    def _process_frames(self) -> None:
        with self._lock:
            if self._cap is None:
                return

            ret, frame = self._cap.read()

        if not ret or frame is None:
            self._logger.warning("Failed to read frame from RTSP stream")
            self._handle_connection_failure()
            return

        with self._lock:
            self._latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if not self._connected:
                self._connected = True
                self._pub_sub.publish(EventCameraConnected())

    def capture(self) -> List[Image]:
        """Captures the latest frame from the camera stream."""
        with self._lock:
            if not self._connected:
                self._logger.debug("Capture called but camera not connected")
                return []

            if self._latest_frame is None:
                self._logger.debug("Capture called but no frame available")
                return []

            # Create a copy to avoid issues if the background thread updates it
            try:
                frame_data = self._latest_frame.copy()
                self._logger.debug(f"Captured frame with shape: {frame_data.shape}")
                return [Image.from_np_array(frame_data)]
            except Exception as e:
                self._logger.error(f"Error creating image from frame: {e}")
                return []

    def events(self) -> PubSub[EventCamera]:
        return self._pub_sub
