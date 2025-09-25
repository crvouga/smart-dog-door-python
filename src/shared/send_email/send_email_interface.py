from abc import ABC, abstractmethod


class SendEmail(ABC):
    @abstractmethod
    async def send_email(self, email: dict) -> None:
        pass
