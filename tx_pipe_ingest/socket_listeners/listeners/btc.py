import logging
import zmq

from typing import Callable, Any, Awaitable

from tx_pipe_ingest.socket_listeners.base import AbstractSocketListener
from tx_pipe_ingest.settings import BTCSettings


class BTCSocketListener(AbstractSocketListener[BTCSettings]):
    def __init__(self, settings: BTCSettings):
        super().__init__(settings)

    async def subscribe(self, on_event: Callable[[bytes, Any], Awaitable[Any]], *args, **kwargs) -> None:
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.settings.zmq_tcp_address)
        socket.setsockopt_string(zmq.SUBSCRIBE, self.settings.zmq_stream_type)
        while True:
            try:
                parts = socket.recv_multipart()
                raw_tx = parts[1]
                await on_event(raw_tx, *args, **kwargs)
            except zmq.Again:
                pass
            except Exception as e:
                logging.error(f"BTC listener error: {e}")
