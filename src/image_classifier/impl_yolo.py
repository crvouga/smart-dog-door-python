from ultralytics import YOLO  # type: ignore
from src.image.image import Image
from src.image_classifier.bounding_box import BoundingBox
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
        return f"./assets/models/yolov8{self.value}.pt"


COCO_DATASET_CLASS_INDICES = {"cat": 15, "dog": 16}
DEFAULT_CONFIDENCE_THRESHOLD = 0.5


class YoloImageClassifier(ImageClassifier):
    def __init__(
        self,
        model_size: YoloModelSize,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> None:
        self._model = YOLO(model_size.to_filename())
        self._confidence_threshold = confidence_threshold
        self._class_indices = COCO_DATASET_CLASS_INDICES

    def classify(self, images: list[Image]) -> list[Classification]:
        return list(self._classify_images(images))

    def _classify_images(
        self,
        images: list[Image],
    ) -> Iterator[Classification]:
        for image in images:
            results = self._model(
                source=image.pil_image,
                conf=self._confidence_threshold,
                classes=list(self._class_indices.values()),
                verbose=False,
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
                    (k for k, v in self._class_indices.items() if v == class_id),
                    "unknown",
                )

                bounding_box = BoundingBox(
                    x_min=float(box.xyxy[0][0]),
                    y_min=float(box.xyxy[0][1]),
                    x_max=float(box.xyxy[0][2]),
                    y_max=float(box.xyxy[0][3]),
                )

                yield Classification(
                    label=label, weight=confidence, bounding_box=bounding_box
                )
