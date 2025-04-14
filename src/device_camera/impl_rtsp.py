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
    _frame_thread: Optional[threading.Thread]
    _running: bool
    _frame_counter: int  # Track frame updates

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
        self._frame_thread = None
        self._running = False
        self._frame_counter = 0  # Initialize frame counter
        self._logger.info(f"Initialized for RTSP URL: {rtsp_url}")

    def start(self) -> None:
        self._logger.info("Starting RtspDeviceCamera...")
        self._running = True
        if self._attempt_connection():
            self._start_frame_processing()

    def stop(self) -> None:
        self._logger.info("Stopping RtspDeviceCamera...")
        self._running = False
        if self._frame_thread and self._frame_thread.is_alive():
            self._frame_thread.join(timeout=2.0)

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

    def _start_frame_processing(self) -> None:
        if self._frame_thread and self._frame_thread.is_alive():
            return

        self._frame_thread = threading.Thread(
            target=self._frame_processing_loop, daemon=True, name="RtspFrameProcessor"
        )
        self._frame_thread.start()
        self._logger.info("Frame processing thread started")

    def _frame_processing_loop(self) -> None:
        self._logger.info("Frame processing loop started")
        consecutive_failures = 0
        while self._running:
            try:
                if not self.is_connected():
                    if not self._attempt_connection():
                        time.sleep(1.0)  # Wait before retry
                        continue

                # Process frames continuously
                while self._running and self.is_connected():
                    success = self._process_frames()
                    if not success:
                        consecutive_failures += 1
                        self._logger.warning(
                            f"Frame processing failure #{consecutive_failures}"
                        )
                        if consecutive_failures >= 3:
                            self._handle_connection_failure()
                            consecutive_failures = 0
                            break  # Exit inner loop to attempt reconnection
                        time.sleep(0.1)  # Short delay before retry
                    else:
                        consecutive_failures = 0
                        # Small sleep to control frame rate
                        time.sleep(0.033)  # ~30 FPS

            except Exception as e:
                self._logger.error(f"Error in frame processing loop: {e}")
                self._handle_connection_failure()
                time.sleep(1.0)

    def _attempt_connection(self) -> bool:
        self._logger.info(f"Attempting to connect to RTSP stream: {self._rtsp_url}")
        try:
            # Create a new capture object outside the lock to avoid deadlocks
            cap = cv2.VideoCapture(self._rtsp_url)

            if not cap.isOpened():
                self._logger.warning("Failed to open stream immediately, will retry...")
                cap.release()
                return False

            # Test read a frame to ensure camera is working
            ret, test_frame = cap.read()
            if not ret or test_frame is None:
                self._logger.warning("Stream opened but failed to read test frame")
                cap.release()
                return False

            # Only lock when updating shared state
            with self._lock:
                # Release any existing capture
                if self._cap:
                    try:
                        self._cap.release()
                    except Exception as e:
                        self._logger.error(f"Error releasing previous capture: {e}")

                self._cap = cap
                self._latest_frame = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
                self._connected = True
                self._frame_counter = 1  # Reset frame counter on new connection

            self._publish_event(EventCameraConnected())
            self._logger.info("RTSP stream opened successfully.")
            return True
        except Exception as e:
            self._logger.error(f"Error during connection attempt: {e}")
            return False

    def _handle_connection_failure(self) -> None:
        with self._lock:
            if self._cap:
                try:
                    self._cap.release()
                except Exception as release_err:
                    self._logger.error(f"Error releasing capture: {release_err}")

            if self._connected:
                self._connected = False
                self._publish_event(EventCameraDisconnected())
                self._logger.info(
                    "Camera disconnection event published due to connection failure"
                )

            self._cap = None
            self._latest_frame = None
            self._frame_counter = 0  # Reset frame counter on disconnection

    def _publish_event(self, event: EventCamera) -> None:
        try:
            self._pub_sub.publish(event)
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")

    def _process_frames(self) -> bool:
        if not self._running:
            return False

        try:
            # Get the capture object without holding the lock
            with self._lock:
                if self._cap is None:
                    return False
                cap = self._cap  # Local reference

            # Read frame without holding the lock
            ret, frame = cap.read()
            if not ret or frame is None:
                self._logger.warning("Failed to read frame from stream")
                return False

            # Convert and update shared state with lock
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            with self._lock:
                self._latest_frame = rgb_frame
                self._frame_counter += 1
                if self._frame_counter % 100 == 0:  # Log periodically
                    self._logger.debug(f"Processed frame #{self._frame_counter}")

            return True
        except Exception as e:
            self._logger.error(f"Error reading frame: {e}")
            return False

    def capture(self) -> List[Image]:
        """Captures the latest frame from the camera stream."""
        frame_data = None
        frame_count = 0

        with self._lock:
            if self._latest_frame is not None:
                # Create a copy to avoid issues if the background thread updates it
                frame_data = self._latest_frame.copy()
                frame_count = self._frame_counter
                self._logger.debug(f"Captured frame #{frame_count}")

        if frame_data is not None:
            return [Image.from_np_array(frame_data)]
        else:
            self._logger.warning("No frame available to capture")
            return []

    def events(self) -> PubSub[EventCamera]:
        return self._pub_sub
