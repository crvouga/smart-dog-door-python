import logging
import time
from src.image.image import Image
from src.library.pub_sub import PubSub
from .event import EventCamera
from .interface import DeviceCamera
from .impl_rtsp import RtspDeviceCamera
from src.library.docker_wyze_bridge import DockerWyzeBridge
from src.library.wyze_sdk.wyze_client import WyzeClient, WyzeDevice


class WyzeRtspDeviceCamera(DeviceCamera):
    _logger: logging.Logger
    _rtsp_camera: RtspDeviceCamera
    _wyze_bridge: DockerWyzeBridge
    _wyze_client: WyzeClient
    _device_mac: str

    def __init__(
        self,
        logger: logging.Logger,
        wyze_client: WyzeClient,
        wyze_device: WyzeDevice,
        host_ip: str,
        api_key: str,
    ):
        """
        Initialize a Wyze camera that uses RTSP via Docker Wyze Bridge.

        Args:
            logger: Logger instance
            wyze_client: WyzeClient instance for API access
            wyze_device: The Wyze device to connect to
            host_ip: Host IP for the Docker Wyze Bridge
            api_key: API key for the Docker Wyze Bridge
        """
        self._logger = logger.getChild("wyze_rtsp_device_camera")
        self._wyze_client = wyze_client
        self._device_mac = wyze_device.mac

        # Initialize the Docker Wyze Bridge
        self._wyze_bridge = DockerWyzeBridge(
            camera_name=wyze_device.name,
            host_ip=host_ip,
            api_key=api_key,
            logger=self._logger,
        )

        # Create the underlying RTSP camera
        self._rtsp_camera = RtspDeviceCamera(
            logger=self._logger, rtsp_url=self._wyze_bridge.rtsp_url
        )

        self._logger.info(f"Initialized WyzeRtspDeviceCamera for {wyze_device.name}")
        self._logger.debug(f"Using RTSP URL: {self._wyze_bridge.rtsp_url}")

    def start(self) -> None:
        """Start the camera."""
        self._logger.info("Starting WyzeRtspDeviceCamera...")
        # Power on the camera before starting
        if self._wyze_bridge.power_on():
            self._logger.info("Successfully powered on the camera")
            time.sleep(1)
            self._logger.debug("Waited 1 second for camera initialization")
            if self._wyze_bridge.stream_enable():
                self._logger.info("Successfully enabled the camera stream")
            else:
                self._logger.warning("Failed to enable the camera stream")

        else:
            self._logger.warning("Failed to power on the camera")
        self._rtsp_camera.start()

    def stop(self) -> None:
        """Stop the camera."""
        self._logger.info("Stopping WyzeRtspDeviceCamera...")
        self._rtsp_camera.stop()
        # Power off the camera after stopping
        if self._wyze_bridge.power_off():
            self._logger.info("Successfully powered off the camera")
        else:
            self._logger.warning("Failed to power off the camera")

    def capture(self) -> list[Image]:
        """Capture the latest frame(s) from the camera."""
        return self._rtsp_camera.capture()

    def events(self) -> PubSub[EventCamera]:
        """Get the event subscriber for camera events."""
        return self._rtsp_camera.events()

    def is_connected(self) -> bool:
        """Check if the camera is currently connected."""
        return self._rtsp_camera.is_connected()

    def _attempt_connection(self) -> bool:
        """
        Attempt to establish a connection to the camera.
        Returns True if connection was successful, False otherwise.
        """
        return self._rtsp_camera._attempt_connection()

    def _handle_connection_failure(self) -> None:
        """
        Handle a connection failure, including cleanup and state management.
        This should be called when a connection attempt fails or when the connection is lost.
        """
        self._rtsp_camera._handle_connection_failure()
