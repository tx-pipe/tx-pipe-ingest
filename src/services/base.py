from abc import ABC, abstractmethod
from typing import TypeVar

from src.kafka.clients.producer import KafkaClientProducer
from src.proto_converters.base import AbstractProtoConverter
from src.rpc.base import AbstractRpcClient
from src.socket_listeners.base import AbstractSocketListener


TxIdentifierType = TypeVar("TxIdentifierType")


class AbstractTxPipe(ABC):
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

    @abstractmethod
    async def run(self):
        pass

    @abstractmethod
    async def process_and_publish(self, tx_identifier: TxIdentifierType):
        pass
