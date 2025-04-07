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
    _pub_sub: PubSub[Union[EventCameraConnected, EventCameraDisconnected]]
    _capture_thread: Optional[threading.Thread]
    _running: bool
    _lock: threading.Lock
    _latest_frame: Optional[Image]
    _connected: bool
    _error_count: int
    _max_errors: int = 5  # Maximum number of consecutive errors before stopping

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
        self._pub_sub = PubSub[Union[EventCameraConnected, EventCameraDisconnected]]()
        self._capture_thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_frame = None
        self._connected = False
        self._error_count = 0

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
        self._error_count = 0
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

    def _capture_loop(self) -> None:
        while self._running:
            try:
                # Get camera snapshot
                print("self._device_mac", self._device_mac)
                response = self._wyze_client.wyze_sdk_client.cameras.turn_on(
                    device_mac=self._device_mac,
                    device_model=self._device_model,
                )

                print("response", response)
                return
                if response and response.data:
                    frame = Image.from_np_array(response.data)
                    with self._lock:
                        self._latest_frame = frame
                    if not self._connected:
                        self._connected = True
                        self._pub_sub.publish(EventCameraConnected())
                    self._error_count = 0  # Reset error count on successful capture
                else:
                    if self._connected:
                        self._connected = False
                        self._pub_sub.publish(EventCameraDisconnected())
                    self._error_count += 1
            except Exception as e:
                self._logger.error(f"Error capturing frame: {e}")
                if self._connected:
                    self._connected = False
                    self._pub_sub.publish(EventCameraDisconnected())
                self._error_count += 1

            # Stop if we've hit too many consecutive errors
            if self._error_count >= self._max_errors:
                self._logger.error(
                    f"Too many consecutive errors ({self._error_count}). Stopping camera."
                )
                self._running = False
                break

            time.sleep(0.1)  # 10 FPS

    def capture(self) -> list[Image]:
        with self._lock:
            if self._latest_frame is None:
                return []
            return [self._latest_frame]

    def events(self) -> Sub[Union[EventCameraConnected, EventCameraDisconnected]]:
        return self._pub_sub
