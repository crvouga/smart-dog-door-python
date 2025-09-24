import logging
from .send_email_interface import SendEmail


class SendEmailImplNoop(SendEmail):

    def __init__(self, logger: logging.Logger):
        self.logger = logger.getChild("send_email_impl_noop")

    def send_email(self, email_address: str, subject: str, body: str) -> None:
        self.logger.info(
            f"Sending email to {email_address} with subject {subject} and body {body}"
        )
