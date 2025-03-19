from typing import Dict
from pydantic import Field

from src.settings.factory import SettingsFactory


class KafkaSettings(SettingsFactory):
    bootstrap_servers: str = Field()
    security_protocol: str = Field()
    sasl_mechanisms: str = Field()
    sasl_username: str = Field()
    sasl_password: str = Field()
    session_timeout_ms: int = Field()
    client_id: str = Field()

    @classmethod
    def from_dict(cls, settings_dict: Dict[str, str]) -> 'KafkaSettings':
        return KafkaSettings(
            bootstrap_servers=settings_dict.get('KAFKA_SETTINGS_BOOTSTRAP_SERVERS'),
            security_protocol=settings_dict.get('KAFKA_SETTINGS_SECURITY_PROTOCOL'),
            sasl_mechanisms=settings_dict.get('KAFKA_SETTINGS_SASL_MECHANISMS'),
            sasl_username=settings_dict.get('KAFKA_SETTINGS_SASL_USERNAME'),
            sasl_password=settings_dict.get('KAFKA_SETTINGS_SASL_PASSWORD'),
            session_timeout_ms=int(settings_dict.get('KAFKA_SETTINGS_SESSION_TIMEOUT_MS')),
            client_id=settings_dict.get('KAFKA_SETTINGS_CLIENT_ID'),
        )
