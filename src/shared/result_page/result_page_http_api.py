from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi import Request
from src.shared.html_root import HtmlRoot
from src.shared.http_api import HttpApi
import logging


class ResultPageHttpApi(HttpApi):
    def __init__(self, **kwargs):
        super().__init__()
        self.logger = kwargs.get("logger")
        assert isinstance(self.logger, logging.Logger)

        @self.api_router.get("/result_page")
        async def result_page(request: Request):
            title = request.query_params["result_page.title"]
            body = request.query_params["result_page.body"]
            link_label = request.query_params["result_page.link_label"]
            link_url = request.query_params["result_page.link_url"]
            return HtmlRoot.response(
                title=title,
                children=f"""
                <main class="container">
                    <h1>{title}</h1>
                    <p>{body}</p>
                    <a href="{link_url}">{link_label}</a>
                </main>
                """,
            )

    @staticmethod
    def redirect(
        title: str, body: str, link_label: str, link_url: str
    ) -> RedirectResponse:
        return RedirectResponse(
            url=f"/result_page/?result_page.title={title}&result_page.body={body}&result_page.link_label={link_label}&result_page.link_url={link_url}",
            status_code=303,
        )
