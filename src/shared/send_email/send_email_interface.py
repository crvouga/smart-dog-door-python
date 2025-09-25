from abc import ABC, abstractmethod
from src.library.sql_db import Tx


class SendEmail(ABC):
    @abstractmethod
    async def send_email(self, tx: Tx, email: dict):
        pass
