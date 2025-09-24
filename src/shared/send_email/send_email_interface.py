from abc import ABC, abstractmethod


class SendEmail(ABC):
    @abstractmethod
    def send_email(self, email_address: str, subject: str, body: str) -> None:
        pass
