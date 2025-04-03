from src.image_classifier.impl_fake import FakeImageClassifier


def main() -> None:
    image_classifier = FakeImageClassifier()

    image_classifier.classify([])

    print("Hello, World!")
