from ultralytics import YOLO  # type: ignore
from src.image.image import Image
from .interface import ImageClassifier, Classification
from enum import Enum


class YoloModelSize(Enum):
    NANO = "n"
    SMALL = "s"
    MEDIUM = "m"
    LARGE = "l"
    EXTRA_LARGE = "x"

    @classmethod
    def to_filename(cls, value: str) -> str:
        return f"./models/yolov8{value}.pt"


class YoloImageClassifier(ImageClassifier):
    def __init__(
        self,
        model_size: YoloModelSize = YoloModelSize.NANO,
        confidence_threshold: float = 0.25,
    ) -> None:
        """
        Initialize the YOLO classifier.

        Args:
            model_size: Size of YOLO model (NANO, SMALL, MEDIUM, LARGE, EXTRA_LARGE)
            confidence_threshold: Minimum confidence threshold for detections
        """
        filename = YoloModelSize.to_filename(model_size.value)
        self.model = YOLO(filename)
        self.confidence_threshold = confidence_threshold
        # COCO dataset class indices
        self.class_indices = {"cat": 15, "dog": 16}

    def classify(self, images: list[Image]) -> list[Classification]:
        """
        Classify the images using YOLOv8.

        Args:
            images: List of images to classify

        Returns:
            List of classifications with label and confidence
        """
        classifications = []

        for image in images:
            results = self.model(
                source=image.pil_image,
                conf=self.confidence_threshold,
                classes=list(self.class_indices.values()),
            )

            for result in results:
                boxes = result.boxes

                for box in boxes:
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])

                    label = next(
                        (k for k, v in self.class_indices.items() if v == class_id),
                        "unknown",
                    )

                    classifications.append(
                        Classification(label=label, weight=confidence)
                    )

        return classifications
