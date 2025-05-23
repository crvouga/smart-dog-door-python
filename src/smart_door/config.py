from dataclasses import dataclass, field
from datetime import timedelta
from src.image_classifier.classification_config import ClassificationConfig


@dataclass
class Config:
    tick_rate: timedelta = timedelta(seconds=1 / 2)
    minimal_rate_camera_process: timedelta = timedelta(seconds=1 / 5)
    minimal_duration_will_open: timedelta = timedelta(seconds=3)
    minimal_duration_will_close: timedelta = timedelta(seconds=3)
    max_classification_runs: int = 3
    classification_close_list: list[ClassificationConfig] = field(
        default_factory=lambda: [
            ClassificationConfig(label="cat", min_weight=0.5),
        ]
    )
    classification_open_list: list[ClassificationConfig] = field(
        default_factory=lambda: [
            ClassificationConfig(label="dog", min_weight=0.5),
        ]
    )
