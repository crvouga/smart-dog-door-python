import json
from fastapi import APIRouter, Request
import logging
import uuid
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from src.shared.html_root import view_html_root
from src.shared.send_email.send_email_interface import SendEmail
from src.library.sql_db import SqlDb


class LoginHttpApi:
    _logger: logging.Logger
    _send_email: SendEmail

    def __init__(self, logger: logging.Logger, send_email: SendEmail, sql_db: SqlDb):
        self._logger = logger.getChild(__name__)
        self._send_email = send_email
        self._sql_db = sql_db
        self._login_link_db = LoginLinkDb(sql_db=self._sql_db)
        self.router = APIRouter()

        @self.router.get("/app/login")
        async def send_login_link_page():
            self._logger.info("Login requested")
            return HTMLResponse(
                view_html_root(
                    title="Smart Dog Door Login",
                    children="""
                    <main class="container">
                        <h1>Smart Dog Door Login</h1>
                        <p>Enter your email to receive a login link.</p>
                        <form method="POST" action="/app/login/send-login-link">
                            <label for="email_address">
                                Email
                                <input type="text" id="email_address" name="email_address" placeholder="Email" required>
                            </label>
                            <button type="submit">Send Login Link</button>
                        </form>
                    </main>
                    """,
                )
            )

        @self.router.post("/app/login/send-login-link")
        async def send_login_link(request: Request):
            try:
                self._logger.info("Login requested")
                form_data = await request.form()
                email_address = form_data["email_address"]
                if not isinstance(email_address, str):
                    return RedirectResponse(
                        url=f"/app/login/err?email_address={email_address}&err='Invalid email address'",
                        status_code=303,
                    )
                self._logger.info(f"Login requested for {email_address}")
                login_link = {
                    "login-link/id": str(uuid.uuid4()),
                    "login-link/token": str(uuid.uuid4()),
                    "login-link/email-address": email_address,
                    "login-link/requested-at-utc-iso": datetime.now().isoformat(),
                    "login-link/status": "login-link-status/pending",
                }
                self._send_email.send_email(
                    email_address=email_address,
                    subject="Smart Dog Door Login",
                    body=f"<p>Click here to login: <a href='/app/clicked-login-link?token={login_link['login-link/token']}'>Login</a></p>",
                )
                self._logger.info(f"Login sent to {email_address}")
                self._login_link_db.add(login_link)

                return RedirectResponse(
                    url=f"/app/login/ok?email_address={email_address}",
                    status_code=303,
                )
            except Exception as e:
                self._logger.error(f"Error sending login: {e}")
                return RedirectResponse(
                    url=f"/app/login/err?email_address={email_address}&err='{e}'",
                    status_code=303,
                )

        @self.router.get("/app/clicked-login-link")
        async def clicked_login_link(request: Request):
            self._logger.info("Clicked login")
            login_link_token = request.query_params["token"]
            login_link = self._login_link_db.find_by_token(login_link_token)
            if login_link is None:
                return RedirectResponse(
                    url=f"/app/login/err?token={login_link_token}&err='Login link not found'",
                    status_code=303,
                )
            return RedirectResponse(
                url=f"/app/login/ok?token={login_link['login-link/token']}",
                status_code=303,
            )

        @self.router.get("/app/login/ok", response_class=HTMLResponse)
        async def login_ok(request: Request):
            self._logger.info("Login successful")
            email_address = request.query_params["token"]
            login_link_token = request.query_params["token"]
            return view_html_root(
                title="Smart Dog Door Login",
                children=f"""
                <main class="container">
                    <h1>Smart Dog Door Login</h1>
                    <p>Login successful for {email_address}</p>  
                </main>
                """,
            )

        @self.router.get("/app/login/err", response_class=HTMLResponse)
        async def login_err(request: Request):
            self._logger.info("Login failed")
            email_address = request.query_params["email_address"]
            error = request.query_params["error"]
            return view_html_root(
                title="Smart Dog Door Login",
                children=f"""
                <main class="container">
                    <h1>Smart Dog Door Login</h1>
                    <p>Login failed for {email_address}</p>
                    <p>Error: {error}</p>
                </main>
                """,
            )


class LoginLinkDb:
    def __init__(self, sql_db: SqlDb):
        self._sql_db = sql_db

    def add(self, login_link: dict):
        self._sql_db.execute(
            "INSERT INTO entities (id, type, data) VALUES (?, ?, ?)",
            (login_link["login-link/id"], "login-link", json.dumps(login_link)),
        )

    def find_by_token(self, login_link_token: str):
        queried = self._sql_db.query(
            "SELECT data FROM entities WHERE type = 'login-link' AND data LIKE '%login-link/token% = ?'",
            (login_link_token,),
        )

        if len(queried) == 0:
            return None

        return json.loads(queried[0]["data"])
