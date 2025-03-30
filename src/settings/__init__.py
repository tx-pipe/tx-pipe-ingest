from pydantic_settings import BaseSettings, SettingsConfigDict

from src.settings.btc import BTCSettings
from src.settings.kafka import KafkaSettings
from src.settings.sol import SOLSettings


class Settings(BaseSettings):
    btc: BTCSettings
    sol: SOLSettings
    kafka: KafkaSettings

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file='.env',
        env_nested_delimiter='__'
    )
