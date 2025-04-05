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
    EventCameraError,
)


class RstpDeviceCamera(DeviceCamera):

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
        Initializes the RstpDeviceCamera.

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
        self._logger.info("Starting RstpDeviceCamera...")
        if self._running:
            self._logger.warning("Already running.")
            return

        self._running = True
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        self._logger.info("Capture thread started.")

    def stop(self) -> None:
        self._logger.info("Stopping RstpDeviceCamera...")
        if not self._running:
            self._logger.warning("Already stopped.")
            return

        self._running = False
        if self._capture_thread:
            self._capture_thread.join(timeout=5.0)  # Wait for thread exit
            if self._capture_thread.is_alive():
                self._logger.warning("Capture thread did not exit cleanly.")
            self._capture_thread = None

        with self._lock:
            if self._cap:
                try:
                    self._cap.release()
                    self._logger.info("OpenCV capture released.")
                except Exception as e:
                    self._logger.error(f"Error releasing OpenCV capture: {e}")
                self._cap = None
            self._latest_frame = None
            if self._connected:
                self._connected = False
                self._publish_event(EventCameraDisconnected())

        self._logger.info("RstpDeviceCamera stopped.")

    def _publish_event(self, event: EventCamera) -> None:
        try:
            self._pub_sub.pub(event)
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")

    def _capture_loop(self) -> None:
        """Background thread to continuously capture frames."""
        reconnect_delay_seconds = 5
        while self._running:
            cap = None  # Local variable for capture instance
            try:
                with self._lock:
                    if self._cap is None:
                        self._logger.info(
                            f"Attempting to connect to RTSP stream: {self._rtsp_url}"
                        )
                        # Set environment variable for potential timeout (may vary in effectiveness)
                        # os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp|timeout;5000000" # 5 seconds timeout in microseconds
                        # cv2.CAP_PROP_OPEN_TIMEOUT_MSEC doesn't work for RTSP
                        cap = cv2.VideoCapture(self._rtsp_url)  # Attempt connection
                        # Check if opened immediately (might take time)
                        if not cap.isOpened():
                            self._logger.warning(
                                "Failed to open stream immediately, will retry..."
                            )
                            cap.release()
                            time.sleep(reconnect_delay_seconds)
                            continue  # Retry connection

                        self._logger.info("RTSP stream opened successfully.")
                        self._cap = cap  # Assign to instance variable only on success
                        if not self._connected:
                            self._connected = True
                            self._publish_event(EventCameraConnected())

                # Use the instance variable from now on within the lock
                with self._lock:
                    if self._cap is None:  # Check if connection dropped between loops
                        continue

                    ret, frame = self._cap.read()

                # Process outside the lock to minimize lock holding time
                if ret and frame is not None:
                    with self._lock:
                        # Convert color space BGR (OpenCV default) to RGB
                        self._latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Optional: Add a small sleep if CPU usage is too high
                    # time.sleep(0.01) # e.g., sleep for 10ms

                else:
                    self._logger.warning(
                        "Failed to read frame from stream or stream ended."
                    )
                    with self._lock:
                        if self._cap:
                            self._cap.release()
                        self._cap = None
                        self._latest_frame = None
                        if self._connected:
                            self._connected = False
                            self._publish_event(EventCameraDisconnected())
                            self._publish_event(
                                EventCameraError(
                                    reason="Stream disconnected or read error"
                                )
                            )
                    time.sleep(reconnect_delay_seconds)  # Wait before reconnect attempt

            except Exception as e:
                self._logger.error(f"Exception in capture loop: {e}", exc_info=True)
                with self._lock:
                    if self._cap:
                        try:
                            self._cap.release()
                        except Exception as release_err:
                            self._logger.error(
                                f"Error releasing capture after exception: {release_err}"
                            )
                    self._cap = None
                    self._latest_frame = None
                    if self._connected:
                        self._connected = False
                        self._publish_event(EventCameraDisconnected())
                        self._publish_event(EventCameraError(reason=f"Exception: {e}"))
                time.sleep(reconnect_delay_seconds)  # Wait before reconnect attempt

    def capture(self) -> List[Image]:
        """Captures the latest frame from the camera stream."""
        frame_data = None
        with self._lock:
            if self._latest_frame is not None:
                # Create a copy to avoid issues if the background thread updates it
                frame_data = self._latest_frame.copy()

        if frame_data is not None:
            # Assuming Image constructor takes numpy array
            return [Image(np_array=frame_data)]
        else:
            # Not connected or no frame received yet
            # self._logger.debug("Capture called but no frame available.")
            return []

    def events(self) -> Sub[EventCamera]:
        """Returns the event subscriber."""
        return self._pub_sub
