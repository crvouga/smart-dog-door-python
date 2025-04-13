from typing import Any, Optional
import asyncio
import kasa
import kasa.discover
from src.device_door.interface import DeviceDoor
from src.device_door.event import EventDoor, EventDoorConnected, EventDoorDisconnected
from src.library.life_cycle import LifeCycle
from src.library.pub_sub import PubSub, Sub
import logging
import time
import threading


class KasaDeviceDoor(DeviceDoor, LifeCycle):
    _logger: logging.Logger
    _plug: Any
    _ip_address: str
    _is_on: bool
    _pub_sub: PubSub[EventDoor]
    _retry_interval: float = 5.0  # seconds between retries
    _is_running: bool = False
    _connection_thread: Optional[threading.Thread] = None

    def __init__(self, logger: logging.Logger, ip_address: str) -> None:
        self._logger = logger.getChild("kasa_device_door")
        self._ip_address = ip_address
        self._plug = None
        self._is_on = False
        self._pub_sub = PubSub[EventDoor]()

    def start(self) -> None:
        self._logger.info("Starting Kasa device door")
        self._is_running = True
        self._connection_thread = threading.Thread(target=self._start_connection_loop)
        self._connection_thread.daemon = True
        self._connection_thread.start()

    def _start_connection_loop(self) -> None:
        while self._is_running:
            try:
                asyncio.run(self._async_start())
                self._logger.info(
                    f"Kasa device door started, initial state: {'on' if self._is_on else 'off'}"
                )
                self._pub_sub.publish(EventDoorConnected())
                return  # Successfully connected, exit the loop
            except Exception as e:
                self._logger.error(f"Failed to start Kasa device door: {e}")
                self._logger.info(f"Retrying in {self._retry_interval} seconds...")
                time.sleep(self._retry_interval)

    async def _async_start(self) -> None:
        self._plug = await kasa.discover.Discover.discover_single(host=self._ip_address)
        if self._plug is not None:
            await self._plug.update()  # Get the latest state
            self._is_on = self._plug.is_on

    def stop(self) -> None:
        self._logger.info("Stopping Kasa device door")
        self._is_running = False
        if self._connection_thread and self._connection_thread.is_alive():
            self._connection_thread.join(timeout=1.0)
        self._pub_sub.publish(EventDoorDisconnected())
        self._plug = None

    def open(self) -> None:
        if not self._plug:
            self._logger.error("Kasa device door not started")
            return

        try:
            asyncio.run(self._async_open())
            self._logger.info("Kasa device door opened")
        except Exception as e:
            self._logger.error(f"Failed to open Kasa device door: {e}")
            # Don't raise, just log the error

    async def _async_open(self) -> None:
        if self._plug is not None:
            try:
                await self._plug.turn_on()
                self._is_on = True
            except Exception as e:
                self._logger.error(f"Communication error on open: {e}")
                raise

    def close(self) -> None:
        if not self._plug:
            self._logger.error("Kasa device door not started")
            return

        try:
            asyncio.run(self._async_close())
            self._logger.info("Kasa device door closed")
        except Exception as e:
            self._logger.error(f"Failed to close Kasa device door: {e}")
            # Don't raise, just log the error

    async def _async_close(self) -> None:
        if self._plug is not None:
            try:
                await self._plug.turn_off()
                self._is_on = False
            except Exception as e:
                self._logger.error(f"Communication error on close: {e}")
                raise

    def is_open(self) -> bool:
        if not self._plug:
            self._logger.error("Kasa device door not started")
            return False

        try:
            return asyncio.run(self._async_is_open())
        except Exception as e:
            self._logger.error(f"Failed to get Kasa device door state: {e}")
            return False

    async def _async_is_open(self) -> bool:
        if self._plug is not None:
            try:
                await self._plug.update()  # Get the latest state
                self._is_on = self._plug.is_on
            except Exception as e:
                self._logger.error(f"Communication error on status check: {e}")
                raise
        return self._is_on

    def events(self) -> Sub[EventDoor]:
        return self._pub_sub
