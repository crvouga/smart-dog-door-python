import logging
from .send_email_interface import SendEmail
from src.library.sql_db import Tx


class SendEmailImplNoop(SendEmail):

    def __init__(self, logger: logging.Logger):
        self.logger = logger.getChild("send_email_impl_noop")

    async def send_email(self, tx: Tx, email: dict) -> None:
        self.logger.info(
            f"Sending email to {email['email__to']} with subject {email['email__subject']} and body {email['email__body']}"
        )
