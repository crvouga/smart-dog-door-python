from dataclasses import dataclass


@dataclass
class ClassificationConfig:
    label: str
    min_weight: float
