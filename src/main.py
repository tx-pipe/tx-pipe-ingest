import asyncio

from src.kafka.client.base import BaseKafkaProducer
from src.kafka.client.client_config import KafkaClientConfig
from src.websockets.listener import SolWebsocketClient


async def main():
    kafka_config = KafkaClientConfig(from_env=True)
    kafka_producer = BaseKafkaProducer(kafka_config, 'sol-raw-txs')
    websocket_listener = SolWebsocketClient()
    await websocket_listener.subscribe(kafka_producer.produce)


if __name__ == "__main__":
    asyncio.run(main())
