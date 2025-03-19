from aiohttp import FormData, BasicAuth
from typing import Optional, Any, Dict

from src.rpc.base import AbstractRpcClient
from src.rpc.models.btc_rpc_response import BTCRPCResponse
from src.settings import BTCSettings
from src.rpc.http_client import HttpClient, HttpClientResponse


class BTCRpcClient(AbstractRpcClient):
    def __init__(
        self,
        http_client: HttpClient,
        settings: BTCSettings,
    ) -> None:
        super().__init__(http_client, settings)

    async def request(
        self,
        method: str,
        data: Optional[Dict[str, Any] | FormData] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> HttpClientResponse:
        url = self.settings.rpc_url

        return await self.http_client.request(
            method,
            url,
            data=data,
            json_=json,
            params=params,
            auth=BasicAuth(self.settings.rpc_user, self.settings.rpc_password),
        )

    async def get_tx(self, tx_identifier: bytes) -> BTCRPCResponse:
        payload = {
            "jsonrpc": "1.0",
            "id": "decode",
            "method": "decoderawtransaction",
            "params": [tx_identifier.hex()]
        }
        response = await self.request('POST', json=payload)
        return BTCRPCResponse(**response.body)
