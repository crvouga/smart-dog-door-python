from src.image.image import Image
from src.image_classifier.classification import Classification
from src.image_classifier.interface import ImageClassifier


class FakeImageClassifier(ImageClassifier):
    def classify(self, images: list[Image]) -> list[Classification]:
        return [Classification(label="fake", weight=0.5)]
