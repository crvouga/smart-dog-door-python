from abc import ABC, abstractmethod
from src.image.image import Image
from src.image_classifier.classification import Classification
from typing import Iterator


class ImageClassifier(ABC):
    @abstractmethod
    def classify(self, images: list[Image]) -> Iterator[Classification]:
        pass
