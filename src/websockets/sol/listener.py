import logging
from typing import Callable, Any, Awaitable

from solana.rpc.websocket_api import connect
from solders.solders import RpcLogsResponse, Signature

from src.websockets.base import BaseWebsocketListener


class SolWebsocketListener(BaseWebsocketListener):
    def __init__(self, ws_url: str = "wss://api.mainnet-beta.solana.com"):
        super().__init__(ws_url)

    async def subscribe(self, on_event: Callable[[Any], Awaitable[Any]]) -> None:
        async with connect(self.ws_url) as websocket:
            await websocket.logs_subscribe()
            first_resp = await websocket.recv()
            subscription_id = first_resp[0].result
            logging.info(f"Subscribed to '{self.ws_url}' with sub_id: {subscription_id}")
            async for msg in websocket:
                try:
                    log: RpcLogsResponse = msg[0].result.value  # noqa
                    await on_event(log.signature)
                except Exception as e:
                    logging.error(f"Failed to get tx: {e} - {msg}")
            await websocket.logs_unsubscribe(subscription_id)
