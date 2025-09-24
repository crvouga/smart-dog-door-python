import json
from fastapi import APIRouter, Request
import logging
import uuid
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from src.shared.html_root import view_html_root
from src.shared.send_email.send_email_interface import SendEmail
from src.library.sql_db import SqlDb
from src.shared.result_page import ResultPage


class LoginHttpApi:
    _logger: logging.Logger
    _send_email: SendEmail

    def __init__(self, logger: logging.Logger, send_email: SendEmail, sql_db: SqlDb):
        self._logger = logger.getChild(__name__)
        self._send_email = send_email
        self._sql_db = sql_db
        self._login_link_db = LoginLinkDb(sql_db=self._sql_db)
        self.router = APIRouter()

        @self.router.get("login_link__send_login_link")
        async def send_login_link_page():
            self._logger.info("Login requested")
            return HTMLResponse(
                view_html_root(
                    title="Smart Dog Door Login",
                    children="""
                    <main class="container">
                        <h1>Smart Dog Door Login</h1>
                        <p>Enter your email to receive a login link.</p>
                        <form method="POST" action="/login_link__send_login_link">
                            <label for="login_link__email_address">
                                Email
                                <input type="text" id="login_link__email_address" name="login_link__email_address" placeholder="Email" required>
                            </label>
                            <button type="submit">Send Login Link</button>
                        </form>
                    </main>
                    """,
                )
            )

        @self.router.post("/login_link__send_login_link")
        async def send_login_link(request: Request):
            try:
                self._logger.info("Login requested")
                form_data = await request.form()
                email_address = form_data["login_link__email_address"]
                if not isinstance(email_address, str):
                    return ResultPage.redirect(
                        title="Invalid email address",
                        body="Invalid email address",
                    )
                self._logger.info(f"Login requested for {email_address}")
                login_link = {
                    "login_link__email_address": email_address,
                    "login_link__id": str(uuid.uuid4()),
                    "login_link__token": str(uuid.uuid4()),
                    "login_link__requested_at_utc_iso": datetime.now().isoformat(),
                    "login_link__status": "login_link_status__pending",
                }
                self._send_email.send_email(
                    email_address=email_address,
                    subject="Smart Dog Door Login",
                    body=f"<p>Click here to login: <a href='login_link__clicked_login_link?token={login_link['login_link__token']}'>Login</a></p>",
                )
                self._logger.info(f"Login sent to {email_address}")
                self._login_link_db.add(login_link)

                return ResultPage.redirect(
                    title="Sent login link",
                    body="Check your email for a login link",
                )
            except Exception as e:
                self._logger.error(f"Error sending login: {e}")
                return ResultPage.redirect(
                    title="Failed to send login link",
                    body="Failed to send login link",
                )

        @self.router.get("login_link__clicked_login_link")
        async def clicked_login_link(request: Request):
            self._logger.info("Clicked login link")
            login_link_token = request.query_params["token"]
            login_link = self._login_link_db.find_by_token(login_link_token)
            if login_link is None:
                return ResultPage.redirect(
                    title="Login link not found",
                    body="Login link not found",
                )
            if is_expired(login_link):
                return ResultPage.redirect(
                    title="Login link expired",
                    body="Login link expired",
                )
            return ResultPage.redirect(
                title="Login link clicked",
                body="Login link clicked",
            )


def to_requested_at_utc_iso(login_link: dict) -> datetime:
    return datetime.fromisoformat(login_link["login_link__requested_at_utc_iso"])


def to_age(login_link: dict) -> timedelta:
    link_age = datetime.now() - to_requested_at_utc_iso(login_link)
    return link_age


def is_expired(login_link: dict) -> bool:
    link_age = to_age(login_link)
    is_expired = link_age > timedelta(minutes=10)
    return is_expired


class LoginLinkDb:
    def __init__(self, sql_db: SqlDb):
        self._sql_db = sql_db

    def add(self, login_link: dict):
        self._sql_db.execute(
            "INSERT INTO entities (id, type, data) VALUES (?, ?, ?)",
            (login_link["login_link__id"], "login_link", json.dumps(login_link)),
        )

    def find_by_token(self, login_link_token: str):
        queried = self._sql_db.query(
            "SELECT data FROM entities WHERE type = 'login_link' AND data LIKE '%login_link__token% = ?'",
            (login_link_token,),
        )

        if len(queried) == 0:
            return None

        return json.loads(queried[0]["data"])
