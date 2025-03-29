from src.protobuf.converters.btc import BTCProtoConverter
from src.rpc.models.btc_rpc_response import BTCRPCResponse
from src.socket_listeners.listeners.btc import BTCSocketListener
from src.kafka.clients.producer import KafkaClientProducer
from src.kafka.kafka_config import KafkaClientConfig
from src.rpc.clients.btc import BTCRpcClient
from src.rpc.http_client import HttpClient
from src.services.pipe import TxPipe
from src.settings import Settings


async def main():
    settings = Settings.new()
    btc_rpc_client = BTCRpcClient(HttpClient(), settings.btc)
    btc_socket_listener = BTCSocketListener(settings.btc)
    kafka_config = KafkaClientConfig.from_settings(settings.kafka)
    kafka_producer = KafkaClientProducer(kafka_config)
    btc_converter = BTCProtoConverter(BTCRPCResponse)
    btc_pipe = TxPipe(btc_rpc_client, btc_socket_listener, kafka_producer, btc_converter)
    await btc_pipe.run('btc_raw_tx')
