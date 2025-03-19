from aiohttp import FormData
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, TypeVar

from pydantic import BaseModel

from src.rpc.http_client import HttpClient, HttpClientResponse
from src.settings.factory import SettingsFactory


T = TypeVar('T', bound=SettingsFactory)
TX = TypeVar('TX', bound=BaseModel)


class AbstractRpcClient(ABC):
    def __init__(
        self,
        http_client: HttpClient,
        settings: T,
    ) -> None:
        self.http_client = http_client
        self.settings = settings

    @abstractmethod
    async def request(
        self,
        method: str,
        data: Optional[Dict[str, Any] | FormData] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> HttpClientResponse:
        pass

    @abstractmethod
    async def get_tx(self, signature) -> TX:
        pass
