from typing import Union
from confluent_kafka import Producer

from src.kafka.factory import AbstractKafkaClient
from src.kafka.kafka_config import KafkaClientConfig


class KafkaClientProducer(AbstractKafkaClient):
    def __init__(self, config: KafkaClientConfig):
        super(KafkaClientProducer, self).__init__(config)
        self.__producer = Producer(config.to_dict())

    def produce(self, topic: str, value: Union[str, bytes], **kwargs) -> None:
        """**kwargs duplicate from confluent_kafka.Producer.produce()"""
        self.__producer.produce(topic=topic, value=value, **kwargs)
