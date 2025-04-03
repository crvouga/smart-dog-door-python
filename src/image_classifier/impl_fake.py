from src.image.image import Image
from src.image_classifier.classification import Classification
from src.image_classifier.interface import ImageClassifier


class ImageClassifierFake(ImageClassifier):
    def classify(self, image: list[Image]) -> list[Classification]:
        return [Classification(label="fake", weight=0.5)]
