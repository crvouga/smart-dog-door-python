import json
from fastapi import APIRouter, Request
import logging
import uuid
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Dict, Any, Union
from src.shared.html_root import HtmlRoot
from src.shared.send_email.send_email_interface import SendEmail
from src.library.sql_db import SqlDb
from src.shared.result_page.result_page_http_api import ResultPageHttpApi
from src.shared.email import Email
from src.login.login_link import LoginLink
from src.login.login_link_db import LoginLinkDb
from datetime import datetime
from src.shared.http_api import HttpApi


class LoginLinkHttpApi(HttpApi):

    def __init__(self, logger: logging.Logger, send_email: SendEmail, sql_db: SqlDb):
        super().__init__(logger=logger)
        self.send_email = send_email
        self.sql_db = sql_db
        self.login_link_db = LoginLinkDb(sql_db=self.sql_db)

        @self.api_router.get("/login_link__send")
        async def send_login_link_page() -> HTMLResponse:
            self.logger.info("Login requested")
            return HTMLResponse(
                HtmlRoot.view(
                    title="Smart Dog Door Login",
                    children="""
                    <main class="container">
                        <h1>Smart Dog Door Login</h1>
                        <p>Enter your email to receive a login link.</p>
                        <form method="POST" action="/login_link__send">
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

        @self.api_router.post("/login_link__send")
        async def send_login_link(
            request: Request,
        ) -> Union[HTMLResponse, RedirectResponse]:
            try:
                self.logger.info("Login requested")
                form_data = await request.form()
                email_address = form_data["login_link__email_address"]
                if not isinstance(email_address, str):
                    return ResultPageHttpApi.redirect(
                        title="Invalid email address",
                        body="Invalid email address",
                        link_label="Back",
                        link_url="/login_link__send",
                    )
                self.logger.info(f"Login requested for {email_address}")
                login_link = {
                    "login_link__email_address": email_address,
                    "login_link__id": str(uuid.uuid4()),
                    "login_link__token": str(uuid.uuid4()),
                    "login_link__requested_at_utc_iso": datetime.now().isoformat(),
                    "login_link__status": "login_link_status.pending",
                }
                email = Email(
                    to=email_address,
                    subject="Smart Dog Door Login",
                    body=f"""
                    <p>Click here to login: <a href='/login_link__clicked_login_link?token={login_link['login_link__token']}'>Login</a></p>
                    """,
                )
                await self.send_email.send_email(email=email)
                self.logger.info(f"Login sent to {email_address}")
                await self.login_link_db.insert(login_link)

                return ResultPageHttpApi.redirect(
                    title="Sent login link",
                    body="Check your email for a login link",
                    link_label="Back",
                    link_url="/login_link__send",
                )
            except Exception as e:
                self.logger.error(f"Error sending login: {e}")
                return ResultPageHttpApi.redirect(
                    title="Failed to send login link",
                    body="Failed to send login link",
                    link_label="Back",
                    link_url="/login_link__send",
                )

        @self.api_router.get("/login_link__clicked_login_link")
        async def clicked_login_link(
            request: Request,
        ) -> Union[HTMLResponse, RedirectResponse]:
            self.logger.info("Clicked login link")
            login_link_token = request.query_params["token"]
            clicked_link = await self.login_link_db.find_by_token(login_link_token)
            if clicked_link is None:
                return ResultPageHttpApi.redirect(
                    title="Login link not found",
                    body="Login link not found",
                    link_label="Back",
                    link_url="/login_link__send",
                )
            if LoginLink.is_expired(clicked_link):
                return ResultPageHttpApi.redirect(
                    title="Login link expired",
                    body="Login link expired",
                    link_label="Back",
                    link_url="/login_link__send",
                )
            return ResultPageHttpApi.redirect(
                title="Login link clicked",
                body="Login link clicked",
                link_label="Back",
                link_url="/login_link__send",
            )
