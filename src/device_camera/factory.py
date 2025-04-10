import logging
from typing import Optional
from src.device_camera.interface import DeviceCamera
from src.device_camera.impl_rstp import RstpDeviceCamera
from src.device_camera.impl_indexed import IndexedDeviceCamera
from src.device_camera.impl_wyze_client import WyzeSdkCamera
from src.library.wyze_sdk.wyze_client import WyzeClient, WyzeDevice
from src.library.docker_wyze_bridge import DockerWyzeBridge
from src.env import Env


class DeviceCameraFactory:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild("device_camera_factory")

    def create_camera(self, env: Env) -> Optional[DeviceCamera]:
        """Factory method to create the appropriate camera based on environment configuration."""
        wyze_rstp_device_camera = self._create_wyze_rstp_camera(env=env)

        if True:  # TODO: Add proper condition based on env configuration
            return wyze_rstp_device_camera

        wyze_device_camera = self._create_wyze_sdk_camera(env=env)

        if not wyze_device_camera:
            return self._create_indexed_camera()

        return wyze_device_camera

    def _create_indexed_camera(self) -> IndexedDeviceCamera:
        """Create a camera using device index (e.g., webcam)."""
        return IndexedDeviceCamera(logger=self._logger, device_ids=[0])

    def _create_wyze_rstp_camera(self, env: Env) -> Optional[DeviceCamera]:
        """Create a Wyze camera using RTSP protocol."""
        self._logger.info("Initializing Wyze RSTP device camera")
        wyze_client = self._init_wyze_client(env=env)
        wyze_device = self._get_wyze_device(wyze_client=wyze_client)
        wyze_bridge = DockerWyzeBridge(camera_name=wyze_device.name)
        wyze_device_camera = RstpDeviceCamera(
            logger=self._logger, rtsp_url=wyze_bridge.rstp_url
        )
        return wyze_device_camera

    def _create_wyze_sdk_camera(self, env: Env) -> Optional[WyzeSdkCamera]:
        """Create a Wyze camera using the official SDK."""
        wyze_client = self._init_wyze_client(env=env)
        wyze_device = self._get_wyze_device(wyze_client=wyze_client)

        if not wyze_device:
            return None

        wyze_device_camera = WyzeSdkCamera(
            wyze_client=wyze_client,
            logger=self._logger,
            device_mac=wyze_device.mac,
            device_model=wyze_device.model,
        )
        return wyze_device_camera

    def _get_wyze_device(self, wyze_client: WyzeClient) -> Optional[WyzeDevice]:
        """Get the first available Wyze device."""
        wyze_devices = wyze_client.list_devices()

        if not wyze_devices:
            return None

        wyze_device = wyze_devices[0]
        return wyze_device

    def _init_wyze_client(self, env: Env) -> WyzeClient:
        """Initialize the Wyze client with credentials from the environment."""
        return WyzeClient(
            logger=self._logger,
            email=env.wyze_email,
            password=env.wyze_password,
            key_id=env.wyze_key_id,
            api_key=env.wyze_api_key,
        )
