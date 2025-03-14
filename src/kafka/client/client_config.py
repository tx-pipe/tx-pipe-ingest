import os

from dotenv import load_dotenv

from src.kafka.exceptions import KafkaConfigError


class KafkaClientConfig:
    REQUIRED_KEYS = {
        "bootstrap.servers",
        "security.protocol",
        "sasl.mechanisms",
        "sasl.username",
        "sasl.password",
    }

    def __init__(self, from_env: bool = False, **config):
        """
        Initializes Kafka client configuration.

        :param from_env: If True, loads configuration from environment variables.
        :param config: Kafka configuration parameters as keyword arguments.
        :raises KafkaConfigError: If required parameters are missing.
        """
        self.config = {}

        if from_env:
            self._load_from_env()

        self.config.update(config)

        self._validate_config()

    def _load_from_env(self):
        load_dotenv()

        for key in self.REQUIRED_KEYS:
            value = os.getenv(key)
            if value:
                self.config[key] = value

    def _validate_config(self):
        missing_keys = self.REQUIRED_KEYS - self.config.keys()
        if missing_keys:
            raise KafkaConfigError(f"Missing required configuration keys: {', '.join(missing_keys)}")
