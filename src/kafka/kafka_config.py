from typing import Dict, Any

from src.kafka.exceptions import KafkaConfigError
from src.settings import KafkaSettings


class KafkaClientConfig:
    REQUIRED_KEYS = frozenset({
        "bootstrap.servers",
        "security.protocol",
        "sasl.mechanisms",
        "sasl.username",
        "sasl.password",
    })

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes Kafka client configuration.

        :param config: Kafka configuration parameters as keyword arguments.
        :raises KafkaConfigError: If required parameters are missing.
        """
        self.config = config
        self._validate_config()

    def to_dict(self) -> Dict[str, Any]:
        return self.config.copy()

    def _validate_config(self) -> None:
        missing_keys = self.REQUIRED_KEYS - self.config.keys()
        if missing_keys:
            raise KafkaConfigError(
                f"Missing required configuration keys: {', '.join(missing_keys)}"
            )

    @classmethod
    def from_settings(cls, settings: KafkaSettings) -> "KafkaClientConfig":
        """
        Creates a KafkaClientConfig instance from KafkaSettings.
        This method converts keys from underscore notation to dot notation.
        """
        raw_config = settings.model_dump()
        transformed_config = {
            key.replace('_', '.'): value for key, value in raw_config.items()
        }
        return cls(transformed_config)
