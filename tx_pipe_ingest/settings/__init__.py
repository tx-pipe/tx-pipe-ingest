from pydantic_settings import BaseSettings, SettingsConfigDict

from tx_pipe_ingest.settings.btc import BTCSettings
from tx_pipe_ingest.settings.kafka import KafkaSettings
from tx_pipe_ingest.settings.sol import SOLSettings


class Settings(BaseSettings):
    btc: BTCSettings
    sol: SOLSettings
    kafka: KafkaSettings

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file='.env',
        env_nested_delimiter='__',
        extra='ignore'
    )
