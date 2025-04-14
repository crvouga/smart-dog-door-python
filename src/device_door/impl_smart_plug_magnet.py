from typing import Optional
from src.device_door.interface import DeviceDoor
from src.device_door.event import (
    EventDoor,
    EventDoorConnected,
    EventDoorDisconnected,
    EventDoorOpened,
    EventDoorClosed,
)
from src.library.pub_sub import PubSub, Sub
import logging
import time
import threading
from src.library.smart_plug.interface import (
    SmartPlug,
    SmartPlugConnectedEvent,
    SmartPlugDisconnectedEvent,
    SmartPlugStateChangedEvent,
    SmartPlugState,
)


class SmartPlugMagnetDeviceDoor(DeviceDoor):
    """
    Implementation of DeviceDoor using a smart plug to control a magnetic door lock.
    When the plug is ON, the door is CLOSED (magnet engaged).
    When the plug is OFF, the door is OPEN (magnet disengaged).
    """

    _logger: logging.Logger
    _smart_plug: SmartPlug
    _pub_sub: PubSub[EventDoor]
    _is_running: bool = False
    _event_handler: Optional[threading.Thread] = None

    def __init__(self, logger: logging.Logger, smart_plug: SmartPlug) -> None:
        self._logger = logger.getChild("smart_plug_magnet_door")
        self._smart_plug = smart_plug
        self._pub_sub = PubSub[EventDoor]()
        self._logger.info("Initialized SmartPlugMagnetDeviceDoor")

    def start(self) -> None:
        """Start the smart plug magnet door device."""
        self._logger.info("Starting smart plug magnet door")
        self._is_running = True

        # Start the smart plug
        self._smart_plug.start()

        # Set initial state to closed (ON) for safety
        self._logger.info("Setting initial door state to closed")
        try:
            self.close()
        except Exception as e:
            self._logger.error(f"Failed to set initial door state: {e}")

        # Start event handler thread
        self._event_handler = threading.Thread(target=self._handle_smart_plug_events)
        self._event_handler.daemon = True
        self._event_handler.start()

        self._logger.info("Smart plug magnet door started")

    def stop(self) -> None:
        """Stop the smart plug magnet door device."""
        self._logger.info("Stopping smart plug magnet door")
        self._is_running = False

        # Close the door before stopping
        try:
            self.close()
        except Exception as e:
            self._logger.error(f"Error closing door during shutdown: {e}")

        # Stop the smart plug
        self._smart_plug.stop()
        self._logger.info("Smart plug magnet door stopped")

    def open(self) -> None:
        """Open the door by turning the smart plug OFF."""
        self._logger.info("Opening door (turning smart plug OFF)")
        if not self._smart_plug.turn_off():
            self._logger.error("Failed to open door - could not turn smart plug off")
            raise RuntimeError("Failed to open door")
        self._logger.info("Door opened successfully")
        self._pub_sub.publish(EventDoorOpened())

    def close(self) -> None:
        """Close the door by turning the smart plug ON."""
        self._logger.info("Closing door (turning smart plug ON)")
        if not self._smart_plug.turn_on():
            self._logger.error("Failed to close door - could not turn smart plug on")
            raise RuntimeError("Failed to close door")
        self._logger.info("Door closed successfully")
        self._pub_sub.publish(EventDoorClosed())

    def events(self) -> Sub[EventDoor]:
        """Get the event subscriber for this door."""
        return self._pub_sub

    def _handle_smart_plug_events(self) -> None:
        """Handle events from the smart plug and translate them to door events."""
        self._logger.debug("Starting smart plug event handler")

        # Subscribe to smart plug events
        smart_plug_events = self._smart_plug.events()

        # Create an observer function to handle events
        def observer(event):
            self._handle_event(event)

        unsubscribe = smart_plug_events.subscribe(observer)

        try:
            # Just wait until the component is stopped
            while self._is_running:
                time.sleep(1.0)
        finally:
            unsubscribe()
            self._logger.debug("Smart plug event handler stopped")

    def _handle_event(self, event) -> None:
        """Process a single smart plug event."""
        if isinstance(event, SmartPlugConnectedEvent):
            self._logger.info("Smart plug connected")
            self._pub_sub.publish(EventDoorConnected())
        elif isinstance(event, SmartPlugDisconnectedEvent):
            self._logger.info("Smart plug disconnected")
            self._pub_sub.publish(EventDoorDisconnected())
        elif isinstance(event, SmartPlugStateChangedEvent):
            self._logger.info(f"Smart plug state changed to {event.state.name}")
            # Update internal state based on the smart plug state
            if event.state == SmartPlugState.ON:
                self._logger.debug("Door is now CLOSED due to smart plug state change")
                self._pub_sub.publish(EventDoorClosed())
            elif event.state == SmartPlugState.OFF:
                self._logger.debug("Door is now OPEN due to smart plug state change")
                self._pub_sub.publish(EventDoorOpened())
            elif event.state == SmartPlugState.UNKNOWN:
                self._logger.warning(
                    "Door state is now UNKNOWN due to smart plug state change"
                )
