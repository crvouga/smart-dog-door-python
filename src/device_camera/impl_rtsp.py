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
    _pub_sub: PubSub[EventCamera]
    _capture_thread: Optional[threading.Thread]
    _running: bool
    _lock: threading.Lock
    _cap: Optional[cv2.VideoCapture]
    _latest_frame: Optional[cv2.typing.MatLike]
    _connected: bool

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

        self._logger = logger.getChild("rstp_device_camera")
        self._rtsp_url = rtsp_url
        self._pub_sub = PubSub[EventCamera]()
        self._capture_thread = None
        self._running = False
        self._lock = threading.Lock()
        self._cap = None
        self._latest_frame = None
        self._connected = False
        self._logger.info(f"Initialized for RTSP URL: {rtsp_url}")

    def start(self) -> None:
        self._logger.info("Starting RtspDeviceCamera...")
        if self._running:
            self._logger.warning("Already running.")
            return

        self._running = True
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        self._logger.info("Capture thread started.")

    def stop(self) -> None:
        self._logger.info("Stopping RtspDeviceCamera...")
        if not self._running:
            self._logger.warning("Already stopped.")
            return

        self._stop_running()
        self._join_capture_thread()
        self._cleanup_resources()
        self._logger.info("RtspDeviceCamera stopped.")

    def _stop_running(self) -> None:
        self._running = False

    def _join_capture_thread(self) -> None:
        if not self._capture_thread:
            return

        self._capture_thread.join(timeout=5.0)
        if self._capture_thread.is_alive():
            self._logger.warning("Capture thread did not exit cleanly.")
        self._capture_thread = None

    def _cleanup_resources(self) -> None:
        with self._lock:
            self._release_capture()
            self._latest_frame = None
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

    def _handle_disconnection(self) -> None:
        if not self._connected:
            return

        self._connected = False
        self._publish_event(EventCameraDisconnected())

    def _publish_event(self, event: EventCamera) -> None:
        try:
            self._pub_sub.publish(event)
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")

    def _capture_loop(self) -> None:
        reconnect_delay_seconds = 5
        while self._running:
            try:
                self._attempt_connection()
                self._process_frames()
            except Exception as e:
                self._logger.error(f"Exception in capture loop: {e}", exc_info=True)
                self._handle_connection_failure()
                time.sleep(reconnect_delay_seconds)

    def _attempt_connection(self) -> None:
        with self._lock:
            if self._cap is not None:
                return

            self._logger.info(f"Attempting to connect to RTSP stream: {self._rtsp_url}")
            cap = cv2.VideoCapture(self._rtsp_url)

            if not cap.isOpened():
                self._logger.warning("Failed to open stream immediately, will retry...")
                cap.release()
                time.sleep(5)
                return

            self._logger.info("RTSP stream opened successfully.")
            self._cap = cap

            if not self._connected:
                self._connected = True
                self._publish_event(EventCameraConnected())

    def _process_frames(self) -> None:
        with self._lock:
            if self._cap is None:
                return

            ret, frame = self._cap.read()

        if not ret or frame is None:
            self._handle_frame_failure()
            return

        with self._lock:
            self._latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _handle_frame_failure(self) -> None:
        self._logger.warning("Failed to read frame from stream or stream ended.")
        self._handle_connection_failure()
        time.sleep(5)

    def _handle_connection_failure(self) -> None:
        with self._lock:
            if self._cap:
                try:
                    self._cap.release()
                except Exception as release_err:
                    self._logger.error(f"Error releasing capture: {release_err}")

            self._cap = None
            self._latest_frame = None

            if self._connected:
                self._connected = False
                self._publish_event(EventCameraDisconnected())

    def capture(self) -> List[Image]:
        """Captures the latest frame from the camera stream."""
        frame_data = None
        with self._lock:
            if self._latest_frame is not None:
                # Create a copy to avoid issues if the background thread updates it
                frame_data = self._latest_frame.copy()

        if frame_data is not None:
            # Assuming Image constructor takes numpy array
            return [Image.from_np_array(frame_data)]
        else:
            # Not connected or no frame received yet
            # self._logger.debug("Capture called but no frame available.")
            return []

    def events(self) -> Sub[EventCamera]:
        """Returns the event subscriber."""
        return self._pub_sub
