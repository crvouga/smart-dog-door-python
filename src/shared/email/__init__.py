from dataclasses import dataclass


@dataclass
class Email:
    to: str
    subject: str
    body: str
