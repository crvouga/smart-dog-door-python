from typing import Optional, Dict, Any
import logging
import threading
import time
from datetime import timedelta
from src.library.smart_plug.interface import (
    SmartPlug,
    SmartPlugState,
    SmartPlugEvent,
    SmartPlugConnectedEvent,
    SmartPlugDisconnectedEvent,
    SmartPlugStateChangedEvent,
    SmartPlugPowerUsageEvent,
)
from src.library.life_cycle import LifeCycle
from src.library.pub_sub import PubSub


class FakeSmartPlug(SmartPlug, LifeCycle):
    """A fake implementation of the SmartPlug interface for testing purposes."""

    def __init__(
        self, logger: logging.Logger, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a fake smart plug.

        Args:
            logger: Logger instance
            config: Optional configuration dictionary
        """
        self._logger = logger.getChild("fake_smart_plug")
        self._config = config or {}
        self._state = SmartPlugState.UNKNOWN
        self._pub_sub = PubSub[SmartPlugEvent]()
        self._is_running = False
        self._polling_thread: Optional[threading.Thread] = None
        self._polling_interval = timedelta(
            seconds=self._config.get("polling_interval", 10.0)
        )
        self._power_usage = self._config.get("initial_power_usage", 0.0)
        self._connected = False
        self._logger.info("Initialized FakeSmartPlug")

    def start(self) -> None:
        """Start the fake smart plug."""
        self._logger.info("Starting fake smart plug")
        self._is_running = True
        self._connected = True
        self._state = SmartPlugState.OFF
        self._pub_sub.publish(SmartPlugConnectedEvent())

        # Start polling thread if configured
        if self._config.get("enable_polling", True):
            self._start_polling()

        self._logger.info("Fake smart plug started successfully")

    def stop(self) -> None:
        """Stop the fake smart plug."""
        self._logger.info("Stopping fake smart plug")
        self._is_running = False

        # Turn off the plug when stopping
        if self._connected:
            self._state = SmartPlugState.OFF
            self._connected = False
            self._pub_sub.publish(SmartPlugDisconnectedEvent())

        self._logger.info("Fake smart plug stopped")

    def turn_on(self) -> bool:
        """Turn the fake smart plug on."""
        self._logger.debug("Turning fake smart plug on")
        if not self._connected:
            self._logger.error("Cannot turn on: fake smart plug not connected")
            return False

        # Simulate occasional failures if configured
        if self._config.get("simulate_failures", False) and self._should_fail():
            self._logger.error("Simulated failure when turning on")
            return False

        self._state = SmartPlugState.ON
        self._pub_sub.publish(SmartPlugStateChangedEvent("state_changed", self._state))
        self._logger.debug("Fake smart plug turned on successfully")
        return True

    def turn_off(self) -> bool:
        """Turn the fake smart plug off."""
        self._logger.debug("Turning fake smart plug off")
        if not self._connected:
            self._logger.error("Cannot turn off: fake smart plug not connected")
            return False

        # Simulate occasional failures if configured
        if self._config.get("simulate_failures", False) and self._should_fail():
            self._logger.error("Simulated failure when turning off")
            return False

        self._state = SmartPlugState.OFF
        self._pub_sub.publish(SmartPlugStateChangedEvent("state_changed", self._state))
        self._logger.debug("Fake smart plug turned off successfully")
        return True

    def get_state(self) -> SmartPlugState:
        """Get the current state of the fake smart plug."""
        self._logger.debug(f"Getting fake smart plug state: {self._state.name}")
        return self._state

    def get_power_usage(self) -> Optional[float]:
        """Get the current power usage of the fake smart plug."""
        if not self._connected or self._state != SmartPlugState.ON:
            return 0.0

        # Return configured power usage or generate a random value
        if self._config.get("variable_power", False):
            import random

            min_power = self._config.get("min_power", 5.0)
            max_power = self._config.get("max_power", 15.0)
            self._power_usage = random.uniform(min_power, max_power)

        self._logger.debug(f"Getting fake smart plug power usage: {self._power_usage}W")
        return self._power_usage

    def is_connected(self) -> bool:
        """Check if the fake smart plug is connected."""
        return self._connected

    def events(self) -> PubSub[SmartPlugEvent]:
        """Get the event publisher for this fake smart plug."""
        return self._pub_sub

    def _start_polling(self) -> None:
        """Start the polling thread."""
        self._logger.debug("Starting polling thread")
        if self._polling_thread is None or not self._polling_thread.is_alive():
            self._polling_thread = threading.Thread(target=self._polling_loop)
            self._polling_thread.daemon = True
            self._polling_thread.start()
            self._logger.debug(
                f"Polling thread started with interval {self._polling_interval.total_seconds()} seconds"
            )

    def _polling_loop(self) -> None:
        """Polling loop to simulate device updates."""
        self._logger.debug("Entering polling loop")
        while self._is_running and self._connected:
            try:
                # Simulate state changes if configured
                if self._config.get("simulate_state_changes", False):
                    self._simulate_state_change()

                # Publish power usage events if the plug is on
                if self._state == SmartPlugState.ON and self._config.get(
                    "report_power_usage", True
                ):
                    power = self.get_power_usage()
                    if power is not None:
                        self._pub_sub.publish(
                            SmartPlugPowerUsageEvent("power_usage", power)
                        )

                time.sleep(self._polling_interval.total_seconds())
            except Exception as e:
                self._logger.error(f"Error in polling loop: {e}")
                time.sleep(1.0)  # Short delay before retrying

    def _simulate_state_change(self) -> None:
        """Simulate random state changes for testing."""
        import random

        if random.random() < 0.05:  # 5% chance of state change
            new_state = (
                SmartPlugState.OFF
                if self._state == SmartPlugState.ON
                else SmartPlugState.ON
            )
            self._logger.info(f"Simulating state change to {new_state.name}")
            self._state = new_state
            self._pub_sub.publish(
                SmartPlugStateChangedEvent("state_changed", self._state)
            )

    def _should_fail(self) -> bool:
        """Determine if an operation should fail based on configured failure rate."""
        import random

        failure_rate = self._config.get("failure_rate", 0.1)  # 10% default failure rate
        return random.random() < failure_rate
