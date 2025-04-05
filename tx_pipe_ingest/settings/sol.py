from pydantic_settings import BaseSettings


class SOLSettings(BaseSettings):
    network: str
    alchemy_api_key: str
    socket_url: str
