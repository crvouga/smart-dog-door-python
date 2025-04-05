import cv2  # type: ignore
import threading
import time
from logging import Logger
from typing import List, Optional
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
    _device_id: int
    _pub_sub: PubSub[EventCamera]
    _capture_thread: Optional[threading.Thread]
    _running: bool
    _lock: threading.Lock
    _cap: Optional[cv2.VideoCapture]
    _latest_frame: Optional[cv2.typing.MatLike]
    _connected: bool

    def __init__(self, logger: Logger, device_id: int = 0):
        self._logger = logger.getChild("usb_device_camera")
        self._device_id = device_id
        self._pub_sub = PubSub[EventCamera]()
        self._capture_thread = None
        self._running = False
        self._lock = threading.Lock()
        self._cap = None
        self._latest_frame = None
        self._connected = False
        self._logger.info(f"Initialized for USB camera ID: {device_id}")

    def start(self) -> None:
        if self._running:
            self._logger.warning("Already running.")
            return

        self._logger.info("Starting UsbDeviceCamera...")
        self._running = True
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        self._logger.info("Capture thread started.")

    def stop(self) -> None:
        if not self._running:
            self._logger.warning("Already stopped.")
            return

        self._logger.info("Stopping UsbDeviceCamera...")
        self._running = False
        self._cleanup_capture_thread()
        self._cleanup_camera()
        self._logger.info("UsbDeviceCamera stopped.")

    def _cleanup_capture_thread(self) -> None:
        if not self._capture_thread:
            return

        self._capture_thread.join(timeout=5.0)
        if self._capture_thread.is_alive():
            self._logger.warning("Capture thread did not exit cleanly.")
        self._capture_thread = None

    def _cleanup_camera(self) -> None:
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

    def capture(self) -> List[Image]:
        with self._lock:
            if not self._connected or self._latest_frame is None:
                return []
            return [Image(self._latest_frame)]

    def events(self) -> Sub[EventCamera]:
        return self._pub_sub

    def _publish_event(self, event: EventCamera) -> None:
        try:
            self._pub_sub.pub(event)
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")

    def _connect_camera(self) -> bool:
        if self._cap is not None:
            return True

        self._logger.info(f"Attempting to connect to USB camera: {self._device_id}")
        cap = cv2.VideoCapture(self._device_id)
        if not cap.isOpened():
            self._logger.warning("Failed to open camera, will retry...")
            return False

        self._cap = cap
        self._connected = True
        self._publish_event(EventCameraConnected())
        return True

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
                with self._lock:
                    if not self._connect_camera():
                        time.sleep(reconnect_delay_seconds)
                        continue

                if not self._cap:
                    time.sleep(reconnect_delay_seconds)
                    continue

                ret, frame = self._cap.read()
                if not ret:
                    self._logger.warning("Failed to read frame from camera")
                    self._handle_frame_read_failure()
                    time.sleep(reconnect_delay_seconds)
                    continue

                with self._lock:
                    self._latest_frame = frame

            except Exception as e:
                self._logger.error(f"Error in capture loop: {e}")
                self._handle_frame_read_failure()
                time.sleep(reconnect_delay_seconds)
