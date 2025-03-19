from typing import Union
from solders.solders import Signature

from src.kafka.clients.producer import KafkaClientProducer
from src.proto_converters.converters.sol import SOLProtoConverter
from src.rpc.clients.sol import SOLRpcClient
from src.services.base import AbstractTxPipe
from src.socket_listeners.listeners.sol import SOLSocketListener


class SolTxPipe(AbstractTxPipe):
    def __init__(
        self,
        rpc_client: SOLRpcClient,
        socket_listener: SOLSocketListener,
        kafka_producer: KafkaClientProducer,
        converter: SOLProtoConverter,
    ):
        super().__init__(rpc_client, socket_listener, kafka_producer, converter)

    async def run(self):
        await self.socket_listener.subscribe(self.process_and_publish)

    async def process_and_publish(self, signature: Union[str, Signature]):
        if isinstance(signature, Signature):
            signature = signature.__str__()

        rpc_response = await self.rpc_client.get_tx(signature)
        tx_proto = self.converter.to_proto(rpc_response.result)
        self.kafka_producer.produce(tx_proto.SerializeToString(), 'sol-raw-txs')
