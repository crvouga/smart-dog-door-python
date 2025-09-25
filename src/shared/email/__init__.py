from dataclasses import dataclass


@dataclass
class Email:
    email__to: str
    email__subject: str
    email__body: str
