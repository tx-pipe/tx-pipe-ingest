from aiohttp import FormData
from typing import Optional, Any, Dict

from tx_pipe_ingest.rpc.base import AbstractRpcClient
from tx_pipe_ingest.settings import SOLSettings
from tx_pipe_ingest.rpc.models.sol_rpc_response import SOLRPCResponse
from tx_pipe_ingest.rpc.http_client import HttpClient, HttpClientResponse


class SOLRpcClient(AbstractRpcClient):
    def __init__(
        self,
        http_client: HttpClient,
        settings: SOLSettings,
    ) -> None:
        super().__init__(http_client, settings)

    async def request(
        self,
        method: str,
        data: Optional[Dict[str, Any] | FormData] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> HttpClientResponse:
        url = f'https://solana-{self.settings.network}.g.alchemy.com/v2/{self.settings.alchemy_api_key}'
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        return await self.http_client.request(
            method,
            url,
            data=data,
            json_=json,
            headers=headers,
            params=params,
        )

    async def get_tx(self, tx_identifier: str) -> SOLRPCResponse:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "getTransaction",
            "params": [
                tx_identifier,
                {
                    "encoding": "json",
                    "commitment": "processed",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        response = await self.request('POST', json=payload)
        return SOLRPCResponse(**response.body)
