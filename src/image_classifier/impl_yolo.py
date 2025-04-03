from ultralytics import YOLO  # type: ignore
from src.image.image import Image
from .interface import ImageClassifier, Classification
from enum import Enum
from typing import Iterator


class YoloModelSize(Enum):
    NANO = "n"
    SMALL = "s"
    MEDIUM = "m"
    LARGE = "l"
    EXTRA_LARGE = "x"

    def to_filename(self) -> str:
        return f"./models/yolov8{self.value}.pt"


COCO_DATASET_CLASS_INDICES = {"cat": 15, "dog": 16}


class YoloImageClassifier(ImageClassifier):
    def __init__(
        self,
        model_size: YoloModelSize = YoloModelSize.NANO,
        confidence_threshold: float = 0.25,
    ) -> None:
        self.model = YOLO(model_size.to_filename())
        self.confidence_threshold = confidence_threshold
        self.class_indices = COCO_DATASET_CLASS_INDICES

    def classify(self, images: list[Image]) -> list[Classification]:
        return list(self._classify_images(images))

    def _classify_images(
        self,
        images: list[Image],
    ) -> Iterator[Classification]:
        for image in images:
            results = self.model(
                source=image.pil_image,
                conf=self.confidence_threshold,
                classes=list(self.class_indices.values()),
            )
            yield from self._classify_image(results=results)

    def _classify_image(
        self,
        results: list,
    ) -> Iterator[Classification]:

        for result in results:
            boxes = result.boxes

            for box in boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])

                label = next(
                    (k for k, v in self.class_indices.items() if v == class_id),
                    "unknown",
                )

                yield Classification(label=label, weight=confidence)
