from abc import abstractmethod, ABC
from typing import Optional, Any, Dict

from aiohttp import FormData

from src.rpc.alchemy.models.rpc_response import RpcResponse
from src.rpc.http_client import HttpClient, HttpClientResponse


class BaseAlchemyRpcClient(ABC):
    def __init__(
        self,
        http_client: HttpClient,
        alchemy_token: str,
        network: str = 'solana-mainnet'
    ) -> None:
        self.http_client = http_client
        self.url = f'https://{network}.g.alchemy.com/v2/{alchemy_token}'

    async def request(
        self,
        method: str,
        data: Optional[Dict[str, Any] | FormData] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> HttpClientResponse:
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        return await self.http_client.request(
            method,
            self.url,
            data=data,
            json_=json,
            headers=headers,
            params=params,
        )

    @abstractmethod
    async def get_tx(self, signature) -> RpcResponse:
        raise NotImplementedError()
