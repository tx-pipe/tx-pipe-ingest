from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    # Client Settings
    bootstrap_servers: str
    security_protocol: str
    sasl_mechanisms: str
    sasl_username: str
    sasl_password: str
    session_timeout_ms: int
    client_id: str

    # Schema Registry Settings
    # sr_url: str = Field()
    # sr_api_key: str = Field()
    # sr_api_secret: str = Field()
