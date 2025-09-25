from fastapi import Request
import logging
from src.library.new_id import new_id
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Union
from src.shared.html_root import HtmlRoot
from src.shared.result_page.result_page_http_api import ResultPageHttpApi
from src.login.login_link import LoginLink
from datetime import datetime
from src.shared.http_api import HttpApi
from src.ctx import Ctx


class LoginLinkHttpApi(HttpApi):

    def __init__(self, ctx: Ctx):
        super().__init__(ctx=ctx)
        self.ctx = ctx

        @self.api_router.get("/login_link__send")
        async def send_login_link_page():
            self.logger.info("Login requested")
            return HtmlRoot.response(
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

        @self.api_router.post("/login_link__send", response_model=None)
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
                    "login_link__id": new_id("login_link__"),
                    "login_link__token": new_id("login_link_token__"),
                    "login_link__requested_at_utc_iso": datetime.now().isoformat(),
                    "login_link__email_id": new_id("email__"),
                }

                email = {
                    "email__id": login_link["login_link__email_id"],
                    "email__to": email_address,
                    "email__subject": "Smart Dog Door Login Link",
                    "email__body": f"<p>Click here to login: <a href='/login_link__clicked_login_link?login_link__token={login_link['login_link__token']}'>Login</a></p>",
                }

                assert email["email__id"] == login_link["login_link__email_id"]

                async with self.ctx.sql_db.transaction() as tx:
                    await self.ctx.send_email.send_email(tx, email)

                    self.logger.info(f"Login sent to {email_address}")

                    await self.ctx.login_link_db.insert(tx, login_link)

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
                    body=f"Failed to send login link: {e}",
                    link_label="Back",
                    link_url="/login_link__send",
                )

        @self.api_router.get("/login_link__clicked_login_link", response_model=None)
        async def clicked_login_link(request: Request):
            self.logger.info("Clicked login link")
            login_link_token = request.query_params["login_link__token"]
            if not isinstance(login_link_token, str):
                return ResultPageHttpApi.redirect(
                    title="Invalid login link token",
                    body="Invalid login link token",
                    link_label="Back",
                    link_url="/login_link__send",
                )
            async with self.ctx.sql_db.transaction() as tx:
                found = await self.ctx.login_link_db.find_by_token(tx, login_link_token)
            if found is None:
                return ResultPageHttpApi.redirect(
                    title="Login link not found",
                    body="Login link not found",
                    link_label="Back",
                    link_url="/login_link__send",
                )
            if LoginLink.is_expired(found):
                return ResultPageHttpApi.redirect(
                    title="Login link expired",
                    body="Login link expired",
                    link_label="Back",
                    link_url="/login_link__send",
                )

            session_id = request.cookies.get("session_id")
            if not isinstance(session_id, str):
                return ResultPageHttpApi.redirect(
                    title="Invalid session id",
                    body="Invalid session id",
                    link_label="Back",
                    link_url="/login_link__send",
                )

            async with self.ctx.sql_db.transaction() as tx:
                login_link_new = {
                    **found,
                    "login_link__status": "clicked",
                    "login_link__used_at_utc_iso": datetime.now().isoformat(),
                }
                await self.ctx.login_link_db.update(tx, login_link_new)

                found_user = await self.ctx.user_db.find_by_email_address(
                    found["login_link__email_address"],
                )

                user_session_new = {
                    "user_session__id": new_id("user_session__"),
                    "user_session__login_link_id": found["login_link__id"],
                    "user_session__created_at_utc_iso": datetime.now().isoformat(),
                    "user_session__session_id": session_id,
                    "user_session__user_id": found_user["user__id"],
                }
                await self.ctx.user_session_db.insert(tx, user_session_new)

                return ResultPageHttpApi.redirect(
                    title="Logged in",
                    body="Logged in",
                    link_label="Home",
                    link_url="/",
                )
