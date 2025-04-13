import pytest
import threading
import time
from datetime import timedelta
from logging import Logger
from typing import Optional, List

from src.device_camera.with_retry import WithRetry
from src.device_camera.impl_fake import FakeDeviceCamera
from src.device_camera.interface import DeviceCamera
from src.device_camera.event import EventCameraConnected, EventCameraDisconnected
from src.image.image import Image


class MockTimeProvider:
    def __init__(self):
        self.sleep_calls = []
        self.event = threading.Event()
        self._sleep_time = 0.0

    def sleep(self, seconds: float) -> None:
        self.sleep_calls.append(seconds)
        self._sleep_time += seconds
        self.event.set()  # Signal that sleep was called

    def get_total_sleep_time(self) -> float:
        return self._sleep_time


class Fixture:
    def __init__(
        self,
        should_fail_connection: bool = False,
        should_fail_frames: bool = False,
        retry_interval: float = 0.1,
    ) -> None:
        self.logger = Logger("test")
        self.mock_time_provider = MockTimeProvider()
        self.fake_camera = FakeDeviceCamera(
            logger=self.logger,
            should_fail_connection=should_fail_connection,
            should_fail_frames=should_fail_frames,
        )
        self.camera_with_retry = WithRetry(
            wrapped=self.fake_camera,
            logger=self.logger,
            retry_interval=retry_interval,
            time_sleep=self.mock_time_provider.sleep,
        )


def test_failed_connection_retry():
    # Test that the camera retries when connection fails
    fixture = Fixture(should_fail_connection=True)
    fixture.camera_with_retry.start()

    # Give the thread time to run
    time.sleep(0.2)

    # Verify retry was attempted
    assert len(fixture.mock_time_provider.sleep_calls) > 0
    assert fixture.camera_with_retry.is_connected() is False

    # Clean up
    fixture.camera_with_retry.stop()


def test_events_subscription():
    # Test that events are properly propagated
    fixture = Fixture()

    # Set up event tracking
    events_received = []

    def on_event(event):
        events_received.append(event)

    # Subscribe to events
    fixture.camera_with_retry.events().subscribe(on_event)

    # Start the camera
    fixture.camera_with_retry.start()

    # Give the thread time to run
    time.sleep(0.2)

    # Should have received a connected event
    assert len(events_received) > 0
    assert any(isinstance(event, EventCameraConnected) for event in events_received)

    # Clean up
    fixture.camera_with_retry.stop()


def test_stop_when_already_stopped():
    # Test stopping when already stopped
    fixture = Fixture()

    # Camera starts in stopped state
    fixture.camera_with_retry.stop()  # Should not raise any exceptions


def test_start_when_already_started():
    # Test starting when already started
    fixture = Fixture()
    fixture.camera_with_retry.start()

    # Give the thread time to run
    time.sleep(0.1)

    # Start again should not create a new thread
    fixture.camera_with_retry.start()

    # Clean up
    fixture.camera_with_retry.stop()


def test_retry_interval_respected():
    # Test that the retry interval is respected
    fixture = Fixture(should_fail_connection=True, retry_interval=0.25)
    fixture.camera_with_retry.start()

    # Wait for at least one retry
    fixture.mock_time_provider.event.wait(timeout=1.0)

    # Verify the retry interval was used
    assert len(fixture.mock_time_provider.sleep_calls) > 0
    assert fixture.mock_time_provider.sleep_calls[0] == 0.25

    # Clean up
    fixture.camera_with_retry.stop()
