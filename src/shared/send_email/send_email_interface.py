from abc import ABC, abstractmethod
from src.shared.email import Email


class SendEmail(ABC):
    @abstractmethod
    def send_email(self, email: Email) -> None:
        pass
