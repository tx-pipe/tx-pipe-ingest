from typing import Union

from confluent_kafka import Producer

from src.kafka.client.client_config import KafkaClientConfig


class BaseKafkaProducer:
    def __init__(self, config: KafkaClientConfig, topic: str):
        self._producer = Producer(config.config)
        self.topic = topic

    def produce(self, value: Union[str, bytes], **kwargs) -> None:
        """**kwargs duplicate from confluent_kafka.Producer"""
        self._producer.produce(topic=self.topic, value=value, **kwargs)
