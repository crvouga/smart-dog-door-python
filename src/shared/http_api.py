from abc import ABC, abstractmethod
from fastapi import APIRouter


class HttpApi(ABC):
    def __init__(self):
        self.api_router = APIRouter()
