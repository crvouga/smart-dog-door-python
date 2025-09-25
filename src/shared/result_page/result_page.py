from fastapi import APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Request
import logging


class ResultPage:
    def __init__(self, logger: logging.Logger):
        self._logger = logger.getChild(__name__)
        self.api_router = APIRouter()

        @self.api_router.get("/result_page")
        async def result_page(request: Request):
            title = request.query_params["result_page.title"]
            body = request.query_params["result_page.body"]
            return HTMLResponse(
                content=f"<h1>{title}</h1><p>{body}</p>",
            )

    @staticmethod
    def redirect(title: str, body: str):
        return RedirectResponse(
            url=f"/result_page/?result_page.title={title}&result_page.body={body}",
            status_code=303,
        )
