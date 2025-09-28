from typing import Awaitable, Callable
from fastapi import Request
from fastapi.responses import Response
from src.library.new_id import new_id


async def session_id_set_cookie_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    """FastAPI middleware that sets a session_id cookie if one doesn't exist.

    The session_id cookie is used to track user sessions and is required for features like login.
    The cookie is httponly for security and uses a randomly generated ID with "session__" prefix.

    Examples:
        # Add middleware to FastAPI app
        app.add_middleware(BaseHTTPMiddleware, dispatch=session_id_set_cookie_middleware)

        # First request - no session_id cookie
        # Request: GET /
        # Response: 200 OK
        # Set-Cookie: session_id=session__abc123; HttpOnly

        # Subsequent requests - session_id cookie exists
        # Request: GET /
        # Cookie: session_id=session__abc123
        # Response: 200 OK
    """
    if not request.cookies.get("session_id"):
        response = await call_next(request)
        response.set_cookie(key="session_id", value=new_id("session__"), httponly=True)
        return response
    return await call_next(request)
