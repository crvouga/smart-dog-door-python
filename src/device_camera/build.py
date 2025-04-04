from src.device_camera.interface import DeviceCamera
from src.device_camera.impl_fake import FakeDeviceCamera


class BuildDeviceCamera:
    @staticmethod
    def fake() -> DeviceCamera:
        return FakeDeviceCamera()
