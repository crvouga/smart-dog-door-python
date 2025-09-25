import json
from fastapi import APIRouter, Request
import logging
import uuid
from fastapi.responses import HTMLResponse
from src.shared.html_root import view_html_root
from src.shared.send_email.send_email_interface import SendEmail
from src.library.sql_db import SqlDb
from src.shared.result_page.result_page import ResultPage
from src.shared.email import Email
from src.login.login_link import LoginLink
from src.login.login_link_db import LoginLinkDb
from datetime import datetime


class LoginLinkHttpApi:
    _logger: logging.Logger
    _send_email: SendEmail

    def __init__(self, logger: logging.Logger, send_email: SendEmail, sql_db: SqlDb):
        self._logger = logger.getChild(__name__)
        self._send_email = send_email
        self._sql_db = sql_db
        self._login_link_db = LoginLinkDb(sql_db=self._sql_db)
        self.api_router = APIRouter()

        @self.api_router.get("/login_link.send")
        async def send_login_link_page():
            self._logger.info("Login requested")
            return HTMLResponse(
                view_html_root(
                    title="Smart Dog Door Login",
                    children="""
                    <main class="container">
                        <h1>Smart Dog Door Login</h1>
                        <p>Enter your email to receive a login link.</p>
                        <form method="POST" action="/login_link.send">
                            <label for="login_link.email_address">
                                Email
                                <input type="text" id="login_link.email_address" name="login_link.email_address" placeholder="Email" required>
                            </label>
                            <button type="submit">Send Login Link</button>
                        </form>
                    </main>
                    """,
                )
            )

        @self.api_router.post("/login_link.send")
        async def send_login_link(request: Request):
            try:
                self._logger.info("Login requested")
                form_data = await request.form()
                email_address = form_data["login_link.email_address"]
                if not isinstance(email_address, str):
                    return ResultPage.redirect(
                        title="Invalid email address",
                        body="Invalid email address",
                    )
                self._logger.info(f"Login requested for {email_address}")
                login_link = {
                    "login_link.email_address": email_address,
                    "login_link.id": str(uuid.uuid4()),
                    "login_link.token": str(uuid.uuid4()),
                    "login_link.requested_at_utc_iso": datetime.now().isoformat(),
                    "login_link.status": "login_link_status.pending",
                }
                email = Email(
                    to=email_address,
                    subject="Smart Dog Door Login",
                    body=f"""
                    <p>Click here to login: <a href='/login_link.clicked_login_link?token={login_link['login_link.token']}'>Login</a></p>
                    """,
                )
                self._send_email.send_email(email=email)
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

        @self.api_router.get("/login_link.clicked_login_link")
        async def clicked_login_link(request: Request):
            self._logger.info("Clicked login link")
            login_link_token = request.query_params["token"]
            clicked_link = self._login_link_db.find_by_token(login_link_token)
            if clicked_link is None:
                return ResultPage.redirect(
                    title="Login link not found",
                    body="Login link not found",
                )
            if LoginLink.is_expired(clicked_link):
                return ResultPage.redirect(
                    title="Login link expired",
                    body="Login link expired",
                )
            return ResultPage.redirect(
                title="Login link clicked",
                body="Login link clicked",
            )
