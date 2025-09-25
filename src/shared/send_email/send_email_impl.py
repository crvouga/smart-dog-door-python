import logging
from .send_email_interface import SendEmail
from .send_email_impl_noop import SendEmailImplNoop
from .send_email_impl_record import SendEmailImplRecord
from src.library.sql_db import SqlDb
from src.shared.send_email.email_db import EmailDb


class SendEmailImpl:
    @staticmethod
    def init(logger: logging.Logger, sql_db: SqlDb) -> SendEmail:
        logger = logger.getChild("send_email_impl")
        send_email = SendEmailImplRecord(
            logger=logger,
            send_email=SendEmailImplNoop(logger=logger),
            email_db=EmailDb(sql_db=sql_db),
        )
        return send_email
