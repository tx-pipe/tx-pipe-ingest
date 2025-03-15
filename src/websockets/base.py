from typing import Callable, Any, Awaitable


class BaseWebsocketListener:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url

    async def subscribe(self, on_event: Callable[[Any], Awaitable[Any]]) -> None:
        raise NotImplementedError()
