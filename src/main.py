from src.image_classifier.impl_fake import FakeImageClassifier
from src.smart_door.smart_door import SmartDoor
from src.device_camera.impl_fake import FakeDeviceCamera
from src.device_door.impl_fake import FakeDeviceDoor


def main() -> None:
    image_classifier = FakeImageClassifier()
    device_door = FakeDeviceDoor()
    device_camera = FakeDeviceCamera()

    smart_door = SmartDoor()

    smart_door.start()

    print("Hello, World!")
