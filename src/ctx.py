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
        self.send_email = SendEmailImpl.init(logger=self.logger, sql_db=self.sql_db)
        self.login_link_db = LoginLinkDb(sql_db=self.sql_db)
        self.user_db = UserDb(sql_db=self.sql_db)
        self.email_db = EmailDb(sql_db=self.sql_db)
        self.user_session_db = UserSessionDb(sql_db=self.sql_db)
