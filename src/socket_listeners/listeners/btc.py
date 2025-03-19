import logging
import zmq

from typing import Callable, Any, Awaitable

from src.socket_listeners.base import AbstractSocketListener
from src.settings import BTCSettings


class BTCSocketListener(AbstractSocketListener[BTCSettings]):
    def __init__(self, settings: BTCSettings):
        super().__init__(settings)

    async def subscribe(self, on_event: Callable[[bytes], Awaitable[Any]]) -> None:
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.settings.zmq_tcp)
        socket.setsockopt_string(zmq.SUBSCRIBE, self.settings.zmq_stream_type)
        while True:
            try:
                parts = socket.recv_multipart()
                raw_tx = parts[1]

                # The 'sequence' variable isn't used currently,
                # but it may help with missing transactions in the future.
                # sequence = int.from_bytes(
                #     parts[2],
                #     byteorder='little'
                # ) if len(parts) > 2 else 0

                await on_event(raw_tx)
            except zmq.Again:
                pass
            except Exception as e:
                logging.error(f"BTC listener error: {e}")
