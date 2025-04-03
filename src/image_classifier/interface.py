from abc import ABC, abstractmethod
from src.image.image import Image
from src.image_classifier.classification import Classification


class ImageClassifier(ABC):
    @abstractmethod
    def classify(self, image: list[Image]) -> list[Classification]:
        pass
