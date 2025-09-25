import asyncio
from src.app_http_api import AppHttpApi


if __name__ == "__main__":
    app = AppHttpApi()
    asyncio.run(app.start())
