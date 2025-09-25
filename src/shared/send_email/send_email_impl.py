import logging
from .send_email_interface import SendEmail
from .send_email_impl_noop import SendEmailImplNoop
from .send_email_impl_record import SendEmailImplRecord
from src.shared.send_email.email_db import EmailDb


class SendEmailImpl:
    @staticmethod
    def init(logger: logging.Logger) -> SendEmail:
        logger = logger.getChild("send_email_impl")
        return SendEmailImplRecord(
            logger=logger,
            send_email=SendEmailImplNoop(logger=logger),
            email_db=EmailDb(),
        )
