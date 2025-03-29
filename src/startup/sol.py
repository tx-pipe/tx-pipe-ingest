from src.protobuf.converters.sol import SOLProtoConverter
from src.socket_listeners.listeners.sol import SOLSocketListener
from src.kafka.clients.producer import KafkaClientProducer
from src.kafka.kafka_config import KafkaClientConfig
from src.rpc.models.sol_rpc_response import ConfirmedTransaction
from src.rpc.clients.sol import SOLRpcClient
from src.rpc.http_client import HttpClient
from src.services.pipe import TxPipe
from src.settings import Settings


async def main():
    settings = Settings.new()
    sol_rpc_client = SOLRpcClient(HttpClient(), settings.sol)
    sol_socket_listener = SOLSocketListener(settings.sol)
    kafka_config = KafkaClientConfig.from_settings(settings.kafka)
    kafka_producer = KafkaClientProducer(kafka_config)
    sol_converter = SOLProtoConverter(ConfirmedTransaction)
    sol_pipe = TxPipe(sol_rpc_client, sol_socket_listener, kafka_producer, sol_converter)
    await sol_pipe.run('sol-raw-tx')
