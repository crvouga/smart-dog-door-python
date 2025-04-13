import logging
from src.device_door.interface import DeviceDoor
from src.device_door.impl_fake import FakeDeviceDoor
from src.device_door.impl_kasa import KasaDeviceDoor
from src.env import Env


class DeviceDoorFactory:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild("device_door_factory")

    def create_from_env(self, env: Env) -> DeviceDoor:
        """Factory method to create the appropriate door device based on environment configuration."""
        if self._should_create_kasa_door(env):
            return self._create_kasa_door(env.kasa_device_ip)
        return self.create_fake_door()

    def _should_create_kasa_door(self, env: Env) -> bool:
        """Determine if a Kasa door device should be created."""
        return bool(env.kasa_device_ip)

    def _create_kasa_door(self, ip_address: str) -> DeviceDoor:
        """Create a Kasa door device with the given IP address."""
        try:
            self._logger.info(f"Creating Kasa device door with IP: {ip_address}")
            return KasaDeviceDoor(logger=self._logger, ip_address=ip_address)
        except Exception as e:
            self._logger.error(f"Failed to create Kasa device door: {e}")
            return self.create_fake_door()

    def create_fake_door(self) -> DeviceDoor:
        """Create a fake door device as fallback."""
        self._logger.info("Falling back to fake device door implementation")
        return FakeDeviceDoor(logger=self._logger)
