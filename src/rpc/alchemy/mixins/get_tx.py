from src.rpc.alchemy.base import BaseAlchemyRpcClient
from src.rpc.alchemy.models.rpc_response import RpcResponse


class GetTxMixin(BaseAlchemyRpcClient):
    async def get_tx(self, signature: str) -> RpcResponse:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "json",
                    "commitment": "processed",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        response = await self.request('POST', json=payload)
        print(response.body)
        return RpcResponse(**response.body)
