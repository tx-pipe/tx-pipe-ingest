from abc import ABC

from src.kafka.kafka_config import KafkaClientConfig


class AbstractKafkaClient(ABC):
    def __init__(self, config: KafkaClientConfig):  # noqa
        """
        Config should be used in Producer/Consumer confluent_kafka C implementation classes

        from confluent_kafka import Producer
        producer = Producer(config)
        """
        pass
