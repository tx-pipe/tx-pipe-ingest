import logging
from typing import TypeVar, Generic

from src.kafka.clients.producer import KafkaClientProducer
from src.protobuf.base import AbstractProtoConverter
from src.socket_listeners.base import AbstractSocketListener
from src.rpc.base import AbstractRpcClient

logger = logging.getLogger(__name__)


T = TypeVar("T")
TxIdentifier = TypeVar("TxIdentifier")


class TxPipe(Generic[T]):
    def __init__(
        self,
        rpc_client: AbstractRpcClient,
        socket_listener: AbstractSocketListener,
        kafka_producer: KafkaClientProducer,
        converter: AbstractProtoConverter,
    ):
        self.rpc_client = rpc_client
        self.socket_listener = socket_listener
        self.kafka_producer = kafka_producer
        self.converter = converter

    async def run(self, topic: str):
        await self.socket_listener.subscribe(self.process_and_publish, topic=topic)

    async def process_and_publish(self, tx_identifier: TxIdentifier, topic: str):
        rpc_response = await self.rpc_client.get_tx(tx_identifier)
        tx_proto = self.converter.to_proto(rpc_response)
        logger.debug(f'{topic}: {str(tx_proto)[:50]}')
        self.kafka_producer.produce(topic, tx_proto.SerializeToString())
