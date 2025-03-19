from typing import Dict
from pydantic import Field

from src.settings.factory import SettingsFactory


class SOLSettings(SettingsFactory):
    network: str = Field()
    alchemy_api_key: str = Field()
    socket_url: str = Field()

    @classmethod
    def from_dict(cls, settings_dict: Dict[str, str]) -> 'SOLSettings':
        return SOLSettings(
            network=settings_dict.get('SOL_SETTINGS_NETWORK'),
            alchemy_api_key=settings_dict.get('SOL_SETTINGS_ALCHEMY_API_KEY'),
            socket_url=settings_dict.get('SOL_SETTINGS_SOCKET_URL'),
        )
