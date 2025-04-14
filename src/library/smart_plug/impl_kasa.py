from typing import Any, Optional
import asyncio
import kasa
import kasa.discover
from src.library.smart_plug.interface import (
    SmartPlug,
    SmartPlugState,
    SmartPlugEvent,
    SmartPlugConnectedEvent,
    SmartPlugDisconnectedEvent,
    SmartPlugStateChangedEvent,
)
from src.library.life_cycle import LifeCycle
from src.library.pub_sub import PubSub
import logging
import time
import threading
from datetime import timedelta


class KasaSmartPlug(SmartPlug, LifeCycle):
    _logger: logging.Logger
    _plug: Any
    _ip_address: str
    _state: SmartPlugState
    _pub_sub: PubSub[SmartPlugEvent]
    _retry_interval: timedelta = timedelta(seconds=5.0)
    _is_running: bool = False
    _connection_thread: Optional[threading.Thread] = None
    _polling_thread: Optional[threading.Thread] = None
    _polling_interval: timedelta = timedelta(seconds=1.0)
    _max_retries: int = 3
    _retry_delay: timedelta = timedelta(seconds=1.0)
    _event_loop: Optional[asyncio.AbstractEventLoop] = None
    _connection_event: threading.Event = threading.Event()

    def __init__(self, logger: logging.Logger, ip_address: str) -> None:
        self._logger = logger.getChild("kasa_smart_plug")
        self._ip_address = ip_address
        self._plug = None
        self._state = SmartPlugState.UNKNOWN
        self._pub_sub = PubSub[SmartPlugEvent]()
        self._connection_event.clear()
        self._logger.info(f"Initialized KasaSmartPlug with IP: {ip_address}")

    def start(self) -> None:
        self._logger.info("Starting Kasa smart plug")
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
                # Create a new event loop for this thread
                self._event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._event_loop)
                self._event_loop.run_until_complete(self._async_start())
                self._logger.info(
                    f"Kasa smart plug started, initial state: {self._state.name}"
                )
                self._pub_sub.publish(SmartPlugConnectedEvent())
                self._logger.debug("Published SmartPlugConnectedEvent")
                self._connection_event.set()  # Signal that connection is established
                self._start_polling()
                return
            except Exception as e:
                self._logger.error(f"Failed to start Kasa smart plug: {e}")
                self._logger.info(
                    f"Retrying in {self._retry_interval.total_seconds()} seconds..."
                )
                time.sleep(self._retry_interval.total_seconds())
            finally:
                # Clean up the event loop
                if self._event_loop and not self._event_loop.is_closed():
                    self._event_loop.close()

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
        # Create a new event loop for this thread
        polling_event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(polling_event_loop)

        try:
            while self._is_running and self._plug is not None:
                try:
                    self._logger.debug("Polling current device state")
                    previous_state = self._state

                    # Create a new event loop for each poll to avoid closed loop issues
                    poll_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(poll_loop)
                    current_state = self.get_state()
                    poll_loop.close()

                    self._logger.debug(
                        f"Poll result: device state is {current_state.name}"
                    )

                    if previous_state != current_state:
                        self._logger.info(f"Plug state changed: {current_state.name}")
                        self._pub_sub.publish(
                            SmartPlugStateChangedEvent("state_changed", current_state)
                        )
                        # Update local state to match physical state
                        self._state = current_state

                    time.sleep(self._polling_interval.total_seconds())
                except Exception as e:
                    self._logger.error(f"Error during state polling: {e}")
                    self._logger.debug(
                        f"Will retry polling in {self._retry_interval.total_seconds()} seconds"
                    )
                    time.sleep(self._retry_interval.total_seconds())
        finally:
            # Clean up the event loop
            if not polling_event_loop.is_closed():
                polling_event_loop.close()

    async def _async_start(self) -> None:
        self._logger.debug(f"Discovering Kasa device at {self._ip_address}")
        self._plug = await kasa.discover.Discover.discover_single(host=self._ip_address)
        if self._plug is not None:
            self._logger.debug(f"Device discovered: {self._plug}")
            await self._plug.update()
            self._update_state_from_plug()
            self._logger.debug(f"Initial device state: {self._state.name}")
            # Sync the physical device state with our local state
            await self._sync_device_with_local_state()
        else:
            self._logger.warning(f"No device found at {self._ip_address}")

    def _update_state_from_plug(self) -> None:
        if self._plug is not None:
            self._state = SmartPlugState.ON if self._plug.is_on else SmartPlugState.OFF
        else:
            self._state = SmartPlugState.UNKNOWN

    async def _sync_device_with_local_state(self) -> None:
        """Ensure the physical device state matches our local state."""
        if self._plug is not None:
            try:
                current_device_state = (
                    SmartPlugState.ON if self._plug.is_on else SmartPlugState.OFF
                )
                if current_device_state != self._state:
                    self._logger.info(
                        f"Syncing device state to match local state: {self._state.name}"
                    )
                    if self._state == SmartPlugState.ON:
                        await self._plug.turn_on()
                    else:
                        await self._plug.turn_off()
                    self._logger.debug("Device state synchronized successfully")
                else:
                    self._logger.debug("Device state already in sync with local state")
            except Exception as e:
                self._logger.error(f"Failed to sync device state: {e}")

    def stop(self) -> None:
        self._logger.info("Stopping Kasa smart plug")
        self._is_running = False
        self._connection_event.clear()

        # Turn off the plug when stopping
        if self._plug is not None:
            try:
                self._logger.info("Turning off plug before disconnecting")
                # Create a new event loop for shutdown
                shutdown_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(shutdown_loop)
                shutdown_loop.run_until_complete(self._turn_off_plug())
                shutdown_loop.close()
                self._logger.debug("Plug turned off successfully")
            except Exception as e:
                self._logger.error(f"Failed to turn off plug during shutdown: {e}")

        self._join_thread(self._polling_thread)
        self._join_thread(self._connection_thread)

        self._logger.debug("Publishing SmartPlugDisconnectedEvent")
        self._pub_sub.publish(SmartPlugDisconnectedEvent())
        self._plug = None
        self._state = SmartPlugState.UNKNOWN
        self._logger.debug("Kasa smart plug stopped")

    async def _turn_off_plug(self) -> None:
        """Turn off the plug during shutdown."""
        if self._plug is not None:
            try:
                await self._plug.update()
                if self._plug.is_on:
                    await self._plug.turn_off()
                    self._state = SmartPlugState.OFF
            except Exception as e:
                self._logger.error(f"Error turning off plug: {e}")
                # Don't re-raise to avoid breaking the shutdown process

    def _join_thread(self, thread: Optional[threading.Thread]) -> None:
        if thread and thread.is_alive():
            self._logger.debug(f"Waiting for thread to terminate")
            try:
                thread.join(timeout=1.0)
                if thread.is_alive():
                    self._logger.warning("Thread did not terminate within timeout")
            except Exception as e:
                self._logger.error(f"Error joining thread: {e}")

    def turn_on(self) -> bool:
        # Wait for the device to be connected before attempting to turn it on
        if not self._connection_event.is_set():
            self._logger.info("Waiting for device to connect before turning on...")
            # Wait with a timeout to avoid hanging indefinitely
            connected = self._connection_event.wait(timeout=30.0)
            if not connected:
                self._logger.error("Timed out waiting for device connection")
                return False
            self._logger.info("Device connected, proceeding with turn on operation")

        return self._execute_plug_operation("turn_on", self._async_turn_on)

    def turn_off(self) -> bool:
        # Wait for the device to be connected before attempting to turn it off
        if not self._connection_event.is_set():
            self._logger.info("Waiting for device to connect before turning off...")
            # Wait with a timeout to avoid hanging indefinitely
            connected = self._connection_event.wait(timeout=30.0)
            if not connected:
                self._logger.error("Timed out waiting for device connection")
                return False
            self._logger.info("Device connected, proceeding with turn off operation")

        return self._execute_plug_operation("turn_off", self._async_turn_off)

    def _execute_plug_operation(self, operation: str, async_func) -> bool:
        self._logger.debug(f"Attempting to {operation}")
        if not self._plug:
            self._logger.error("Kasa smart plug not started")
            return False

        for attempt in range(self._max_retries):
            try:
                self._logger.debug(
                    f"{operation.capitalize()} attempt {attempt+1}/{self._max_retries}"
                )
                # Create a new event loop for this operation
                operation_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(operation_loop)
                operation_loop.run_until_complete(async_func())
                operation_loop.close()
                self._logger.info(f"Kasa smart plug {operation} successful")
                return True
            except Exception as e:
                self._logger.error(
                    f"Failed to {operation} Kasa smart plug (attempt {attempt+1}/{self._max_retries}): {e}"
                )
                if attempt < self._max_retries - 1:
                    self._logger.debug(
                        f"Retrying {operation} in {self._retry_delay.total_seconds()} seconds"
                    )
                    time.sleep(self._retry_delay.total_seconds())

        return False

    async def _async_turn_on(self) -> None:
        await self._async_toggle(True, "turn_on")

    async def _async_turn_off(self) -> None:
        await self._async_toggle(False, "turn_off")

    async def _async_toggle(self, turn_on: bool, operation: str) -> None:
        if self._plug is not None:
            try:
                self._logger.debug(
                    f"Sending turn_{'on' if turn_on else 'off'} command to device"
                )
                if turn_on:
                    await self._plug.turn_on()
                    self._state = SmartPlugState.ON
                else:
                    await self._plug.turn_off()
                    self._state = SmartPlugState.OFF
                self._logger.debug(
                    f"Device turned {'on' if turn_on else 'off'} successfully"
                )
                self._pub_sub.publish(
                    SmartPlugStateChangedEvent("state_changed", self._state)
                )
            except Exception as e:
                self._logger.error(f"Communication error on {operation}: {e}")
                raise

    def get_state(self) -> SmartPlugState:
        self._logger.debug("Checking plug state")
        if not self._plug:
            self._logger.error("Kasa smart plug not started")
            return SmartPlugState.UNKNOWN

        for attempt in range(self._max_retries):
            try:
                self._logger.debug(
                    f"Status check attempt {attempt+1}/{self._max_retries}"
                )
                # Create a new event loop for this status check
                status_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(status_loop)
                status_loop.run_until_complete(self._async_update_state())
                status_loop.close()
                self._logger.debug(f"Plug state is {self._state.name}")
                return self._state
            except Exception as e:
                self._logger.error(f"Communication error on status check: {e}")
                self._logger.error(
                    f"Failed to get Kasa smart plug state (attempt {attempt+1}/{self._max_retries}): {e}"
                )
                if attempt < self._max_retries - 1:
                    self._logger.debug(
                        f"Retrying status check in {self._retry_delay.total_seconds()} seconds"
                    )
                    time.sleep(self._retry_delay.total_seconds())

        self._logger.warning(
            "All status check attempts failed, returning last known state"
        )
        return self._state  # Return last known state instead of UNKNOWN

    async def _async_update_state(self) -> None:
        if self._plug is not None:
            try:
                self._logger.debug("Updating device state")
                await self._plug.update()
                self._update_state_from_plug()
                self._logger.debug(f"Updated device state: {self._state.name}")
            except Exception as e:
                # self._logger.error(f"Communication error on status check: {e}")
                # Don't raise the exception, just log it and keep the current state
                pass

    def get_power_usage(self) -> Optional[float]:
        if not self._plug or not self.is_connected():
            return None

        try:
            # This is a simplified implementation - actual implementation would depend
            # on the specific Kasa device capabilities
            if hasattr(self._plug, "emeter"):
                # Create a new event loop for power usage check
                power_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(power_loop)
                result = power_loop.run_until_complete(self._async_get_power_usage())
                power_loop.close()
                return result
            else:
                self._logger.debug("This Kasa device doesn't support power monitoring")
                return None
        except Exception as e:
            self._logger.error(f"Failed to get power usage: {e}")
            return None

    async def _async_get_power_usage(self) -> Optional[float]:
        if self._plug is not None and hasattr(self._plug, "emeter"):
            await self._plug.update()
            emeter_data = await self._plug.emeter.get_realtime()
            if "power" in emeter_data:
                return float(emeter_data["power"])
        return None

    def is_connected(self) -> bool:
        return self._plug is not None and self._state != SmartPlugState.UNKNOWN

    def events(self) -> PubSub[SmartPlugEvent]:
        return self._pub_sub
