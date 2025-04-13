import os
from dotenv import load_dotenv
from dataclasses import dataclass
from src.library.secret_string import SecretString
from typing import Any


@dataclass
class Env:
    wyze_key_id: str
    wyze_api_key: SecretString
    wyze_email: str
    wyze_password: SecretString
    wyze_bridge_host_ip: str
    wyze_bridge_api_key: str
    kasa_device_ip: str

    @classmethod
    def load(cls) -> "Env":
        load_dotenv()

        wyze_key_id = _ensure_non_empty_string(os.getenv("WYZE_KEY_ID"))

        wyze_api_key = SecretString(
            name="wyze_api_key",
            secret=_ensure_non_empty_string(os.getenv("WYZE_API_KEY")),
        )

        wyze_email = _ensure_non_empty_string(os.getenv("WYZE_EMAIL"))

        wyze_password = SecretString(
            name="wyze_password",
            secret=_ensure_non_empty_string(os.getenv("WYZE_PASSWORD")),
        )

        wyze_bridge_host_ip = _ensure_non_empty_string(
            os.getenv("WYZE_BRIDGE_HOST_IP", "localhost")
        )

        wyze_bridge_api_key = _ensure_non_empty_string(
            os.getenv("WYZE_BRIDGE_API_KEY", "My-Custom-API-Key-For-WebUI")
        )

        kasa_device_ip = _ensure_non_empty_string(os.getenv("KASA_DEVICE_IP"))

        env = cls(
            wyze_key_id=wyze_key_id,
            wyze_api_key=wyze_api_key,
            wyze_email=wyze_email,
            wyze_password=wyze_password,
            wyze_bridge_host_ip=wyze_bridge_host_ip,
            wyze_bridge_api_key=wyze_bridge_api_key,
            kasa_device_ip=kasa_device_ip,
        )

        return env


def _ensure_non_empty_string(name: Any) -> str:
    if isinstance(name, str) and name:
        return name
    else:
        raise ValueError(f"{name} is not a non-empty string")
