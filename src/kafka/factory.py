from abc import ABC, abstractmethod

from src.kafka.kafka_config import KafkaClientConfig


class AbstractKafkaClient(ABC):
    @abstractmethod
    def __init__(self, config: KafkaClientConfig):  # noqa
        """
        Config should be used in Producer/Consumer confluent_kafka
        in implementation classes (confluent_kafka)

        from confluent_kafka import Producer
        producer = Producer(config)
        """
        pass
