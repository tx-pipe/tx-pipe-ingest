from typing import Union

from solders.solders import Signature

from src.kafka.client.base import BaseKafkaProducer
from src.rpc.alchemy.base import BaseAlchemyRpcClient
from src.rpc.alchemy.models._to_proto import pydantic_to_proto_result
from src.websockets.base import BaseWebsocketListener
from tx_pb2 import Result  # noqa


class SolPipe:
    def __init__(
        self,
        alchemy_rpc_client: BaseAlchemyRpcClient,
        ws_listener: BaseWebsocketListener,
        kafka_producer: BaseKafkaProducer
    ):
        self.alchemy_rpc_client = alchemy_rpc_client
        self.ws_listener = ws_listener
        self.kafka_producer = kafka_producer

    async def run(self):
        await self.ws_listener.subscribe(self.process_and_publish)

    async def process_and_publish(self, signature: Union[str, Signature]):
        if isinstance(signature, Signature):
            signature = signature.__str__()

        rpc_response = await self.alchemy_rpc_client.get_tx(signature)
        tx_proto = pydantic_to_proto_result(rpc_response.result)
        self.kafka_producer.produce(tx_proto.SerializeToString())
