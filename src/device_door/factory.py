import logging
from src.device_door.interface import DeviceDoor
from src.device_door.impl_fake import FakeDeviceDoor
from src.device_door.impl_smart_plug_magnet import SmartPlugMagnetDeviceDoor
from src.env import Env
from src.library.smart_plug.factory import SmartPlugFactory


class DeviceDoorFactory:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild("device_door_factory")

    def create_from_env(self, env: Env) -> DeviceDoor:
        """Factory method to create the appropriate door device based on environment configuration."""
        if self._should_create_kasa_door(env):
            return self._create_smart_plug_magnet_door(env)
        return self.create_fake_door()

    def _should_create_kasa_door(self, env: Env) -> bool:
        """Determine if a Kasa door device should be created."""
        return bool(env.kasa_device_ip)

    def _create_smart_plug_magnet_door(self, env: Env) -> DeviceDoor:
        """Create a smart plug magnet door with the appropriate smart plug."""
        try:
            self._logger.info("Creating SmartPlugMagnetDeviceDoor")
            smart_plug_factory = SmartPlugFactory(logger=self._logger)
            smart_plug = smart_plug_factory.create_from_env(env)
            return SmartPlugMagnetDeviceDoor(logger=self._logger, smart_plug=smart_plug)
        except Exception as e:
            self._logger.error(f"Failed to create smart plug magnet door: {e}")
            return self.create_fake_door()

    def create_fake_door(self) -> DeviceDoor:
        """Create a fake door device as fallback."""
        self._logger.info("Falling back to fake device door implementation")
        return FakeDeviceDoor(logger=self._logger)
