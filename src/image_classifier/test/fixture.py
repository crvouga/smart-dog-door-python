from src.image_classifier.build import BuildImageClassifier
from src.image_classifier.interface import ImageClassifier


class Fixture:
    image_classifier: ImageClassifier

    def __init__(self) -> None:
        self.image_classifier = BuildImageClassifier.yolo_large()
