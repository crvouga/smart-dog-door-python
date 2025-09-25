from fastapi import APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Request
import logging
from src.shared.html_root import HtmlRoot


class ResultPage:
    def __init__(self, logger: logging.Logger):
        self._logger = logger.getChild(__name__)
        self.api_router = APIRouter()

        @self.api_router.get("/result_page")
        async def result_page(request: Request):
            title = request.query_params["result_page.title"]
            body = request.query_params["result_page.body"]
            link_label = request.query_params["result_page.link_label"]
            link_url = request.query_params["result_page.link_url"]
            return HTMLResponse(
                content=HtmlRoot.view(
                    title=title,
                    children=f"""
                <main class="container">
                    <h1>{title}</h1>
                    <p>{body}</p>
                    <a href="{link_url}">{link_label}</a>
                </main>
                """,
                ),
            )

    @staticmethod
    def redirect(title: str, body: str, link_label: str, link_url: str):
        return RedirectResponse(
            url=f"/result_page/?result_page.title={title}&result_page.body={body}&result_page.link_label={link_label}&result_page.link_url={link_url}",
            status_code=303,
        )
