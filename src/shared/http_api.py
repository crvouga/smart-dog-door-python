from src.ctx import Ctx
from fastapi import APIRouter


class HttpApi:
    def __init__(self, ctx: Ctx):
        self.logger = ctx.logger.getChild(__name__)
        self.api_router = APIRouter()
