from dataclasses import dataclass
from src.image_classifier.bounding_box import BoundingBox


@dataclass
class Classification:
    label: str
    weight: float
    bounding_box: BoundingBox
