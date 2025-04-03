from src.image_classifier.impl_fake import FakeImageClassifier
from src.smart_door.smart_door import SmartDoor


def main() -> None:
    image_classifier = FakeImageClassifier()

    smart_door = SmartDoor()

    smart_door.start()

    print("Hello, World!")
