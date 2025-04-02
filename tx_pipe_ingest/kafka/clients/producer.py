from typing import Union
from confluent_kafka import Producer

from tx_pipe_ingest.kafka.base import AbstractKafkaClient
from tx_pipe_ingest.kafka.kafka_config import KafkaClientConfig


class KafkaClientProducer(AbstractKafkaClient):
    def __init__(self, config: KafkaClientConfig):
        self.__producer = Producer(config.to_dict())

    def produce(self, topic: str, value: Union[str, bytes], **kwargs) -> None:
        """**kwargs duplicate from confluent_kafka.Producer.produce()"""
        self.__producer.produce(topic=topic, value=value, **kwargs)

    def flush(self) -> None:
        self.__producer.flush()
