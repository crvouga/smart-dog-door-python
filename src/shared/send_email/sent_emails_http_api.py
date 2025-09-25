from src.shared.http_api import HttpApi
from src.ctx import Ctx
from src.shared.html_root import HtmlRoot
import html
from fastapi import Request
from fastapi.responses import HTMLResponse


class SentEmailsHttpApi(HttpApi):
    def __init__(self, ctx: Ctx):
        super().__init__(ctx=ctx)
        self.ctx = ctx

        @self.api_router.get("/sent_emails__list")
        async def list() -> HTMLResponse:
            emails = await self.ctx.sql_db.query(
                """
                SELECT 
                    email__id,
                    email__to,
                    email__subject, 
                    email__body,
                    email__sent_at_utc_iso
                FROM emails
                LIMIT 100
                """
            )

            html_table = (
                "<table border='1'>"
                "<tr>"
                "<th>ID</th>"
                "<th>Subject</th>"
                "<th>To</th>"
                "<th>Sent At</th>"
                "</tr>"
            )

            for email in emails:
                html_table += (
                    "<tr>"
                    f"<td>"
                    f"<a href='/sent_emails__view?email__id={html.escape(str(email.get('email__id', '')))}'>"
                    f"{html.escape(str(email.get('email__id', '')))}"
                    f"</a>"
                    f"</td>"
                    f"<td>{html.escape(str(email.get('email__subject', '')))}</td>"
                    f"<td>{html.escape(str(email.get('email__to', '')))}</td>"
                    f"<td>{html.escape(str(email.get('email__sent_at_utc_iso', '')))}</td>"
                    "</tr>"
                )

            html_table += "</table>"

            return HtmlRoot.response(
                title="Sent Emails",
                children=f"""<main><h1>Sent Emails</h1>{html_table}</main>""",
            )

        @self.api_router.get("/sent_emails__view")
        async def view(request: Request) -> HTMLResponse:
            email__id = request.query_params["email__id"]
            emails = await self.ctx.sql_db.query(
                """
                SELECT 
                    email__id,
                    email__to,
                    email__subject,
                    email__body, 
                    email__sent_at_utc_iso
                FROM emails 
                WHERE email__id = ?
                ORDER BY email__sent_at_utc_iso DESC
                """,
                (email__id,),
            )

            if not emails:
                return HtmlRoot.response(
                    title="Email Not Found", children="<p>Email not found</p>"
                )

            email = emails[0]

            return HtmlRoot.response(
                title="Sent Email",
                children=f"""
            <main>
                <h1>{html.escape(str(email.get('email__subject', '')))}</h1>
                <div class="email-metadata">
                    <p><strong>To:</strong> {html.escape(str(email.get('email__to', '')))}</p>
                    <p><strong>Sent:</strong> {html.escape(str(email.get('email__sent_at_utc_iso', '')))}</p>
                </div>
                <div class="email-body">
                    <p>{html.escape(str(email.get('email__body', '')))}</p>
                </div>
            </main>
            """,
            )
