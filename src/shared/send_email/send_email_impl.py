import logging
from .send_email_interface import SendEmail
from .send_email_impl_noop import SendEmailImplNoop


class SendEmailImpl:
    @staticmethod
    def init(logger: logging.Logger) -> SendEmail:
        logger = logger.getChild("send_email_impl")
        return SendEmailImplNoop(logger=logger)
