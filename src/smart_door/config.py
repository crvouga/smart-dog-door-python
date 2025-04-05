from dataclasses import dataclass
from datetime import timedelta
from src.image_classifier.classification_config import ClassificationConfig


@dataclass
class Config:
    tick_rate: timedelta
    minimal_rate_camera_process: timedelta
    minimal_duration_will_open: timedelta
    minimal_duration_will_close: timedelta
    classification_close_list: list[ClassificationConfig]
    classification_open_list: list[ClassificationConfig]

    @classmethod
    def init(cls) -> "Config":
        return Config(
            tick_rate=timedelta(seconds=1),
            minimal_rate_camera_process=timedelta(seconds=1),
            minimal_duration_will_open=timedelta(seconds=1),
            minimal_duration_will_close=timedelta(seconds=1),
            classification_close_list=[
                ClassificationConfig(label="cat", min_weight=0.5),
            ],
            classification_open_list=[
                ClassificationConfig(label="dog", min_weight=0.5),
            ],
        )
