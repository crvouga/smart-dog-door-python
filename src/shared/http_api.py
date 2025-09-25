import logging
from fastapi import APIRouter


class HttpApi:
    def __init__(self, logger: logging.Logger):
        self.logger = logger.getChild(__name__)
        self.api_router = APIRouter()
