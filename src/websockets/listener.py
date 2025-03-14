import logging
from typing import Callable, Any

from solana.rpc.websocket_api import connect


class SolWebsocketClient:
    def __init__(self, ws_url: str = "https://api.mainnet-beta.solana.com"):
        self.ws_url = ws_url

    async def subscribe(self, on_event: Callable[[str], Any]) -> None:
        async with connect(self.ws_url) as websocket:
            await websocket.logs_subscribe()
            first_resp = await websocket.recv()
            subscription_id = first_resp[0].result
            logging.info(f"Subscribed to '{self.ws_url}' with sub_id: {subscription_id}")
            async for msg in websocket:
                on_event(msg)
            await websocket.logs_unsubscribe(subscription_id)
