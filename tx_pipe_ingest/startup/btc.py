from tx_pipe_ingest.protobuf.converters.btc import BTCProtoConverter
from tx_pipe_ingest.rpc.models.btc_rpc_response import BTCRPCResponse
from tx_pipe_ingest.socket_listeners.listeners.btc import BTCSocketListener
from tx_pipe_ingest.kafka.clients.producer import KafkaClientProducer
from tx_pipe_ingest.kafka.kafka_config import KafkaClientConfig
from tx_pipe_ingest.rpc.clients.btc import BTCRpcClient
from tx_pipe_ingest.rpc.http_client import HttpClient
from tx_pipe_ingest.services.pipe import TxPipe
from tx_pipe_ingest.settings import Settings


async def main():
    settings = Settings()  # noqa
    btc_rpc_client = BTCRpcClient(HttpClient(), settings.btc)
    btc_socket_listener = BTCSocketListener(settings.btc)
    kafka_config = KafkaClientConfig.from_settings(settings.kafka)
    kafka_producer = KafkaClientProducer(kafka_config)
    btc_converter = BTCProtoConverter(BTCRPCResponse)
    btc_pipe = TxPipe(btc_rpc_client, btc_socket_listener, kafka_producer, btc_converter)
    await btc_pipe.run('btc_raw_tx')
