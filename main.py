import asyncio

from src.proto_converters.converters.sol import SOLProtoConverter
from src.kafka.kafka_config import KafkaClientConfig
from src.kafka.clients.producer import KafkaClientProducer
from src.rpc.clients.sol import SOLRpcClient
from src.rpc.http_client import HttpClient
from src.rpc.models.sol_rpc_response import Result
from src.settings import Settings
from src.services.concrete.sol import SolTxPipe
from src.socket_listeners.listeners.sol import SOLSocketListener


async def main():
    settings = Settings.new()

    alchemy_rpc_client = SOLRpcClient(HttpClient(), settings.sol)

    websocket_listener = SOLSocketListener(settings.sol)

    kafka_config = KafkaClientConfig.from_settings(settings.kafka)
    kafka_producer = KafkaClientProducer(kafka_config)

    sol_converter = SOLProtoConverter(Result)

    sol_pipe = SolTxPipe(alchemy_rpc_client, websocket_listener, kafka_producer, sol_converter)
    await sol_pipe.run()


if __name__ == "__main__":
    asyncio.run(main())
