import os
from dotenv import load_dotenv
from pydantic import BaseModel

from src.settings.factories.btc import BTCSettings
from src.settings.factories.kafka import KafkaSettings
from src.settings.factories.sol import SOLSettings


class Settings(BaseModel):
    btc: BTCSettings
    sol: SOLSettings
    kafka: KafkaSettings

    @classmethod
    def new(cls) -> 'Settings':
        load_dotenv()
        settings_dict = dict(os.environ)

        return Settings(
            btc=BTCSettings.from_dict(settings_dict),
            kafka=KafkaSettings.from_dict(settings_dict),
            sol=SOLSettings.from_dict(settings_dict),
        )
