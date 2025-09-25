from abc import ABC, abstractmethod
from src.shared.email import Email
from typing import Any, Coroutine


class SendEmail(ABC):
    @abstractmethod
    async def send_email(self, email: Email) -> None:
        pass
