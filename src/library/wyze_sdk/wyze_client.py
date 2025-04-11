from dataclasses import dataclass
from typing import List, Dict, Any
from wyze_sdk import Client  # type: ignore
from wyze_sdk.errors import WyzeApiError  # type: ignore
from logging import Logger
from src.library.secret_string import SecretString
from urllib.parse import quote


@dataclass
class WyzeDevice:
    mac: str
    nickname: str
    is_online: bool
    model: str

    @property
    def name(self) -> str:
        """Normalize camera name to match wyze-bridge format."""

        return quote(self.nickname.strip().lower().replace(" ", "-"))


class WyzeClient:
    _logger: Logger
    _client: Client

    def __init__(
        self,
        logger: Logger,
        email: str,
        password: SecretString,
        key_id: str,
        api_key: SecretString,
    ):
        self._logger = logger.getChild("wyze_client")
        self._init_client(
            email=email, password=password, key_id=key_id, api_key=api_key
        )

    def _init_client(
        self,
        email: str,
        password: SecretString,
        key_id: str,
        api_key: SecretString,
    ) -> None:
        self._client = Client()
        try:
            self._client.login(
                email=email,
                password=password.dangerously_read_secret(),
                key_id=key_id,
                api_key=api_key.dangerously_read_secret(),
            )
            self._logger.info("Successfully logged in to Wyze API")
        except Exception as e:
            self._logger.error(f"Failed to login to Wyze API: {e}")
            raise

    def get_device_info(self, device_mac: str) -> Dict[str, Any]:
        """Get detailed information about the device."""
        try:
            info = self._client.cameras.info(device_mac=device_mac)
            self._logger.info(f"Device info: {info}")
            return info
        except WyzeApiError as e:
            self._logger.error(f"Error getting device info: {e}")
            raise

    def list_devices(self) -> List[WyzeDevice]:
        """List all Wyze devices."""
        try:
            response = self._client.devices_list()
            devices: List[WyzeDevice] = []
            for device in response:
                devices.append(
                    WyzeDevice(
                        mac=device.mac,
                        nickname=device.nickname,
                        is_online=device.is_online,
                        model=device.product.model,
                    )
                )
            return devices
        except WyzeApiError as e:
            self._logger.error(f"Error listing devices: {e}")
            raise

    @property
    def wyze_sdk_client(self) -> Client:
        return self._client
