from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, Literal
from dataclasses import dataclass, field
from src.library.pub_sub import PubSub


class SmartPlugState(Enum):
    """Represents the possible states of a smart plug."""

    ON = auto()
    OFF = auto()
    UNKNOWN = auto()


@dataclass
class SmartPlugEvent(ABC):
    """Base class for all smart plug events."""

    type: str


@dataclass
class SmartPlugConnectedEvent(SmartPlugEvent):
    """Event fired when a smart plug is connected."""

    type: Literal["connected"] = "connected"


@dataclass
class SmartPlugDisconnectedEvent(SmartPlugEvent):
    """Event fired when a smart plug is disconnected."""

    type: Literal["disconnected"] = "disconnected"


@dataclass
class SmartPlugStateChangedEvent(SmartPlugEvent):
    """Event fired when a smart plug's state changes."""

    state: SmartPlugState = field(default=SmartPlugState.UNKNOWN)
    type: Literal["state_changed"] = "state_changed"


@dataclass
class SmartPlugPowerUsageEvent(SmartPlugEvent):
    """Event fired when power usage data is available."""

    type: Literal["power_usage"] = "power_usage"
    watts: float = field(default=0.0)


class SmartPlug(ABC):
    """Interface for smart plug devices."""

    @abstractmethod
    def start(self) -> None:
        """Initialize and start the smart plug connection."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop and clean up the smart plug connection."""
        pass

    @abstractmethod
    def turn_on(self) -> bool:
        """
        Turn the smart plug on.

        Returns:
            bool: True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def turn_off(self) -> bool:
        """
        Turn the smart plug off.

        Returns:
            bool: True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_state(self) -> SmartPlugState:
        """
        Get the current state of the smart plug.

        Returns:
            SmartPlugState: The current state of the plug.
        """
        pass

    @abstractmethod
    def get_power_usage(self) -> Optional[float]:
        """
        Get the current power usage in watts.

        Returns:
            Optional[float]: Power usage in watts, or None if not available.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the smart plug is connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        pass

    @abstractmethod
    def events(self) -> PubSub[SmartPlugEvent]:
        """
        Get the event publisher for this smart plug.

        Returns:
            PubSub[SmartPlugEvent]: The event publisher.
        """
        pass
