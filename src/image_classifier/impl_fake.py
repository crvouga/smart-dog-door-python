from src.image.image import Image
from src.library.bounding_box import BoundingBox
from src.image_classifier.classification import Classification
from src.image_classifier.interface import ImageClassifier


class FakeImageClassifier(ImageClassifier):
    def classify(self, images: list[Image]) -> list[Classification]:

        return [
            Classification(
                label="fake",
                weight=0.5,
                bounding_box=BoundingBox(x_min=0, y_min=0, x_max=1, y_max=1),
            )
        ]
