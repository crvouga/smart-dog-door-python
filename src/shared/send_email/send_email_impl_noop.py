import logging
from .send_email_interface import SendEmail
from src.shared.email import Email


class SendEmailImplNoop(SendEmail):

    def __init__(self, logger: logging.Logger):
        self.logger = logger.getChild("send_email_impl_noop")

    def send_email(self, email: Email) -> None:
        self.logger.info(
            f"Sending email to {email.to} with subject {email.subject} and body {email.body}"
        )
