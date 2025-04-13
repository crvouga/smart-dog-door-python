import pytest
import time
from logging import Logger
from typing import List

from src.device_camera.interface import DeviceCamera
from src.device_camera.impl_fake import FakeDeviceCamera
from src.device_camera.event import EventCamera
from src.image.image import Image


class Fixture:
    def __init__(self) -> None:
        self.logger = Logger("test")
        self.camera: DeviceCamera = FakeDeviceCamera(logger=self.logger)


def test_capture_returns_non_empty_list():
    # Test that the camera capture method returns a non-empty list of images
    fixture = Fixture()

    # Start the camera
    fixture.camera.start()

    # Give the camera time to initialize
    time.sleep(0.1)

    # Verify camera is connected
    assert fixture.camera.is_connected() is True

    # Capture images
    images = fixture.camera.capture()

    # Verify we got a non-empty list of images
    assert isinstance(images, list)
    assert len(images) > 0
    assert all(isinstance(image, Image) for image in images)

    # Clean up
    fixture.camera.stop()
