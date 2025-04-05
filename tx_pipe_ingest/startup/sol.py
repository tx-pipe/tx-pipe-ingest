from tx_pipe_ingest.protobuf.converters.sol import SOLProtoConverter
from tx_pipe_ingest.rpc.models.sol_rpc_response import SOLRPCResponse
from tx_pipe_ingest.socket_listeners.listeners.sol import SOLSocketListener
from tx_pipe_ingest.kafka.clients.producer import KafkaClientProducer
from tx_pipe_ingest.kafka.kafka_config import KafkaClientConfig
from tx_pipe_ingest.rpc.clients.sol import SOLRpcClient
from tx_pipe_ingest.rpc.http_client import HttpClient
from tx_pipe_ingest.services.pipe import TxPipe
from tx_pipe_ingest.settings import Settings


async def main():
    settings = Settings()  # noqa
    sol_rpc_client = SOLRpcClient(HttpClient(), settings.sol)
    sol_socket_listener = SOLSocketListener(settings.sol)
    kafka_config = KafkaClientConfig.from_settings(settings.kafka)
    kafka_producer = KafkaClientProducer(kafka_config)
    sol_converter = SOLProtoConverter(SOLRPCResponse)
    sol_pipe = TxPipe(sol_rpc_client, sol_socket_listener, kafka_producer, sol_converter)
    await sol_pipe.run('sol_raw_tx')
