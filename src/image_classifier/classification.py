from dataclasses import dataclass, field
from src.image_classifier.bounding_box import BoundingBox


@dataclass
class Classification:
    label: str
    weight: float = field(default=0)
    bounding_box: BoundingBox = field(default_factory=BoundingBox)
