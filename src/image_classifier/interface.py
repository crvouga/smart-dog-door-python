from abc import ABC, abstractmethod
from image.image import Image
from image_classifier.classification import Classification


class ImageClassifier(ABC):
    @abstractmethod
    def classify(self, image: list[Image]) -> list[Classification]:
        pass
