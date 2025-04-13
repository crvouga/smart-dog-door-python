import logging
from typing import Dict, Any, Optional
from src.library.smart_plug.interface import SmartPlug
from src.library.smart_plug.impl_fake import FakeSmartPlug
from src.library.smart_plug.impl_kasa import KasaSmartPlug
from src.env import Env


class SmartPlugFactory:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild("smart_plug_factory")

    def create_from_env(self, env: Env) -> SmartPlug:
        """Factory method to create the appropriate smart plug based on environment configuration."""
        if self._should_create_kasa_plug(env):
            return self._create_kasa_plug(env.kasa_device_ip)
        return self.create_fake_plug()

    def _should_create_kasa_plug(self, env: Env) -> bool:
        """Determine if a Kasa smart plug should be created."""
        return bool(env.kasa_device_ip)

    def _create_kasa_plug(self, ip_address: str) -> SmartPlug:
        """Create a Kasa smart plug with the given IP address."""
        try:
            self._logger.info(f"Creating Kasa smart plug with IP: {ip_address}")
            return KasaSmartPlug(logger=self._logger, ip_address=ip_address)
        except Exception as e:
            self._logger.error(f"Failed to create Kasa smart plug: {e}")
            return self.create_fake_plug()

    def create_fake_plug(self, config: Optional[Dict[str, Any]] = None) -> SmartPlug:
        """Create a fake smart plug as fallback."""
        self._logger.info("Falling back to fake smart plug implementation")
        return FakeSmartPlug(logger=self._logger, config=config)
