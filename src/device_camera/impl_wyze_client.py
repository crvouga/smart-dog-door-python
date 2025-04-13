from src.image.image import Image
from src.library.pub_sub import PubSub, Sub
from .event import EventCamera, EventCameraConnected, EventCameraDisconnected
from .interface import DeviceCamera
from src.library.wyze_sdk.wyze_client import WyzeClient
import threading
import time
from logging import Logger
from typing import Optional, Union


class WyzeSdkCamera(DeviceCamera):
    _logger: Logger
    _wyze_client: WyzeClient
    _device_mac: str
    _device_model: str
    _pub_sub: PubSub[EventCamera]
    _capture_thread: Optional[threading.Thread]
    _running: bool
    _lock: threading.Lock
    _latest_frame: Optional[Image]
    _connected: bool

    def __init__(
        self,
        logger: Logger,
        device_mac: str,
        device_model: str,
        wyze_client: WyzeClient,
    ):
        self._logger = logger.getChild("wyze_device_camera")
        self._device_mac = device_mac
        self._device_model = device_model
        self._wyze_client = wyze_client
        self._pub_sub = PubSub[EventCamera]()
        self._capture_thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_frame = None
        self._connected = False

        self._log_list_cameras()
        self._log_details()

    def _log_details(self) -> None:
        self._logger.info("Details for camera...")
        response = self._wyze_client.get_device_info(device_mac=self._device_mac)
        self._logger.info(f"Response: {response}")

    def _log_list_cameras(self) -> None:
        self._logger.info("Listing cameras...")
        devices = self._wyze_client.list_devices()
        camera_count = sum(1 for d in devices if d.model.startswith("WYZE_CA"))
        self._logger.info(f"Found {camera_count} cameras")
        for device in devices:
            if device.model.startswith("WYZE_CA"):
                self._logger.info(f"Camera: {device}")
        self._logger.info("Listing cameras... done")

    def start(self) -> None:
        self._logger.info("Starting WyzeSdkCamera...")
        if self._running:
            self._logger.warning("Already running.")
            return

        self._running = True
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        self._logger.info("Capture thread started.")

    def stop(self) -> None:
        self._logger.info("Stopping WyzeSdkCamera...")
        if not self._running:
            self._logger.warning("Already stopped.")
            return

        self._running = False
        if self._capture_thread:
            self._capture_thread.join(timeout=5.0)
            if self._capture_thread.is_alive():
                self._logger.warning("Capture thread did not exit cleanly.")
            self._capture_thread = None

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _attempt_connection(self) -> bool:
        try:
            response = self._wyze_client.wyze_sdk_client.cameras.turn_on(
                device_mac=self._device_mac,
                device_model=self._device_model,
            )
            if response and response.data:
                with self._lock:
                    self._connected = True
                    self._pub_sub.publish(EventCameraConnected())
                return True
            return False
        except Exception as e:
            self._logger.error(f"Error connecting to camera: {e}")
            return False

    def _handle_connection_failure(self) -> None:
        with self._lock:
            if self._connected:
                self._connected = False
                self._pub_sub.publish(EventCameraDisconnected())
            self._latest_frame = None

    def _process_frames(self) -> None:
        try:
            response = self._wyze_client.wyze_sdk_client.cameras.turn_on(
                device_mac=self._device_mac,
                device_model=self._device_model,
            )

            if response and response.data:
                frame = Image.from_np_array(response.data)
                with self._lock:
                    self._latest_frame = frame
                    if not self._connected:
                        self._connected = True
                        self._pub_sub.publish(EventCameraConnected())
            else:
                self._handle_connection_failure()
        except Exception as e:
            self._logger.error(f"Error capturing frame: {e}")
            self._handle_connection_failure()

    def _capture_loop(self) -> None:
        while self._running:
            if not self.is_connected():
                if not self._attempt_connection():
                    continue

            self._process_frames()
            time.sleep(0.1)  # 10 FPS

    def capture(self) -> list[Image]:
        with self._lock:
            if self._latest_frame is None:
                return []
            return [self._latest_frame]

    def events(self) -> Sub[EventCamera]:
        return self._pub_sub
