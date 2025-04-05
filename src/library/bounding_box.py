from dataclasses import dataclass


@dataclass
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
