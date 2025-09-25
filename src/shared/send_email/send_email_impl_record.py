import logging
from datetime import datetime
from src.shared.send_email.email_db import EmailDb
from .send_email_interface import SendEmail
from src.library.sql_db import Tx


class SendEmailImplRecord(SendEmail):

    def __init__(
        self, logger: logging.Logger, send_email: SendEmail, email_db: EmailDb
    ):
        self._logger = logger.getChild("record_sent_emails")
        self._send_email = send_email
        self._email_db = email_db

    async def send_email(self, tx: Tx, email: dict):
        await self._send_email.send_email(tx, email)
        email = {**email, "email__sent_at_utc_iso": datetime.now().isoformat()}
        await self._email_db.insert(tx, email)
        self._logger.info(
            f"Sent email to {email['email__to']} with subject {email['email__subject']} and body {email['email__body']}"
        )
