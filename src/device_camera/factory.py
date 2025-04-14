from datetime import timedelta
import logging
from typing import Optional
from src.device_camera.interface import DeviceCamera
from src.device_camera.impl_rtsp import RtspDeviceCamera
from src.device_camera.impl_indexed import IndexedDeviceCamera
from src.device_camera.impl_wyze_client import WyzeSdkCamera
from src.device_camera.impl_wyze_rtsp import WyzeRtspDeviceCamera
from src.device_camera.with_retry import WithRetry
from src.device_camera.with_fallbacks import WithFallbacks
from src.library.wyze_sdk.wyze_client import WyzeClient, WyzeDevice
from src.library.docker_wyze_bridge import DockerWyzeBridge
from src.env import Env


class DeviceCameraFactory:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild("device_camera_factory")

    def create_from_env(self, env: Env) -> DeviceCamera:
        """Factory method to create the appropriate camera based on environment configuration."""

        device_camera = WithFallbacks(
            devices=[
                self.create_wyze_rtsp(env=env),
                self.create_indexed(),
                # self.create_wyze_sdk(env=env),
            ],
            max_retry_attempts=3,
            retry_interval=timedelta(seconds=1.0),
            logger=self._logger,
        )

        return device_camera

    def create_indexed(self) -> IndexedDeviceCamera:
        """Create a camera using device index (e.g., webcam)."""
        return IndexedDeviceCamera(logger=self._logger, device_ids=[0])

    def create_wyze_rtsp(self, env: Env) -> Optional[DeviceCamera]:
        """Create a Wyze camera using RTSP protocol."""
        self._logger.info("Initializing Wyze rtsp device camera")

        wyze_client = self._init_wyze_client(env=env)

        wyze_device = self._get_wyze_device(wyze_client=wyze_client)

        if not wyze_device:
            return None

        wyze_device_camera = WyzeRtspDeviceCamera(
            logger=self._logger,
            wyze_client=wyze_client,
            wyze_device=wyze_device,
            host_ip=env.wyze_bridge_host_ip,
            api_key=env.wyze_bridge_api_key,
        )
        return wyze_device_camera

    def create_wyze_sdk(self, env: Env) -> Optional[WyzeSdkCamera]:
        """Create a Wyze camera using the official SDK."""
        wyze_client = self._init_wyze_client(env=env)
        wyze_device = self._get_wyze_device(wyze_client=wyze_client)

        if not wyze_device:
            return None

        wyze_device_camera = WyzeSdkCamera(
            wyze_client=wyze_client,
            logger=self._logger,
            wyze_device=wyze_device,
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
