import asyncio
import os

from dotenv import load_dotenv

from src.kafka.client.base import BaseKafkaProducer
from src.kafka.client.client_config import KafkaClientConfig
from src.rpc.alchemy import AlchemyRpcClient
from src.rpc.http_client import HttpClient
from src.websockets.sol.listener import SolWebsocketListener
from src.services.sol_pipe import SolPipe


async def main():
    load_dotenv()

    alchemy_rpc_client = AlchemyRpcClient(HttpClient(), os.getenv("ALCHEMY_API_KEY"))

    websocket_listener = SolWebsocketListener()

    kafka_config = KafkaClientConfig(from_env=True)
    kafka_producer = BaseKafkaProducer(kafka_config, 'sol-raw-txs')

    sol_pipe = SolPipe(alchemy_rpc_client, websocket_listener, kafka_producer)
    await sol_pipe.run()


if __name__ == "__main__":
    asyncio.run(main())
