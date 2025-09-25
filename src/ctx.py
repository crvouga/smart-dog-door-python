from src.shared.send_email.send_email_impl import SendEmailImpl
from src.login.login_link_db import LoginLinkDb
from src.library.sql_db import SqlDb
from src.user.user_db import UserDb
from src.shared.send_email.email_db import EmailDb
from src.user.user_session_db import UserSessionDb
import logging


class Ctx:
    def __init__(self, logger: logging.Logger):
        self.logger = logging.getLogger(__name__)
        self.sql_db = SqlDb(db_path="main.db")
        self.send_email = SendEmailImpl.init(logger=self.logger)
        self.login_link_db = LoginLinkDb()
        self.user_db = UserDb()
        self.email_db = EmailDb()
        self.user_session_db = UserSessionDb()
