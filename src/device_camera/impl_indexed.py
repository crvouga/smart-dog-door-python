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
    _frame_thread: Optional[threading.Thread]
    _running: bool

    def __init__(self, logger: Logger, device_ids: List[int]):
        self._logger = logger.getChild("indexed_device_camera")
        self._device_ids = device_ids
        self._device_id_cycle = cycle(device_ids)
        self._pub_sub = PubSub[EventCamera]()
        self._lock = threading.Lock()
        self._cap = None
        self._latest_frame = None
        self._connected = False
        self._frame_thread = None
        self._running = False
        self._logger.info(f"Initialized for camera IDs: {device_ids}")

    def start(self) -> None:
        self._logger.info("Starting IndexedDeviceCamera...")
        self._running = True
        if self._attempt_connection():
            self._start_frame_processing()

    def stop(self) -> None:
        self._logger.info("Stopping IndexedDeviceCamera...")
        self._running = False
        if self._frame_thread and self._frame_thread.is_alive():
            self._frame_thread.join(timeout=1.0)
        self._cleanup_camera()
        self._logger.info("IndexedDeviceCamera stopped.")

    def _start_frame_processing(self) -> None:
        self._frame_thread = threading.Thread(
            target=self._frame_processing_loop,
            daemon=True,
            name="IndexedDeviceCamera-FrameProcessor",
        )
        self._frame_thread.start()
        self._logger.debug("Frame processing thread started")

    def _frame_processing_loop(self) -> None:
        consecutive_failures = 0
        max_failures = (
            3  # Number of consecutive failures before considering camera disconnected
        )

        while self._running and self._connected:
            success = self._process_frames()

            if not success:
                consecutive_failures += 1
                self._logger.warning(
                    f"Frame processing failure: {consecutive_failures}/{max_failures}"
                )

                if consecutive_failures >= max_failures:
                    self._logger.error("Camera appears to be disconnected")
                    self._cleanup_camera()  # This will trigger the disconnected event
                    break
            else:
                consecutive_failures = 0  # Reset counter on successful frame

            threading.Event().wait(0.03)  # ~30 FPS

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
        self._logger.info("Camera disconnection event published")

    def capture(self) -> List[Image]:
        with self._lock:
            if not self._connected or self._latest_frame is None:
                self._logger.debug("No frame available for capture")
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

            # Test read a frame to ensure camera is working
            ret, test_frame = cap.read()
            if not ret or test_frame is None:
                self._logger.warning(
                    f"Camera {device_id} opened but failed to read test frame"
                )
                cap.release()
                return False

            with self._lock:
                self._cap = cap
                self._latest_frame = test_frame  # Store the test frame
                self._connected = True
                self._publish_event(EventCameraConnected())
            self._logger.info(f"Successfully connected to camera {device_id}")
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
                self._logger.info(
                    "Camera disconnection event published due to connection failure"
                )
            self._latest_frame = None

    def _publish_event(self, event: EventCamera) -> None:
        try:
            self._pub_sub.publish(event)
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")

    def _get_next_device_id(self) -> int:
        return next(self._device_id_cycle)

    def _process_frames(self) -> bool:
        with self._lock:
            if not self._cap:
                return False

            try:
                ret, frame = self._cap.read()
                if not ret or frame is None:
                    self._logger.warning("Failed to read frame from camera")
                    return False

                self._latest_frame = frame
                return True
            except Exception as e:
                self._logger.error(f"Error reading frame: {e}")
                return False
