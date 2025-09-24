from fastapi.responses import RedirectResponse


class ResultPage:
    def __init__(self):
        pass

    @staticmethod
    def redirect(title: str, body: str):
        return RedirectResponse(
            url=f"/app/result?title={title}&body={body}",
            status_code=303,
        )
