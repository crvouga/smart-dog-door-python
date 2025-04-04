from abc import ABC, abstractmethod


class LifeCycle(ABC):
    """Interface for components with explicit start and stop phases."""

    @abstractmethod
    def start(self) -> None:
        """Starts the component's operation."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stops the component's operation and cleans up resources."""
        pass
