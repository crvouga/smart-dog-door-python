from src.image.image import Image
from src.library.pub_sub import PubSub, Sub
from .event import EventCamera, EventCameraConnected, EventCameraDisconnected
from .interface import DeviceCamera
from wyze_sdk import Client  # type: ignore
from wyze_sdk.errors import WyzeApiError  # type: ignore
import threading
import time
from logging import Logger
from typing import Optional, Union


class WyzeSdkCamera(DeviceCamera):
    _logger: Logger
    _client: Client
    _device_mac: str
    _pub_sub: PubSub[Union[EventCameraConnected, EventCameraDisconnected]]
    _capture_thread: Optional[threading.Thread]
    _running: bool
    _lock: threading.Lock
    _latest_frame: Optional[Image]
    _connected: bool

    def __init__(self, logger: Logger, client: Client, device_mac: str):
        self._logger = logger.getChild("wyze_device_camera")
        self._client = client
        self._device_mac = device_mac
        self._pub_sub = PubSub[Union[EventCameraConnected, EventCameraDisconnected]]()
        self._capture_thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_frame = None
        self._connected = False
        self._logger.info(f"Initialized for device MAC: {device_mac}")

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

    def _capture_loop(self) -> None:
        while self._running:
            try:
                # Get camera snapshot
                response = self._client.cameras.get_thumbnail(
                    device_mac=self._device_mac
                )
                if response and response.data:
                    frame = Image.from_np_array(response.data)
                    with self._lock:
                        self._latest_frame = frame
                    if not self._connected:
                        self._connected = True
                        self._pub_sub.publish(EventCameraConnected())
                else:
                    if self._connected:
                        self._connected = False
                        self._pub_sub.publish(EventCameraDisconnected())
            except WyzeApiError as e:
                self._logger.error(f"Error capturing frame: {e}")
                if self._connected:
                    self._connected = False
                    self._pub_sub.publish(EventCameraDisconnected())
            except Exception as e:
                self._logger.error(f"Unexpected error in capture loop: {e}")
                if self._connected:
                    self._connected = False
                    self._pub_sub.publish(EventCameraDisconnected())

            time.sleep(0.1)  # 10 FPS

    def capture(self) -> list[Image]:
        with self._lock:
            if self._latest_frame is None:
                return []
            return [self._latest_frame]

    def events(self) -> Sub[Union[EventCameraConnected, EventCameraDisconnected]]:
        return self._pub_sub
