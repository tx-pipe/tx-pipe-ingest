import logging

from typing import Callable, Any, Awaitable
from solana.rpc.websocket_api import connect
from solders.solders import RpcLogsResponse

from src.settings import SOLSettings
from src.socket_listeners.base import AbstractSocketListener


class SOLSocketListener(AbstractSocketListener[SOLSettings]):
    def __init__(self, settings: SOLSettings):
        super().__init__(settings)

    async def subscribe(self, on_event: Callable[[str, Any], Awaitable[Any]], *args, **kwargs) -> None:
        async with connect(self.settings.socket_url, ping_interval=None) as websocket:
            await websocket.logs_subscribe()
            first_resp = await websocket.recv()
            subscription_id = first_resp[0].result
            logging.info(f"Subscribed to '{self.settings.socket_url}' with sub_id: {subscription_id}")

            async for msg in websocket:
                try:
                    log: RpcLogsResponse = msg[0].result.value  # noqa
                    await on_event(log.signature.__str__(), *args, **kwargs)
                except Exception as e:
                    logging.error(f"Failed to get tx: {e} - {msg}")
            await websocket.logs_unsubscribe(subscription_id)
