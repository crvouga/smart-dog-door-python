from src.image_classifier.impl_yolo import YoloImageClassifier, YoloModelSize
from src.image_classifier.interface import ImageClassifier
from src.image_classifier.impl_fake import FakeImageClassifier


class BuildImageClassifier:
    @staticmethod
    def fake() -> ImageClassifier:
        return FakeImageClassifier()

    @staticmethod
    def yolo_nano() -> ImageClassifier:
        return YoloImageClassifier(model_size=YoloModelSize.NANO)

    @staticmethod
    def yolo_small() -> ImageClassifier:
        return YoloImageClassifier(model_size=YoloModelSize.SMALL)

    @staticmethod
    def yolo_medium() -> ImageClassifier:
        return YoloImageClassifier(model_size=YoloModelSize.MEDIUM)

    @staticmethod
    def yolo_large() -> ImageClassifier:
        return YoloImageClassifier(model_size=YoloModelSize.LARGE)

    @staticmethod
    def yolo_extra_large() -> ImageClassifier:
        return YoloImageClassifier(model_size=YoloModelSize.EXTRA_LARGE)
