from src.image_classifier.impl_fake import FakeImageClassifier
from src.image_classifier.impl_yolo import YoloImageClassifier, YoloModelSize
from src.image_classifier.interface import ImageClassifier


class Fixture:
    image_classifier: ImageClassifier

    def __init__(self) -> None:
        self.image_classifier = FakeImageClassifier()
        self.image_classifier = YoloImageClassifier(
            model_size=YoloModelSize.EXTRA_LARGE,
            confidence_threshold=0.25,
        )
