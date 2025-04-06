from dataclasses import dataclass, field


@dataclass
class BoundingBox:
    x_min: float = field(default=0)
    y_min: float = field(default=0)
    x_max: float = field(default=0)
    y_max: float = field(default=0)
