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
from datetime import timedelta


class KasaDeviceDoor(DeviceDoor, LifeCycle):
    _logger: logging.Logger
    _plug: Any
    _ip_address: str
    _is_on: bool
    _pub_sub: PubSub[EventDoor]
    _retry_interval: timedelta = timedelta(seconds=5.0)
    _is_running: bool = False
    _connection_thread: Optional[threading.Thread] = None
    _polling_thread: Optional[threading.Thread] = None
    _polling_interval: timedelta = timedelta(seconds=10.0)
    _max_retries: int = 3
    _retry_delay: timedelta = timedelta(seconds=1.0)

    def __init__(self, logger: logging.Logger, ip_address: str) -> None:
        self._logger = logger.getChild("kasa_device_door")
        self._ip_address = ip_address
        self._plug = None
        self._is_on = False
        self._pub_sub = PubSub[EventDoor]()
        self._logger.info(f"Initialized KasaDeviceDoor with IP: {ip_address}")

    def start(self) -> None:
        self._logger.info("Starting Kasa device door")
        self._is_running = True
        self._connection_thread = self._create_thread(self._start_connection_loop)
        self._connection_thread.start()
        self._logger.debug("Connection thread started")

    def _create_thread(self, target_func) -> threading.Thread:
        thread = threading.Thread(target=target_func)
        thread.daemon = True
        return thread

    def _start_connection_loop(self) -> None:
        self._logger.debug("Entering connection loop")
        while self._is_running:
            try:
                self._logger.debug(
                    f"Attempting to connect to Kasa device at {self._ip_address}"
                )
                asyncio.run(self._async_start())
                self._logger.info(
                    f"Kasa device door started, initial state: {'closed' if self._is_on else 'open'}"
                )
                self._pub_sub.publish(EventDoorConnected())
                self._logger.debug("Published EventDoorConnected")
                self._start_polling()
                return
            except Exception as e:
                self._logger.error(f"Failed to start Kasa device door: {e}")
                self._logger.info(
                    f"Retrying in {self._retry_interval.total_seconds()} seconds..."
                )
                time.sleep(self._retry_interval.total_seconds())

    def _start_polling(self) -> None:
        self._logger.debug("Starting polling mechanism")
        if self._polling_thread is None or not self._polling_thread.is_alive():
            self._polling_thread = self._create_thread(self._polling_loop)
            self._polling_thread.start()
            self._logger.info(
                f"Started state polling every {self._polling_interval.total_seconds()} seconds"
            )

    def _polling_loop(self) -> None:
        self._logger.debug("Entering polling loop")
        while self._is_running and self._plug is not None:
            try:
                self._logger.debug("Polling current device state")
                previous_state = self._is_on
                current_state = asyncio.run(self._async_is_open())
                self._logger.debug(
                    f"Poll result: device is {'open' if current_state else 'closed'}"
                )

                if previous_state != current_state:
                    self._logger.info(
                        f"Door state changed: {'open' if current_state else 'closed'}"
                    )

                time.sleep(self._polling_interval.total_seconds())
            except Exception as e:
                self._logger.error(f"Error during state polling: {e}")
                self._logger.debug(
                    f"Will retry polling in {self._retry_interval.total_seconds()} seconds"
                )
                time.sleep(self._retry_interval.total_seconds())

    async def _async_start(self) -> None:
        self._logger.debug(f"Discovering Kasa device at {self._ip_address}")
        self._plug = await kasa.discover.Discover.discover_single(host=self._ip_address)
        if self._plug is not None:
            self._logger.debug(f"Device discovered: {self._plug}")
            await self._plug.update()
            self._is_on = self._plug.is_on
            self._logger.debug(
                f"Initial device state: {'closed' if self._is_on else 'open'}"
            )
        else:
            self._logger.warning(f"No device found at {self._ip_address}")

    def stop(self) -> None:
        self._logger.info("Stopping Kasa device door")
        self._is_running = False
        self._join_thread(self._connection_thread)
        self._join_thread(self._polling_thread)
        self._logger.debug("Publishing EventDoorDisconnected")
        self._pub_sub.publish(EventDoorDisconnected())
        self._plug = None
        self._logger.debug("Kasa device door stopped")

    def _join_thread(self, thread: Optional[threading.Thread]) -> None:
        if thread and thread.is_alive():
            self._logger.debug(f"Waiting for thread to terminate")
            thread.join(timeout=1.0)

    def open(self) -> None:
        self._execute_door_operation("open", self._async_open)

    def close(self) -> None:
        self._execute_door_operation("close", self._async_close)

    def _execute_door_operation(self, operation: str, async_func) -> None:
        self._logger.debug(f"Attempting to {operation} door")
        if not self._plug:
            self._logger.error("Kasa device door not started")
            return

        for attempt in range(self._max_retries):
            try:
                self._logger.debug(
                    f"{operation.capitalize()} attempt {attempt+1}/{self._max_retries}"
                )
                asyncio.run(async_func())
                self._logger.info(f"Kasa device door {operation}ed")
                return
            except Exception as e:
                self._logger.error(
                    f"Failed to {operation} Kasa device door (attempt {attempt+1}/{self._max_retries}): {e}"
                )
                if attempt < self._max_retries - 1:
                    self._logger.debug(
                        f"Retrying {operation} in {self._retry_delay.total_seconds()} seconds"
                    )
                    time.sleep(self._retry_delay.total_seconds())

    async def _async_open(self) -> None:
        await self._async_toggle(False, "open")

    async def _async_close(self) -> None:
        await self._async_toggle(True, "close")

    async def _async_toggle(self, turn_on: bool, operation: str) -> None:
        if self._plug is not None:
            try:
                self._logger.debug(
                    f"Sending turn_{'on' if turn_on else 'off'} command to device"
                )
                if turn_on:
                    await self._plug.turn_on()
                else:
                    await self._plug.turn_off()
                self._is_on = turn_on
                self._logger.debug(
                    f"Device turned {'on' if turn_on else 'off'} successfully"
                )
            except Exception as e:
                self._logger.error(f"Communication error on {operation}: {e}")
                raise

    def is_open(self) -> bool:
        self._logger.debug("Checking if door is open")
        if not self._plug:
            self._logger.error("Kasa device door not started")
            return False

        for attempt in range(self._max_retries):
            try:
                self._logger.debug(
                    f"Status check attempt {attempt+1}/{self._max_retries}"
                )
                result = asyncio.run(self._async_is_open())
                self._logger.debug(f"Door is {'open' if result else 'closed'}")
                return result
            except Exception as e:
                self._logger.error(
                    f"Failed to get Kasa device door state (attempt {attempt+1}/{self._max_retries}): {e}"
                )
                if attempt < self._max_retries - 1:
                    self._logger.debug(
                        f"Retrying status check in {self._retry_delay.total_seconds()} seconds"
                    )
                    time.sleep(self._retry_delay.total_seconds())

        self._logger.warning("All status check attempts failed, defaulting to closed")
        return False

    async def _async_is_open(self) -> bool:
        if self._plug is not None:
            try:
                self._logger.debug("Updating device state")
                await self._plug.update()
                self._is_on = self._plug.is_on
                self._logger.debug(
                    f"Updated device state: {'closed' if self._is_on else 'open'}"
                )
            except Exception as e:
                self._logger.error(f"Communication error on status check: {e}")
                raise
        return not self._is_on

    def events(self) -> Sub[EventDoor]:
        return self._pub_sub
