from dataclasses import dataclass


@dataclass
class Classification:
    label: str
    weight: float
