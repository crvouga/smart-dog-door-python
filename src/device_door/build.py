from src.device_door.interface import DeviceDoor
from src.device_door.impl_fake import FakeDeviceDoor


class BuildDeviceDoor:
    @staticmethod
    def fake() -> DeviceDoor:
        return FakeDeviceDoor()
